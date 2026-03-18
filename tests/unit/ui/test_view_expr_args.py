from fleur import Cond, Model, State, emit
from fleur.ui import Divider, Grid, GridItem, Text


class CondModel(Model):
    count: State[int]


def test_text_supports_expr_style_args() -> None:
    source = emit(Text("value", fg=Cond.when(CondModel.count > 0, "red", "blue")).__compile__())

    assert 'color: ((model.count>0)?"red":"blue")' in source


def test_grid_supports_expr_columns() -> None:
    source = emit(Grid("value", columns=Cond.when(CondModel.count > 0, 2, 3)).__compile__())

    assert '"grid-template-columns": (("repeat("+((model.count>0)?2:3))+", minmax(0, 1fr))")' in source


def test_grid_item_and_divider_support_expr_args() -> None:
    grid_item_source = emit(GridItem("value", col_span=Cond.when(CondModel.count > 0, 2, 3)).__compile__())
    divider_source = emit(Divider(color=Cond.when(CondModel.count > 0, "red", "blue")).__compile__())

    assert '"grid-column": ("span "+((model.count>0)?2:3))' in grid_item_source
    assert '"border-top": ("1px solid "+((model.count>0)?"red":"blue"))' in divider_source
