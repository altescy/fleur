# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check that a component's view, commands and subscriptions only produce messages its update handles."""

from fleur import Array, Cmd, Component, Cond, Model, ModelUpdate, Msg, MsgGroup, State, Sub, Update
from fleur.core import (
    DialogCloseEvent,
    DomEvents,
    EventBinding,
    InputEvent,
    PointerEvent,
    SubmitEvent,
    ToastCloseEvent,
    ToggleEvent,
)
from fleur.ui import Box, Button, Combobox, Dialog, Form, Input, Popover, Text, Toast, VStack, field, tabs


class Counter(Model):
    count: State[int]
    items: State[list[str]]


class Actions(MsgGroup):
    INC: Msg[PointerEvent] = Msg()
    PICK: Msg[PointerEvent, int] = Msg()
    TYPE: Msg[InputEvent] = Msg()
    TICK: Msg[None] = Msg()


class Other(MsgGroup):
    BOOM: Msg[PointerEvent] = Msg()
    TICK: Msg[None] = Msg()


def update(model: Counter) -> Update[Counter, Actions]:
    return Actions.cases(
        Actions.INC.then(State.set(Counter.count, model.count + 1)),
        Actions.PICK.then(lambda event, context: State.set(Counter.count, context)),
    )


def valid_examples() -> None:
    Component(
        Counter(count=0, items=[]),
        update,
        lambda model: VStack(
            Button("+", onclick=Actions.INC),
            Button("Pick", onclick=Actions.PICK.bind(1)),
            Input(oninput=Actions.TYPE),
            Box(Text("nested"), Button("deep", onclick=Actions.INC)),
            Array.map(model.items, lambda item: Button(item, onclick=Actions.INC)),
            Cond.when(model.count > 0, Button("reset", onclick=Actions.INC), None),
            Box(props={"onclick": Actions.INC}),
            Box(props=EventBinding.on(DomEvents.click, Actions.INC)),
            "text",
        ),
        lambda model: Sub.interval("tick", 1000, Actions.TICK),
    )


def invalid_examples() -> None:
    # A view message from another group.
    Component(Counter(count=0, items=[]), update, lambda model: VStack(Button("x", onclick=Other.BOOM)))  # pyright: ignore[reportArgumentType]
    # The same, nested inside layout views.
    Component(Counter(count=0, items=[]), update, lambda model: VStack(Box(Box(Button("x", onclick=Other.BOOM)))))  # pyright: ignore[reportArgumentType]
    # Inside a mapped list.
    Component(
        Counter(count=0, items=[]),
        update,  # pyright: ignore[reportArgumentType]
        lambda model: VStack(Array.map(model.items, lambda item: Button(item, onclick=Other.BOOM))),
    )
    # Through raw props.
    Component(Counter(count=0, items=[]), update, lambda model: Box(props={"onclick": Other.BOOM}))  # pyright: ignore[reportArgumentType]
    # A message with a context that was never bound.
    Button("x", onclick=Actions.PICK)  # pyright: ignore[reportArgumentType]
    Box(props={"onclick": Actions.PICK})  # pyright: ignore[reportArgumentType]
    # A subscription or command producing another group's message.
    Component(
        Counter(count=0, items=[]),
        update,
        lambda model: Text("x"),
        lambda model: Sub.interval("tick", 1000, Other.TICK),  # pyright: ignore[reportArgumentType]
    )
    Actions.cases(Actions.INC.then((State.set(Counter.count, 0), Cmd.map(Other.BOOM, Cmd.none()))))  # pyright: ignore[reportCallIssue,reportArgumentType]


class Panel(Model):
    open: State[bool]
    tab: State[str]


class PanelActions(MsgGroup):
    OPEN: Msg[PointerEvent] = Msg()


class Stray(MsgGroup):
    PICK: Msg[PointerEvent, str] = Msg()
    CLOSE: Msg[DialogCloseEvent] = Msg()
    TOAST_CLOSE: Msg[ToastCloseEvent] = Msg()
    SUBMIT: Msg[SubmitEvent] = Msg()
    TYPE: Msg[InputEvent] = Msg()
    CLICK: Msg[PointerEvent] = Msg()
    TOGGLE: Msg[ToggleEvent] = Msg()


def handle(model: Panel) -> Update[Panel, PanelActions]:
    return PanelActions.cases(PanelActions.OPEN.then(State.set(Panel.open, True)))


def invalid_component_messages() -> None:
    """Messages of another group are rejected through component arguments and callbacks."""
    panel = Panel(open=False, tab="a")
    stray_select = Combobox({"a": "A"}, id="c", label="C", value=None, onselect=Stray.PICK)
    Component(panel, handle, lambda model: stray_select)  # pyright: ignore[reportArgumentType]
    Component(panel, handle, lambda model: Dialog(open=model.open, onclose=Stray.CLOSE, label="Settings"))  # pyright: ignore[reportArgumentType]
    Component(panel, handle, lambda model: Toast("Saved", open=model.open, onclose=Stray.TOAST_CLOSE))  # pyright: ignore[reportArgumentType]
    Component(panel, handle, lambda model: Form(onsubmit=Stray.SUBMIT))  # pyright: ignore[reportArgumentType]
    stray_field = field(id="f", label="F", control=lambda attrs: Input(oninput=Stray.TYPE, props=attrs))
    Component(panel, handle, lambda model: stray_field)  # pyright: ignore[reportArgumentType]
    stray_trigger = Popover(Text("p"), id="p", trigger=lambda attrs: Button("t", onclick=Stray.CLICK, props=attrs))
    Component(panel, handle, lambda model: stray_trigger)  # pyright: ignore[reportArgumentType]
    stray_toggle = Popover(Text("p"), id="p", trigger=lambda attrs: Button("t", props=attrs), ontoggle=Stray.TOGGLE)
    Component(panel, handle, lambda model: stray_toggle)  # pyright: ignore[reportArgumentType]
    Component(panel, handle, lambda model: tabs({"a": Text("A")}, model.tab, Stray.PICK, label="Tabs"))  # pyright: ignore[reportArgumentType]


def handler_forms() -> None:
    """A click handler may ignore the event, and `EventBinding.on` keeps the message group."""
    Component(Counter(count=0, items=[]), update, lambda model: Button("tick", onclick=Actions.TICK))
    stray_binding = Box(props=EventBinding.on(DomEvents.click, Other.BOOM))
    Component(Counter(count=0, items=[]), update, lambda model: stray_binding)  # pyright: ignore[reportArgumentType]
    # A mixed list is inferred as a union under strictListInference, which this project enables.
    mixed = [Button("ok", onclick=Actions.INC), Button("bad", onclick=Other.BOOM)]
    Component(Counter(count=0, items=[]), update, lambda model: VStack(mixed))  # pyright: ignore[reportArgumentType]
    # Leaf views alongside do not hide another group's message.
    Component(Counter(count=0, items=[]), update, lambda model: VStack(Text("x"), Button("y", onclick=Other.BOOM)))  # pyright: ignore[reportArgumentType]


def _count_from_event(event: PointerEvent) -> ModelUpdate[Counter]:
    return State.unchanged()


def _count_from_input(event: InputEvent) -> ModelUpdate[Counter]:
    return State.unchanged()


def _count_from_context(value: int) -> ModelUpdate[Counter]:
    return State.set(Counter.count, value)


def _count_from_text(value: str) -> ModelUpdate[Counter]:
    return State.set(Counter.count, 0)


def event_and_context_types() -> None:
    """A case receives its message's event, and with two parameters also the context of the message."""
    Actions.cases(
        Actions.INC.then(lambda event: _count_from_event(event)),
        Actions.PICK.then(lambda event, context: _count_from_context(context)),
    )
    Actions.cases(
        Actions.INC.then(lambda event: _count_from_input(event)),  # pyright: ignore[reportArgumentType]
        Actions.PICK.then(lambda event, context: _count_from_text(context)),  # pyright: ignore[reportArgumentType]
    )
