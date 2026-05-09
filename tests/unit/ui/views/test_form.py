from fleur import Msg, MsgGroup, emit
from fleur.core.events import SubmitEvent
from fleur.ui import Form, Text


class FormMsg(MsgGroup):
    SUBMIT: Msg[SubmitEvent] = Msg()


class TestForm:
    def test_form_compiles_submit_event(self) -> None:
        source = emit(
            Form(
                Text("Feedback"),
                onsubmit=FormMsg.SUBMIT,
            ).__compile__()
        )

        assert '__fleur.h("form"' in source
        assert "onsubmit: function(event)" in source
        assert 'type: "SUBMIT"' in source
