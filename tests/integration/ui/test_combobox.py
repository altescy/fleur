from collections.abc import Callable, Mapping
from pathlib import Path

from fleur import Component, Model, Msg, MsgGroup, State, bloom
from fleur.core import PointerEvent
from fleur.ui import Button, Combobox, VStack


class Screen(Model):
    options: State[Mapping[str, str]]
    selected: State[str | None]


class Actions(MsgGroup):
    SELECT: Msg[PointerEvent, str] = Msg()
    REORDER: Msg[PointerEvent] = Msg()
    REMOVE: Msg[PointerEvent] = Msg()
    CLEAR: Msg[PointerEvent] = Msg()


def test_combobox_keeps_focus_when_model_options_change(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        Screen(options={"jane": "Jane Eyre", "emma": "Emma", "persuasion": "Persuasion"}, selected="emma"),
        Actions.cases(
            Actions.SELECT.then(State.set(Screen.selected, Actions.SELECT.context)),
            Actions.REORDER.then(
                State.set(Screen.options, {"persuasion": "Persuasion", "emma": "Emma (1815)", "jane": "Jane Eyre"})
            ),
            Actions.REMOVE.then(State.set(Screen.options, {"persuasion": "Persuasion", "emma": "Emma (1815)"})),
            Actions.CLEAR.then(State.set(Screen.selected, None)),
        ),
        VStack(
            Combobox(
                Screen.options,
                id="book",
                label="Book",
                value=Screen.selected,
                onselect=Actions.SELECT,
            ),
            Button("Reorder", onclick=Actions.REORDER),
            Button("Remove Jane Eyre", onclick=Actions.REMOVE),
            Button("Clear selection", onclick=Actions.CLEAR),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("combobox.cjs"))
