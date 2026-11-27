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


def test_request_sends_values_read_from_the_model(playwright_page: Callable[[str, Path], str]) -> None:
    save = Http.put(
        Url.path("/todos/{id}", id=Editor.todo_id),
        expect=Http.expectJson(),
        query={"notify": True, "source": Editor.title},
        headers={"Authorization": "Bearer " + Editor.token},
        body={"title": Editor.title, "tags": ["work", Editor.title], "done": False},
    )
    app = Component(
        Editor(todo_id=42, title="", token="secret", result=""),
        Actions.cases(
            Actions.TITLE.then(State.set(Editor.title, Actions.TITLE.event.value)),
            Actions.SAVE.then((State.unchanged(), Cmd.task(save, Actions.SAVED, Actions.FAILED))),
            Actions.SAVED.then(State.set(Editor.result, "saved " + String.from_number(Actions.SAVED.event.status))),
            Actions.FAILED.then(State.set(Editor.result, Actions.FAILED.event.message)),
        ),
        VStack(
            Input(value=Editor.title, oninput=Actions.TITLE, props={"aria-label": "Title"}),
            Button("Save", onclick=Actions.SAVE),
            Text(Editor.result, props={"id": "result"}),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("http_requests.cjs"))
