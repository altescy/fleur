from collections.abc import Callable
from pathlib import Path

from fleur import Component, Cond, Model, Msg, MsgGroup, State, bloom
from fleur.core import DialogCloseEvent, PointerEvent, ToggleEvent
from fleur.ui import Button, Dialog, Input, Popover, Text, VStack


class Screen(Model):
    dialog_open: State[bool]
    popover_open: State[bool]


class Actions(MsgGroup):
    OPEN_DIALOG: Msg[PointerEvent] = Msg()
    CLOSE_DIALOG: Msg[DialogCloseEvent] = Msg()
    OPEN_POPOVER: Msg[PointerEvent] = Msg()
    TOGGLE_POPOVER: Msg[ToggleEvent] = Msg()


def test_escape_returns_focus_to_the_overlay_opener(overlay_focus_page: Callable[[str, Path], str]) -> None:
    app = Component(
        Screen(dialog_open=False, popover_open=False),
        Actions.cases(
            Actions.OPEN_DIALOG.then(State.set(Screen.dialog_open, True)),
            Actions.CLOSE_DIALOG.then(State.set(Screen.dialog_open, False)),
            Actions.OPEN_POPOVER.then(State.set(Screen.popover_open, True)),
            Actions.TOGGLE_POPOVER.then(State.set(Screen.popover_open, Actions.TOGGLE_POPOVER.event.open)),
        ),
        VStack(
            Input(props={"aria-label": "Outside"}),
            Button("Open dialog", onclick=Actions.OPEN_DIALOG),
            Button("Open dialog again", onclick=Actions.OPEN_DIALOG),
            Dialog(
                Input(props={"autofocus": True, "aria-label": "Name"}),
                open=Screen.dialog_open,
                onclose=Actions.CLOSE_DIALOG,
                props={"aria-label": "Profile"},
            ),
            Popover(
                Input(props={"autofocus": True, "aria-label": "Title"}),
                id="editor",
                trigger=lambda attrs: Button(Text("Edit"), props=attrs),
                open=Screen.popover_open,
                ontoggle=Actions.TOGGLE_POPOVER,
            ),
            Button("Open editor from model", onclick=Actions.OPEN_POPOVER),
            Text(Cond.when(Screen.dialog_open, "Open", "Closed"), props={"id": "dialog-state"}),
            Text(Cond.when(Screen.popover_open, "Open", "Closed"), props={"id": "popover-state"}),
        ),
    )
    overlay_focus_page(bloom(app), Path(__file__).with_name("overlay_focus.cjs"))
