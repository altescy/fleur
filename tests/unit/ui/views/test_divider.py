from fleur import Cond, Model, State, emit
from fleur.ui import Divider, css


class CondModel(Model):
    count: State[int]


class TestDivider:
    def test_divider_supports_expr_args(self) -> None:
        source = emit(Divider(color=css(Cond.when(CondModel.count > 0, "red", "blue"))).__compile__())

        assert '"--fleur-local-divider-color": ((model.count>0)?"red":"blue")' in source
