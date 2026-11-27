from typing import cast

import pytest

from fleur import Model, Msg, MsgGroup, State, emit
from fleur.core.msg import MessageEventRef


class SampleMsg(MsgGroup):
    LOADED = Msg[dict[str, object]]()


class TestMsg:
    def test_message_event_reference_compiles_from_grouped_msg(self) -> None:
        event_ref = cast(MessageEventRef[dict[str, object]], SampleMsg.LOADED.event)

        assert emit(event_ref.title.__compile__()) == "message.event.title"
        assert emit(event_ref["title"].__compile__()) == 'message.event["title"]'

    def test_message_event_fields_support_operators_at_runtime(self) -> None:
        # The event reference is an expression, so `+` builds JavaScript instead of failing.
        label = cast(MessageEventRef[dict[str, object]], SampleMsg.LOADED.event).title + "!"

        assert emit(label.__compile__()) == '(message.event.title+"!")'

    def test_grouped_msg_compiles_to_message_builder_function(self) -> None:
        source = emit(SampleMsg.LOADED.__compile__())

        assert 'type: "LOADED"' in source
        assert "event" in source


class Toggles(MsgGroup):
    OPEN: Msg[None] = Msg()
    CLOSE: Msg[None] = Msg()


class Flags(Model):
    open: State[bool]


def test_cases_must_handle_every_message_of_the_group() -> None:
    with pytest.raises(ValueError, match=r"Toggles.cases\(\) does not handle: CLOSE"):
        Toggles.cases(Toggles.OPEN.then(State.set(Flags.open, True)))


def test_unchanged_handles_a_message_without_a_state_change() -> None:
    update = Toggles.cases(Toggles.OPEN.then(State.set(Flags.open, True)), Toggles.CLOSE.then(State.unchanged()))
    assert '"CLOSE"' in emit(update.__compile__())
