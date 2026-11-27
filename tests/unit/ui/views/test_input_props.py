from fleur import Msg, MsgGroup, emit
from fleur.core import PointerEvent
from fleur.ui import Combobox, NumberField


class Actions(MsgGroup):
    PICK: Msg[PointerEvent, str] = Msg()


def test_number_field_keeps_input_props_that_are_not_given_as_arguments() -> None:
    js = emit(NumberField(input_props={"name": "qty", "required": True, "step": "any"}).__compile__())

    assert 'name: "qty"' in js
    assert "required: true" in js
    assert 'step: "any"' in js


def test_number_field_arguments_override_input_props() -> None:
    js = emit(NumberField(name="amount", required=False, input_props={"name": "qty", "required": True}).__compile__())

    assert 'name: "amount"' in js and 'name: "qty"' not in js
    assert "required: false" in js


def test_combobox_keeps_disabled_from_input_props_but_not_pattern_attributes() -> None:
    def render(disabled: bool | None) -> str:
        combobox = Combobox(
            {"a": "Alpha"},
            id="fruit",
            label="Fruit",
            value=None,
            onselect=Actions.PICK,
            disabled=disabled,
            input_props={"disabled": True, "autocomplete": "name", "role": "textbox"},
        )
        return emit(combobox.__compile__())

    inherited, overridden = render(None), render(False)
    assert "disabled: true" in inherited
    assert "disabled: false" in overridden
    assert 'autocomplete: "off"' in inherited and 'role: "combobox"' in inherited
