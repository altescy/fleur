from fleur import Cond, Model, State, emit
from fleur.ui import Grid, GridItem


class CondModel(Model):
    count: State[int]


class TestGrid:
    def test_grid_supports_expr_columns(self) -> None:
        source = emit(Grid("value", columns=Cond.when(CondModel.count > 0, 2, 3)).__compile__())

        assert '"grid-template-columns": (("repeat("+((model.count>0)?2:3))+", minmax(0, 1fr))")' in source

    def test_grid_item_supports_expr_args(self) -> None:
        source = emit(GridItem("value", col_span=Cond.when(CondModel.count > 0, 2, 3)).__compile__())

        assert '"grid-column": ("span "+((model.count>0)?2:3))' in source
