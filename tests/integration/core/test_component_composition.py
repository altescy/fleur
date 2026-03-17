from fleur import Component, Model, Msg, MsgGroup, State, Update, View, compile_component, emit
from fleur.ui import Button, Text, VStack


class CounterModel(Model):
    count: State[int]


class CounterMsg(MsgGroup):
    INC = Msg()
    DEC = Msg()


def counter():
    return Component(
        CounterModel(count=0),
        CounterMsg.caseof(
            CounterMsg.INC(CounterModel.count.set(CounterModel.count + 1)),
            CounterMsg.DEC(CounterModel.count.set(CounterModel.count - 1)),
        ),
        VStack(
            Text(f"Count: {CounterModel.count}"),
            Button("+", onclick=CounterMsg.INC),
            Button("-", onclick=CounterMsg.DEC),
        ),
    )


class AppModel(Model):
    counter: State[CounterModel]


class AppMsg(MsgGroup):
    COUNTER = Msg()


def app():
    nested_counter = counter()
    return Component(
        AppModel(counter=nested_counter.init.model),
        AppMsg.caseof(
            AppMsg.COUNTER(Update.forward(AppModel.counter, nested_counter, AppMsg.COUNTER)),
        ),
        VStack(
            Text("Nested"),
            View.forward(AppModel.counter, nested_counter.view, AppMsg.COUNTER),
        ),
    )


def test_nested_component_compiles_with_message_mapping() -> None:
    source = emit(compile_component(app))

    assert "__fleur.Html.map" in source
    assert "__fleur.Cmd.map" in source
    assert "message.event" in source
    assert 'type: "COUNTER"' in source
