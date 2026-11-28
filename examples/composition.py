"""Compose two editors with independent state and message forwarding."""

from fleur import Component, Cond, Model, Msg, MsgGroup, State, String, Update, View
from fleur.core import InputEvent, PointerEvent
from fleur.ui import Button, Input, Text, VStack


class EditorModel(Model):
    name: State[str]


class EditorMsg(MsgGroup):
    CHANGE: Msg[InputEvent] = Msg()
    CLEAR: Msg[PointerEvent] = Msg()


def _editor_view(model: EditorModel) -> View[EditorModel, EditorMsg]:
    is_blank = Cond.equal(String.trim(model.name), "")
    return VStack(
        Input(
            value=model.name,
            oninput=EditorMsg.CHANGE,
            props={"aria-label": "Display name"},
        ),
        Text(Cond.when(is_blank, "Enter a display name.", "Preview: " + model.name)),
        Button("Clear", onclick=EditorMsg.CLEAR, props={"disabled": is_blank}),
        gap="sm",
    )


def editor() -> Component[EditorModel, EditorMsg]:
    return Component(
        EditorModel(name=""),
        update=lambda _: EditorMsg.cases(
            EditorMsg.CHANGE.then(lambda event: State.set(EditorModel.name, event.value)),
            EditorMsg.CLEAR.then(State.set(EditorModel.name, "")),
        ),
        view=_editor_view,
    )


class WorkspaceModel(Model):
    first: State[EditorModel]
    second: State[EditorModel]


class WorkspaceMsg(MsgGroup):
    FIRST: Msg[EditorMsg] = Msg()
    SECOND: Msg[EditorMsg] = Msg()


def app() -> Component[WorkspaceModel, WorkspaceMsg]:
    first = editor()
    second = editor()
    return Component(
        WorkspaceModel(first=first.init.model, second=second.init.model),
        update=lambda _: WorkspaceMsg.cases(
            WorkspaceMsg.FIRST.then(Update.forward(WorkspaceModel.first, first, WorkspaceMsg.FIRST)),
            WorkspaceMsg.SECOND.then(Update.forward(WorkspaceModel.second, second, WorkspaceMsg.SECOND)),
        ),
        view=lambda _: VStack(
            Text("First editor"),
            View.forward(WorkspaceModel.first, first, WorkspaceMsg.FIRST),
            Text("Second editor"),
            View.forward(WorkspaceModel.second, second, WorkspaceMsg.SECOND),
            gap="md",
        ),
    )
