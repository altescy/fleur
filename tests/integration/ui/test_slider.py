from collections.abc import Callable
from pathlib import Path

from fleur import Component, Model, Msg, MsgGroup, State, bloom
from fleur.core import PointerEvent
from fleur.ui import Button, Slider, VStack


class Screen(Model):
    low: State[int]
    high: State[int]
    step: State[int]
    value: State[int]


class Actions(MsgGroup):
    LIMIT: Msg[PointerEvent] = Msg()
    RESTORE: Msg[PointerEvent] = Msg()
    SHIFT: Msg[PointerEvent] = Msg()
    COARSE: Msg[PointerEvent] = Msg()
    FINE: Msg[PointerEvent] = Msg()


def test_slider_applies_controlled_value_after_range_changes(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        init=Screen(low=120, high=140, step=2, value=132),
        update=lambda _: Actions.cases(
            Actions.LIMIT.then(State.set(Screen.low, 136)),
            Actions.RESTORE.then(State.set(Screen.low, 120)),
            Actions.SHIFT.then(State.set(Screen.low, 200) & State.set(Screen.high, 240) & State.set(Screen.value, 228)),
            Actions.COARSE.then(State.set(Screen.step, 5)),
            Actions.FINE.then(State.set(Screen.step, 2)),
        ),
        view=lambda model: VStack(
            Slider(
                label="Level",
                value=model.value,
                min=model.low,
                max=model.high,
                step=model.step,
                props={"value": 0},
            ),
            Button("Limit", onclick=Actions.LIMIT),
            Button("Restore", onclick=Actions.RESTORE),
            Button("Shift", onclick=Actions.SHIFT),
            Button("Coarse", onclick=Actions.COARSE),
            Button("Fine", onclick=Actions.FINE),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("slider.cjs"))
