from typing import cast

from fleur import Msg, MsgGroup, emit
from fleur.core.msg import MessageEventRef


class SampleMsg(MsgGroup):
    LOADED = Msg[dict[str, object]]()


def test_message_event_reference_compiles_from_grouped_msg() -> None:
    event_ref = cast(MessageEventRef[dict[str, object]], SampleMsg.LOADED.event)
    source = emit(event_ref["title"].__compile__())

    assert source == "message.event.title"


def test_grouped_msg_compiles_to_message_builder_function() -> None:
    source = emit(SampleMsg.LOADED.__compile__())

    assert 'type: "LOADED"' in source
    assert "event" in source
