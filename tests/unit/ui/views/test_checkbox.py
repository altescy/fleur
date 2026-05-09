from fleur import Cond, Model, Msg, MsgGroup, State, emit
from fleur.core.events import InputEvent
from fleur.ui import Checkbox


class TableModel(Model):
    enabled: State[bool]


class TableMsg(MsgGroup):
    TOGGLE: Msg[InputEvent] = Msg()


class TestCheckbox:
    def test_checkbox_view_compiles_checked_state_and_change_event(self) -> None:
        source = emit(
            Checkbox(
                checked=Cond.when(TableModel.enabled, True, False),
                name="accept",
                onchange=TableMsg.TOGGLE,
            ).__compile__()
        )

        assert '__fleur.h("input"' in source
        assert 'type: "checkbox"' in source
        assert 'name: "accept"' in source
        assert "checked: (model.enabled?true:false)" in source
        assert "onchange: function(event)" in source
        assert 'type: "TOGGLE"' in source
