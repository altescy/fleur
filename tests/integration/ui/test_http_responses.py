from collections.abc import Callable
from pathlib import Path

from fleur import Array, Cmd, Component, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State, String, bloom
from fleur.core import PointerEvent
from fleur.ui import Button, Text, VStack


class Todo(Model):
    id: State[int]
    title: State[str]
    note: State[str | None]


class Board(Model):
    todos: State[list[Todo]]
    error: State[str]


class Actions(MsgGroup):
    LOAD: Msg[PointerEvent] = Msg()
    LOAD_BROKEN: Msg[PointerEvent] = Msg()
    LOAD_MISSING: Msg[PointerEvent] = Msg()
    LOADED: Msg[HttpResponse[list[Todo]]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def _load(url: str) -> Cmd[Board, Actions]:
    return Cmd.task(Http.get(url, expect=Http.expectJson(list[Todo])), Actions.LOADED, Actions.FAILED)


def test_typed_responses_are_validated(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        Board(todos=[], error=""),
        Actions.cases(
            Actions.LOAD.then((State.unchanged(), _load("/todos"))),
            Actions.LOAD_BROKEN.then((State.unchanged(), _load("/broken"))),
            Actions.LOAD_MISSING.then((State.unchanged(), _load("/missing"))),
            Actions.LOADED.then(State.set(Board.todos, Actions.LOADED.event.body) & State.set(Board.error, "")),
            Actions.FAILED.then(
                # Event fields are expressions, so `+` builds the message in the browser.
                State.set(Board.error, Actions.FAILED.event.kind + ": " + Actions.FAILED.event.message)
            ),
        ),
        VStack(
            Button("Load", onclick=Actions.LOAD),
            Button("Load broken", onclick=Actions.LOAD_BROKEN),
            Button("Load missing", onclick=Actions.LOAD_MISSING),
            VStack(
                Array.map(
                    Board.todos,
                    lambda todo: Text(
                        todo.title + " / " + String.or_empty(todo.note),
                        props={"key": todo.id},
                    ),
                ),
                props={"id": "todos"},
            ),
            Text(Board.error, props={"id": "error"}),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("http_responses.cjs"))
