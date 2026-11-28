"""Update a counter from two button messages."""

from fleur import Component, Model, Msg, MsgGroup, State
from fleur.core import PointerEvent
from fleur.ui import Button, Text, VStack


class CounterModel(Model):
    count: State[int]


class CounterMsg(MsgGroup):
    INC = Msg[PointerEvent]()
    DEC = Msg[PointerEvent]()


def app() -> Component[CounterModel, CounterMsg]:
    return Component(
        init=CounterModel(count=0),
        update=lambda model: CounterMsg.cases(
            CounterMsg.INC.then(State.set(CounterModel.count, model.count + 1)),
            CounterMsg.DEC.then(State.set(CounterModel.count, model.count - 1)),
        ),
        view=lambda model: VStack(
            Text("Count: " + model.count),
            Button("+", onclick=CounterMsg.INC),
            Button("-", onclick=CounterMsg.DEC),
            gap="sm",
        ),
    )
