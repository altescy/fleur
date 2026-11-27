from collections.abc import Callable, Sequence
from pathlib import Path

from fleur import Array, Component, Cond, Model, Msg, MsgGroup, State, bloom
from fleur.core import InputEvent, PointerEvent
from fleur.ui import Button, Card, Heading, Option, Select, Text, Theme, field


class Screen(Model):
    selected: State[str]
    choices: State[Sequence[str]]


class Actions(MsgGroup):
    CHANGE: Msg[InputEvent] = Msg()
    REMOVE: Msg[PointerEvent] = Msg()
    RESTORE: Msg[PointerEvent] = Msg()


def test_select_and_field_in_browser(playwright_page: Callable[[str, Path], str]) -> None:
    choices = Array.map(Screen.choices, lambda key: Option("Label " + key, value=key, props={"key": key}))
    app = Component(
        Screen(selected="b", choices=["a", "b"]),
        Actions.cases(
            Actions.CHANGE.then(State.set(Screen.selected, Actions.CHANGE.event.value)),
            Actions.REMOVE.then(State.set(Screen.choices, ["a", "c"])),
            Actions.RESTORE.then(State.set(Screen.choices, ["c", "a", "b"])),
        ),
        Card(
            Heading("Preferences", level=2),
            field(
                id="choice",
                label="Choice",
                description="Select one item.",
                error=Cond.when(Array.includes(Screen.choices, Screen.selected), None, "Choice unavailable."),
                control=lambda attrs: Select(choices, value=Screen.selected, onchange=Actions.CHANGE, props=attrs),
            ),
            Select(choices, props={"aria-label": "Uncontrolled"}),
            Button("Remove", onclick=Actions.REMOVE),
            Button("Restore", onclick=Actions.RESTORE),
            Text(Screen.selected, props={"id": "model-value"}),
        ),
    )
    theme = Theme(colors={"card": "#edf0ff"}, components={"input": {"radius": 9}})
    playwright_page(bloom(app, theme=theme), Path(__file__).with_name("select.cjs"))
