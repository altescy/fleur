from collections.abc import Callable
from pathlib import Path

from fleur import Component, Cond, Model, Msg, MsgGroup, State, bloom
from fleur.core import PointerEvent, ToggleEvent
from fleur.ui import Button, Input, Popover, Text, VStack


class Screen(Model):
    editing: State[bool]


class Actions(MsgGroup):
    OPEN: Msg[PointerEvent] = Msg()
    TOGGLE: Msg[ToggleEvent] = Msg()


def test_popover_model_anchor_and_dismissal(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        init=Screen(editing=True),
        update=lambda _: Actions.cases(
            Actions.OPEN.then(State.set(Screen.editing, True)),
            Actions.TOGGLE.then(lambda event: State.set(Screen.editing, event.open)),
        ),
        view=lambda model: VStack(
            Popover(
                Input(props={"autofocus": True, "aria-label": "Title"}),
                id="editor",
                trigger=lambda attrs: Button("Edit", props=attrs),
                open=model.editing,
                ontoggle=Actions.TOGGLE,
                display="grid",
            ),
            Popover(Text("Second panel"), id="help", trigger=lambda attrs: Button("Help", props=attrs)),
            Button("Open from model", onclick=Actions.OPEN),
            Input(props={"aria-label": "Outside"}),
            Text(Cond.when(model.editing, "Editing", "Closed"), props={"role": "status"}),
            align="end",
            p="lg",
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("popover.cjs"))
