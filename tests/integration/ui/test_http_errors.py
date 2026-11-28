from collections.abc import Callable
from pathlib import Path

from fleur import Array, Cmd, Component, Cond, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State, bloom
from fleur.core import PointerEvent
from fleur.ui import Button, Text, VStack


class Todo(Model):
    title: State[str]


class Issue(Model):
    loc: State[list[str | int]]
    msg: State[str]


class ValidationError(Model):
    detail: State[list[Issue]]


class Editor(Model):
    issues: State[list[Issue]]
    status: State[str]
    raw: State[str]


class Actions(MsgGroup):
    SAVE: Msg[PointerEvent] = Msg()
    SAVE_MISSING: Msg[PointerEvent] = Msg()
    SAVE_UNTYPED: Msg[PointerEvent] = Msg()
    SAVED: Msg[HttpResponse[Todo]] = Msg()
    REJECTED: Msg[HttpError[ValidationError]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def _save(url: str) -> Cmd[Editor, Actions]:
    request = Http.post(url, body={"title": ""}, expect=Http.expectJson(Todo, error=ValidationError))
    return Cmd.task(request, Actions.SAVED, Actions.REJECTED)


def test_error_bodies_reach_the_app(playwright_page: Callable[[str, Path], str]) -> None:
    untyped = Http.post("/untyped", expect=Http.expectJson(Todo))
    app = Component(
        init=Editor(issues=[], status="", raw=""),
        update=lambda _: Actions.cases(
            Actions.SAVE.then((State.unchanged(), _save("/todos"))),
            Actions.SAVE_MISSING.then((State.unchanged(), _save("/missing"))),
            Actions.SAVE_UNTYPED.then((State.unchanged(), Cmd.task(untyped, Actions.SAVED, Actions.FAILED))),
            Actions.SAVED.then(State.set(Editor.status, "saved")),
            Actions.REJECTED.then(
                lambda rejected: (
                    State.set(Editor.issues, Cond.maybe(rejected.body, then=lambda error: error.detail, otherwise=[]))
                    & State.set(Editor.status, Cond.maybe(rejected.body, then=lambda _: "invalid", otherwise="no body"))
                )
            ),
            Actions.FAILED.then(
                lambda event: State.set(Editor.raw, Cond.when(Cond.equal(event.body, None), "none", "json"))
            ),
        ),
        view=lambda model: VStack(
            Button("Save", onclick=Actions.SAVE),
            Button("Save missing", onclick=Actions.SAVE_MISSING),
            Button("Save untyped", onclick=Actions.SAVE_UNTYPED),
            VStack(Array.map(model.issues, lambda issue: Text(issue.msg)), props={"id": "issues"}),
            Text(model.status, props={"id": "status"}),
            Text(model.raw, props={"id": "raw"}),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("http_errors.cjs"))
