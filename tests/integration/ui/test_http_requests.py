from collections.abc import Callable
from pathlib import Path

from fleur import Cmd, Component, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State, String, Url, bloom
from fleur.core import InputEvent, PointerEvent
from fleur.types import JsonValue
from fleur.ui import Button, Input, Text, VStack


class Editor(Model):
    todo_id: State[int]
    title: State[str]
    token: State[str]
    result: State[str]


class Actions(MsgGroup):
    TITLE: Msg[InputEvent] = Msg()
    SAVE: Msg[PointerEvent] = Msg()
    SAVED: Msg[HttpResponse[JsonValue]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def _save(model: Editor) -> Cmd[Editor, Actions]:
    request = Http.put(
        Url.path("/todos/{id}", id=model.todo_id),
        expect=Http.expectJson(),
        query={"notify": True, "source": model.title},
        headers={"Authorization": "Bearer " + model.token},
        body={"title": model.title, "tags": ["work", model.title], "done": False},
    )
    return Cmd.task(request, Actions.SAVED, Actions.FAILED)


def test_request_sends_values_read_from_the_model(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        init=Editor(todo_id=42, title="", token="secret", result=""),
        update=lambda model: Actions.cases(
            Actions.TITLE.then(lambda event: State.set(Editor.title, event.value)),
            Actions.SAVE.then((State.unchanged(), _save(model))),
            Actions.SAVED.then(lambda event: State.set(Editor.result, "saved " + String.from_number(event.status))),
            Actions.FAILED.then(lambda event: State.set(Editor.result, event.message)),
        ),
        view=lambda model: VStack(
            Input(value=model.title, oninput=Actions.TITLE, props={"aria-label": "Title"}),
            Button("Save", onclick=Actions.SAVE),
            Text(model.result, props={"id": "result"}),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("http_requests.cjs"))
