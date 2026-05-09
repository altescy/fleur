from fleur import Cond, Model, Msg, MsgGroup, State, emit
from fleur.core.events import InputEvent
from fleur.ui import Textarea


class FormModel(Model):
    count: State[int]


class FormMsg(MsgGroup):
    INPUT: Msg[InputEvent] = Msg()


class TestTextarea:
    def test_textarea_compiles_rows_expression_and_input_event(self) -> None:
        source = emit(
            Textarea(
                rows=Cond.when(FormModel.count > 0, 4, 2),
                oninput=FormMsg.INPUT,
            ).__compile__()
        )

        assert '__fleur.h("textarea"' in source
        assert "rows: ((model.count>0)?4:2)" in source
        assert "oninput: function(event)" in source
        assert 'type: "INPUT"' in source
