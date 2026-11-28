from collections.abc import Callable, Sequence
from pathlib import Path

from fleur import Array, Component, Cond, Model, Msg, MsgGroup, State, View, bloom
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
    def view(model: Screen) -> View[Screen, Actions]:
        choices = Array.map(model.choices, lambda key: Option("Label " + key, value=key, props={"key": key}))
        return Card(
            Heading("Preferences", level=2),
            field(
                id="choice",
                label="Choice",
                description="Select one item.",
                error=Cond.when(Array.includes(model.choices, model.selected), None, "Choice unavailable."),
                control=lambda attrs: Select(choices, value=model.selected, onchange=Actions.CHANGE, props=attrs),
            ),
            Select(choices, props={"aria-label": "Uncontrolled"}),
            Button("Remove", onclick=Actions.REMOVE),
            Button("Restore", onclick=Actions.RESTORE),
            Text(model.selected, props={"id": "model-value"}),
        )

    app = Component(
        init=Screen(selected="b", choices=["a", "b"]),
        update=lambda _: Actions.cases(
            Actions.CHANGE.then(lambda event: State.set(Screen.selected, event.value)),
            Actions.REMOVE.then(State.set(Screen.choices, ["a", "c"])),
            Actions.RESTORE.then(State.set(Screen.choices, ["c", "a", "b"])),
        ),
        view=view,
    )
    theme = Theme(colors={"card": "#edf0ff"}, components={"input": {"radius": 9}})
    playwright_page(bloom(app, theme=theme), Path(__file__).with_name("select.cjs"))
