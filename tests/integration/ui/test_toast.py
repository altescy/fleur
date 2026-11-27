from collections.abc import Callable
from pathlib import Path

from fleur import Component, Model, Msg, MsgGroup, State, String, bloom
from fleur.core import PointerEvent, ToastCloseEvent
from fleur.ui import Button, Text, Toast, VStack


class ToastSettings(Model):
    opened: State[bool]
    duration: State[int | None]
    closed: State[int]
    reason: State[str]


class ToastActions(MsgGroup):
    SHOW: Msg[PointerEvent] = Msg()
    SET_DURATION: Msg[PointerEvent, int | None] = Msg()
    CLOSED: Msg[ToastCloseEvent] = Msg()


def test_toast_updates_duration_on_the_existing_element(overlay_focus_page: Callable[[str, Path], str]) -> None:
    app = Component(
        ToastSettings(opened=False, duration=None, closed=0, reason=""),
        ToastActions.cases(
            ToastActions.SHOW.then(State.set(ToastSettings.opened, True)),
            ToastActions.SET_DURATION.then(State.set(ToastSettings.duration, ToastActions.SET_DURATION.context)),
            ToastActions.CLOSED.then(
                State.set(ToastSettings.opened, False),
                State.set(ToastSettings.closed, ToastSettings.closed + 1),
                State.set(ToastSettings.reason, ToastActions.CLOSED.event.reason),
            ),
        ),
        VStack(
            Button("Show", onclick=ToastActions.SHOW),
            Button("No timeout", onclick=ToastActions.SET_DURATION.bind(None)),
            Button("1.2 seconds", onclick=ToastActions.SET_DURATION.bind(1200)),
            Button("Zero milliseconds", onclick=ToastActions.SET_DURATION.bind(0)),
            Toast(
                "Saved",
                open=ToastSettings.opened,
                duration_ms=ToastSettings.duration,
                onclose=ToastActions.CLOSED,
                props={"id": "toast"},
            ),
            Text(String.from_number(ToastSettings.closed), props={"id": "closed"}),
            Text(ToastSettings.reason, props={"id": "reason"}),
        ),
    )
    overlay_focus_page(bloom(app), Path(__file__).with_name("toast_inputs.cjs"))
