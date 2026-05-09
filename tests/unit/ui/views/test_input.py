from fleur import Msg, MsgGroup, emit
from fleur.core.events import InputEvent, KeyboardEvent
from fleur.ui import Input


class FormMsg(MsgGroup):
    INPUT: Msg[InputEvent] = Msg()
    KEYDOWN: Msg[KeyboardEvent] = Msg()


class TestInput:
    def test_input_view_compiles_events_and_core_props(self) -> None:
        source = emit(
            Input(
                type="email",
                value="hello@example.com",
                placeholder="Type your email",
                oninput=FormMsg.INPUT,
                onkeydown=FormMsg.KEYDOWN,
            ).__compile__()
        )

        assert '__fleur.h("input"' in source
        assert 'type: "email"' in source
        assert 'value: "hello@example.com"' in source
        assert 'placeholder: "Type your email"' in source
        assert "oninput: function(event)" in source
        assert "onkeydown: function(event)" in source
        assert 'type: "INPUT"' in source
        assert 'type: "KEYDOWN"' in source
