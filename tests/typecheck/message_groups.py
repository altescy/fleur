# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check that a component's view, commands and subscriptions only produce messages its update handles."""

from fleur import Array, Cmd, Component, Cond, Model, Msg, MsgGroup, State, Sub
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


update = Actions.cases(
    Actions.INC.then(State.set(Counter.count, Counter.count + 1)),
    Actions.PICK.then(State.set(Counter.count, Actions.PICK.context)),
)


def valid_examples() -> None:
    Component(
        Counter(count=0, items=[]),
        update,
        VStack(
            Button("+", onclick=Actions.INC),
            Button("Pick", onclick=Actions.PICK.bind(1)),
            Input(oninput=Actions.TYPE),
            Box(Text("nested"), Button("deep", onclick=Actions.INC)),
            Array.map(Counter.items, lambda item: Button(item, onclick=Actions.INC)),
            Cond.when(Counter.count > 0, Button("reset", onclick=Actions.INC), None),
            Box(props={"onclick": Actions.INC}),
            Box(props=EventBinding.on(DomEvents.click, Actions.INC)),
            "text",
        ),
        Sub.interval("tick", 1000, Actions.TICK),
    )


def invalid_examples() -> None:
    # A view message from another group.
    Component(Counter(count=0, items=[]), update, VStack(Button("x", onclick=Other.BOOM)))  # pyright: ignore[reportArgumentType]
    # The same, nested inside layout views.
    Component(Counter(count=0, items=[]), update, VStack(Box(Box(Button("x", onclick=Other.BOOM)))))  # pyright: ignore[reportArgumentType]
    # Inside a mapped list.
    Component(
        Counter(count=0, items=[]),
        update,  # pyright: ignore[reportArgumentType]
        VStack(Array.map(Counter.items, lambda item: Button(item, onclick=Other.BOOM))),
    )
    # Through raw props.
    Component(Counter(count=0, items=[]), update, Box(props={"onclick": Other.BOOM}))  # pyright: ignore[reportArgumentType]
    # A message with a context that was never bound.
    Button("x", onclick=Actions.PICK)  # pyright: ignore[reportArgumentType]
    Box(props={"onclick": Actions.PICK})  # pyright: ignore[reportArgumentType]
    # A subscription or command producing another group's message.
    Component(Counter(count=0, items=[]), update, Text("x"), Sub.interval("tick", 1000, Other.TICK))  # pyright: ignore[reportArgumentType]
    Actions.cases(Actions.INC.then((State.set(Counter.count, 0), Cmd.map(Other.BOOM, Cmd.none()))))  # pyright: ignore[reportArgumentType]


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


def invalid_component_messages() -> None:
    """Messages of another group are rejected through component arguments and callbacks."""
    panel = Panel(open=False, tab="a")
    handle = PanelActions.cases(PanelActions.OPEN.then(State.set(Panel.open, True)))
    stray_select = Combobox({"a": "A"}, id="c", label="C", value=None, onselect=Stray.PICK)
    Component(panel, handle, stray_select)  # pyright: ignore[reportArgumentType]
    Component(panel, handle, Dialog(open=Panel.open, onclose=Stray.CLOSE, label="Settings"))  # pyright: ignore[reportArgumentType]
    Component(panel, handle, Toast("Saved", open=Panel.open, onclose=Stray.TOAST_CLOSE))  # pyright: ignore[reportArgumentType]
    Component(panel, handle, Form(onsubmit=Stray.SUBMIT))  # pyright: ignore[reportArgumentType]
    stray_field = field(id="f", label="F", control=lambda attrs: Input(oninput=Stray.TYPE, props=attrs))
    Component(panel, handle, stray_field)  # pyright: ignore[reportArgumentType]
    stray_trigger = Popover(Text("p"), id="p", trigger=lambda attrs: Button("t", onclick=Stray.CLICK, props=attrs))
    Component(panel, handle, stray_trigger)  # pyright: ignore[reportArgumentType]
    stray_toggle = Popover(Text("p"), id="p", trigger=lambda attrs: Button("t", props=attrs), ontoggle=Stray.TOGGLE)
    Component(panel, handle, stray_toggle)  # pyright: ignore[reportArgumentType]
    Component(panel, handle, tabs({"a": Text("A")}, Panel.tab, Stray.PICK, label="Tabs"))  # pyright: ignore[reportArgumentType]


def handler_forms() -> None:
    """A click handler may ignore the event, and `EventBinding.on` keeps the message group."""
    Component(Counter(count=0, items=[]), update, Button("tick", onclick=Actions.TICK))
    stray_binding = Box(props=EventBinding.on(DomEvents.click, Other.BOOM))
    Component(Counter(count=0, items=[]), update, stray_binding)  # pyright: ignore[reportArgumentType]
    # A mixed list is inferred as a union under strictListInference, which this project enables.
    mixed = [Button("ok", onclick=Actions.INC), Button("bad", onclick=Other.BOOM)]
    Component(Counter(count=0, items=[]), update, VStack(mixed))  # pyright: ignore[reportArgumentType]
    # Leaf views alongside do not hide another group's message.
    Component(Counter(count=0, items=[]), update, VStack(Text("x"), Button("y", onclick=Other.BOOM)))  # pyright: ignore[reportArgumentType]
