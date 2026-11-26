"""Compose two editors with independent state and message forwarding."""

from fleur import Component, Cond, Model, Msg, MsgGroup, State, String, Update, View
from fleur.core import InputEvent, PointerEvent
from fleur.ui import Button, Input, Text, VStack


class EditorModel(Model):
    name: State[str]


class EditorMsg(MsgGroup):
    CHANGE: Msg[InputEvent] = Msg()
    CLEAR: Msg[PointerEvent] = Msg()


def editor() -> Component[EditorModel, EditorMsg]:
    is_blank = Cond.equal(String.trim(EditorModel.name), "")
    return Component(
        EditorModel(name=""),
        EditorMsg.cases(
            EditorMsg.CHANGE.then(State.set(EditorModel.name, EditorMsg.CHANGE.event.value)),
            EditorMsg.CLEAR.then(State.set(EditorModel.name, "")),
        ),
        VStack(
            Input(
                value=EditorModel.name,
                oninput=EditorMsg.CHANGE,
                props={"aria-label": "Display name"},
            ),
            Text(Cond.when(is_blank, "Enter a display name.", "Preview: " + EditorModel.name)),
            Button("Clear", onclick=EditorMsg.CLEAR, props={"disabled": is_blank}),
            gap="sm",
        ),
    )


class WorkspaceModel(Model):
    first: State[EditorModel]
    second: State[EditorModel]


class WorkspaceMsg(MsgGroup):
    FIRST = Msg()
    SECOND = Msg()


def app() -> Component[WorkspaceModel, WorkspaceMsg]:
    first = editor()
    second = editor()
    return Component(
        WorkspaceModel(first=first.init.model, second=second.init.model),
        WorkspaceMsg.cases(
            WorkspaceMsg.FIRST.then(Update.forward(WorkspaceModel.first, first, WorkspaceMsg.FIRST)),
            WorkspaceMsg.SECOND.then(Update.forward(WorkspaceModel.second, second, WorkspaceMsg.SECOND)),
        ),
        VStack(
            Text("First editor"),
            View.forward(WorkspaceModel.first, first.view, WorkspaceMsg.FIRST),
            Text("Second editor"),
            View.forward(WorkspaceModel.second, second.view, WorkspaceMsg.SECOND),
            gap="md",
        ),
    )
