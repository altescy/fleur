from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from fleur import Array, Component, Model, Msg, MsgGroup, State, bloom
from fleur.core import PointerEvent
from fleur.ui import Button, Text, ToggleGroup, Toolbar, VStack


class Screen(Model):
    options: State[Mapping[str, str]]
    selection: State[Sequence[str]]


class Actions(MsgGroup):
    CHANGE: Msg[PointerEvent, Sequence[str]] = Msg()
    REFRESH: Msg[PointerEvent] = Msg()


def test_toggle_group_shares_toolbar_navigation_and_dispatches_selection(
    playwright_page: Callable[[str, Path], str],
) -> None:
    app = Component(
        init=Screen(options={"a": "A", "b": "B"}, selection=["a"]),
        update=lambda _: Actions.cases(
            Actions.CHANGE.then(lambda _, context: State.set(Screen.selection, context)),
            Actions.REFRESH.then(State.set(Screen.options, {"b": "B", "a": "A", "c": "C"})),
        ),
        view=lambda model: VStack(
            Button("Before"),
            Toolbar(
                ToggleGroup(model.options, label="Options", value=model.selection, onchange=Actions.CHANGE),
                Button("Refresh", onclick=Actions.REFRESH),
                label="Tools",
            ),
            Button("After"),
            Text(Array.join(model.selection), props={"role": "status"}),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("toggle_group.cjs"))
