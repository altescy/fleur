import pytest

from fleur import Cmd, Msg, MsgGroup, Sub, emit
from fleur.core import Dom, DomFocusError


class Actions(MsgGroup):
    TICK: Msg[None] = Msg()
    FOCUSED: Msg[None] = Msg()
    NOT_FOCUSED: Msg[DomFocusError] = Msg()


class Parent(MsgGroup):
    CHILD: Msg[Actions] = Msg()


def test_cmd_batch_compiles_to_runtime_batch_of_each_command() -> None:
    focus = Cmd.task(Dom.focus("editor"), Actions.FOCUSED, Actions.NOT_FOCUSED)
    js = emit(Cmd.batch(focus, Cmd.none()).__compile__())

    assert js.startswith("__fleur.Cmd.batch([__fleur.Cmd.task(")
    assert js.endswith("__fleur.Cmd.none()])")


def test_sub_batch_records_the_keys_of_its_subscriptions() -> None:
    batched = Sub.batch(Sub.interval("fast", 100, Actions.TICK), Sub.none(), Sub.interval("slow", 1000, Actions.TICK))

    assert batched.keys == ("fast", "slow")
    assert Sub.map(Parent.CHILD, batched).keys == ("fast", "slow")
    assert emit(batched.__compile__()).startswith('__fleur.Sub.batch([__fleur.Sub.interval("fast",100,')


def test_sub_batch_rejects_subscriptions_with_the_same_key() -> None:
    clock = Sub.interval("clock", 100, Actions.TICK)
    nested = Sub.batch(Sub.interval("other", 100, Actions.TICK), Sub.interval("clock", 1000, Actions.TICK))

    with pytest.raises(ValueError, match="same key: clock"):
        Sub.batch(clock, nested)
