from fleur import Expr, Model, Msg, MsgGroup, State, emit
from fleur.core.events import InputEvent, KeyboardEvent, SubmitEvent
from fleur.ui import Form, Input, Text, Textarea


class FormModel(Model):
    count: State[int]


class FormMsg(MsgGroup):
    INPUT: Msg[InputEvent] = Msg()
    KEYDOWN: Msg[KeyboardEvent] = Msg()
    SUBMIT: Msg[SubmitEvent] = Msg()


def test_input_view_compiles_events_and_core_props() -> None:
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


def test_textarea_and_form_compile_rows_expression_and_submit_event() -> None:
    source = emit(
        Form(
            Text("Feedback"),
            Textarea(
                rows=Expr.when(FormModel.count > 0, 4, 2),
                oninput=FormMsg.INPUT,
            ),
            onsubmit=FormMsg.SUBMIT,
        ).__compile__()
    )

    assert '__fleur.h("form"' in source
    assert '__fleur.h("textarea"' in source
    assert "rows: ((model.count>0)?4:2)" in source
    assert "onsubmit: function(event)" in source
    assert 'type: "SUBMIT"' in source
