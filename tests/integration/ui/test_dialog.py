from collections.abc import Callable
from pathlib import Path

from fleur import Component, Cond, Model, Msg, MsgGroup, State, bloom
from fleur.core import DialogCloseEvent, PointerEvent
from fleur.ui import Button, Dialog, Form, Heading, Input, Text, VStack


class Screen(Model):
    editing: State[bool]


class Actions(MsgGroup):
    EDIT: Msg[PointerEvent] = Msg()
    DONE: Msg[PointerEvent] = Msg()
    CLOSED: Msg[DialogCloseEvent] = Msg()


def test_modal_state_and_keyboard_focus(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        Screen(editing=True),
        Actions.cases(
            Actions.EDIT.then(State.set(Screen.editing, True)),
            Actions.DONE.then(State.set(Screen.editing, False)),
            Actions.CLOSED.then(State.set(Screen.editing, False)),
        ),
        VStack(
            Button("Edit profile", onclick=Actions.EDIT),
            Button("Edit again", onclick=Actions.EDIT),
            Text(Cond.when(Screen.editing, "Open", "Closed"), props={"id": "model-state"}),
            Dialog(
                Heading("Profile", level=2, props={"id": "profile-title"}),
                Button("Done", onclick=Actions.DONE),
                Input(props={"aria-label": "Name", "autofocus": True}),
                Form(Button("Cancel", props={"type": "submit"}), props={"method": "dialog"}),
                open=Screen.editing,
                onclose=Actions.CLOSED,
                props={"aria-labelledby": "profile-title"},
                display="grid",
            ),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("dialog.cjs"))
