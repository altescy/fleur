# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check that a forwarded child component matches the type of the field that stores its model."""

from fleur import Component, Model, Msg, MsgGroup, State, Update, View
from fleur.ui import Text


class Child(Model):
    n: State[int]


class Other(Model):
    s: State[str]


class ChildMsg(MsgGroup):
    INC: Msg[None] = Msg()


class Parent(Model):
    child: State[Child]


class ParentMsg(MsgGroup):
    CHILD: Msg[ChildMsg] = Msg()


child = Component(
    Child(n=0),
    lambda model: ChildMsg.cases(ChildMsg.INC.then(State.set(Child.n, 1))),
    lambda model: Text("c"),
)
other = Component(
    Other(s=""),
    lambda model: ChildMsg.cases(ChildMsg.INC.then(State.set(Other.s, "x"))),
    lambda model: Text("o"),
)


def child_view(model: Child) -> View[Child, ChildMsg]:
    return Text("c")


def examples() -> None:
    Update.forward(Parent.child, child, ParentMsg.CHILD)
    Update.forward(Parent.child, other, ParentMsg.CHILD)  # pyright: ignore[reportArgumentType]
    View.forward(Parent.child, child, ParentMsg.CHILD)
    View.forward(Parent.child, other, ParentMsg.CHILD)  # pyright: ignore[reportArgumentType]


class Stray(MsgGroup):
    TICK: Msg[None] = Msg()


def tagger_groups() -> None:
    ParentMsg.cases(ParentMsg.CHILD.then(Update.forward(Parent.child, child, ParentMsg.CHILD)))
    ParentMsg.cases(ParentMsg.CHILD.then(Update.forward(Parent.child, child, Stray.TICK)))  # pyright: ignore[reportCallIssue,reportArgumentType]


class WrongTagger(MsgGroup):
    CHILD: Msg[Stray] = Msg()


def tagger_events() -> None:
    """A tagger declares the child's message group as its event."""
    View.forward(Parent.child, child, WrongTagger.CHILD)  # pyright: ignore[reportArgumentType]
    View.map(ParentMsg.CHILD, child_view(Child(n=0)))
    View.map(WrongTagger.CHILD, child_view(Child(n=0)))  # pyright: ignore[reportArgumentType]
