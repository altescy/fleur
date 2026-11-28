import pytest

from fleur import Component, Model, Msg, MsgGroup, State, Update, View, emit
from fleur.ui import Text


class Leaf(Model):
    n: State[int]


class Branch(Model):
    leaf: State[Leaf]


class Tree(Model):
    branch: State[Branch]


class LeafMsg(MsgGroup):
    INC: Msg[None] = Msg()


class TreeMsg(MsgGroup):
    LEAF: Msg[LeafMsg] = Msg()


leaf = Component(
    Leaf(n=0),
    lambda model: LeafMsg.cases(LeafMsg.INC.then(State.set(Leaf.n, model.n + 1))),
    lambda model: Text("leaf"),
)


def test_forward_to_a_top_level_field_is_accepted() -> None:
    branch = Component(
        Branch(leaf=leaf.init.model),
        lambda model: TreeMsg.cases(TreeMsg.LEAF.then(Update.forward(Branch.leaf, leaf, TreeMsg.LEAF))),
        lambda model: Text("branch"),
    )
    assert '"LEAF"' in emit(branch.__compile__())


def test_update_forward_rejects_a_nested_field() -> None:
    with pytest.raises(ValueError, match="takes a field of the model itself"):
        Update.forward(Tree.branch[Branch.leaf], leaf, TreeMsg.LEAF)


def test_view_forward_rejects_a_nested_field() -> None:
    with pytest.raises(ValueError, match="takes a field of the model itself"):
        View.forward(Tree.branch[Branch.leaf], leaf, TreeMsg.LEAF)
