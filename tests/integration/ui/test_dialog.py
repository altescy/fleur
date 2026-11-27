from collections.abc import Callable
from pathlib import Path

import pytest

from fleur import Component, Cond, Model, Msg, MsgGroup, State, View, bloom
from fleur.core import DialogCloseEvent, PointerEvent
from fleur.core.view import ViewProp
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
                labelledby="profile-title",
                display="grid",
            ),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("dialog.cjs"))


class Replacement(Model):
    swapped: State[bool]


class ReplacementActions(MsgGroup):
    SWAP: Msg[PointerEvent] = Msg()
    CLOSE: Msg[DialogCloseEvent] = Msg()


@pytest.mark.parametrize(
    ("replacement_props", "expected_open"),
    [({}, False), ({"open": None}, False), ({"open": True}, True)],
    ids=["open-omitted", "open-none", "nonmodal-open"],
)
def test_reusing_a_dialog_element_releases_its_modal_state(
    overlay_focus_page: Callable[[str, Path], str], replacement_props: dict[str, ViewProp], expected_open: bool
) -> None:
    app = Component(
        Replacement(swapped=False),
        ReplacementActions.cases(
            ReplacementActions.SWAP.then(State.set(Replacement.swapped, True)),
            ReplacementActions.CLOSE.then(State.unchanged()),
        ),
        VStack(
            Button("Outside"),
            Cond.when(
                Replacement.swapped,
                View("Replacement", tag="dialog", props={**replacement_props, "id": "panel"}),
                Dialog(
                    Button("Swap", onclick=ReplacementActions.SWAP),
                    open=True,
                    onclose=ReplacementActions.CLOSE,
                    label="Replacement",
                    props={"id": "panel"},
                ),
            ),
            props={"data-expected-open": "true" if expected_open else "false"},
        ),
    )
    overlay_focus_page(bloom(app), Path(__file__).with_name("dialog_reuse.cjs"))
