# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check that a component's initial model, update and view agree on one model type."""

from fleur import Component, Model, Msg, MsgGroup, State, View
from fleur.core import PointerEvent
from fleur.ui import Button, Text


class Counter(Model):
    count: State[int]


class Profile(Model):
    name: State[str]


class Actions(MsgGroup):
    INC: Msg[PointerEvent] = Msg()


counter_update = Actions.cases(Actions.INC.then(State.set(Counter.count, Counter.count + 1)))
profile_update = Actions.cases(Actions.INC.then(State.set(Profile.name, "x")))


def counter_view() -> View[Counter, Actions]:
    return Button("+", onclick=Actions.INC)


def examples() -> None:
    Component(Counter(count=0), counter_update, counter_view())
    Component(Counter(count=0), counter_update, Text("leaf views fit any model"))
    Component(Profile(name=""), counter_update, Text("x"))  # pyright: ignore[reportArgumentType]
    Component(Profile(name=""), profile_update, counter_view())  # pyright: ignore[reportArgumentType]
