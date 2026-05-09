from fleur import Cond, Model, State, emit
from fleur.ui import Divider


class CondModel(Model):
    count: State[int]


class TestDivider:
    def test_divider_supports_expr_args(self) -> None:
        source = emit(Divider(color=Cond.when(CondModel.count > 0, "red", "blue")).__compile__())

        assert '"border-top": ("1px solid "+((model.count>0)?"red":"blue"))' in source
