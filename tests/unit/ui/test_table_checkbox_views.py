from fleur import Cond, Model, Msg, MsgGroup, State, emit
from fleur.core.events import InputEvent
from fleur.ui import Checkbox, Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow


class TableModel(Model):
    enabled: State[bool]


class TableMsg(MsgGroup):
    TOGGLE: Msg[InputEvent] = Msg()


def test_checkbox_view_compiles_checked_state_and_change_event() -> None:
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


def test_table_views_compile_semantic_tags_and_defaults() -> None:
    source = emit(
        Table(
            TableHeader(
                TableRow(
                    TableHead("Name"),
                    TableHead("Role", align="right"),
                )
            ),
            TableBody(
                TableRow(
                    TableCell("Alice"),
                    TableCell("Admin", align="right"),
                )
            ),
            TableCaption("Team members"),
        ).__compile__()
    )

    assert '__fleur.h("table"' in source
    assert '__fleur.h("thead"' in source
    assert '__fleur.h("tbody"' in source
    assert '__fleur.h("tr"' in source
    assert '__fleur.h("th"' in source
    assert '__fleur.h("td"' in source
    assert '__fleur.h("caption"' in source
    assert '"border-bottom": "1px solid var(--fleur-color-border-default)"' in source
    assert '"text-align": "right"' in source
