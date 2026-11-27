# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check that batched commands and subscriptions share the component's message group."""

from fleur import Cmd, Component, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State, Sub
from fleur.core import Dom, DomFocusError
from fleur.ui import Text


class Clock(Model):
    ticks: State[int]


class Actions(MsgGroup):
    TICK: Msg[None] = Msg()
    LOADED: Msg[HttpResponse[str]] = Msg()
    FAILED: Msg[HttpError] = Msg()
    FOCUSED: Msg[None] = Msg()
    NOT_FOCUSED: Msg[DomFocusError] = Msg()


class Other(MsgGroup):
    TICK: Msg[None] = Msg()
    FOCUSED: Msg[None] = Msg()
    NOT_FOCUSED: Msg[DomFocusError] = Msg()


load = Cmd.task(Http.get("/status.txt", expect=Http.expectText()), Actions.LOADED, Actions.FAILED)
focus = Cmd.task(Dom.focus("editor"), Actions.FOCUSED, Actions.NOT_FOCUSED)
stray_focus = Cmd.task(Dom.focus("editor"), Other.FOCUSED, Other.NOT_FOCUSED)
update = Actions.cases(
    Actions.TICK.then((State.set(Clock.ticks, Clock.ticks + 1), Cmd.batch(load, focus, Cmd.none()))),
    Actions.LOADED.then(State.unchanged()),
    Actions.FAILED.then(State.unchanged()),
    Actions.FOCUSED.then(State.unchanged()),
    Actions.NOT_FOCUSED.then(State.unchanged()),
)


def valid_examples() -> None:
    subscriptions = Sub.batch(
        Sub.interval("fast", 100, Actions.TICK), Sub.none(), Sub.interval("slow", 1000, Actions.TICK)
    )
    Component(Clock(ticks=0), update, Text("x"), subscriptions)


def invalid_examples() -> None:
    Cmd.batch(load, stray_focus)  # pyright: ignore[reportArgumentType]
    Sub.batch(Sub.interval("a", 100, Actions.TICK), Sub.interval("b", 100, Other.TICK))  # pyright: ignore[reportArgumentType]
    stray = Sub.batch(Sub.interval("a", 100, Other.TICK))
    Component(Clock(ticks=0), update, Text("x"), stray)  # pyright: ignore[reportArgumentType]
