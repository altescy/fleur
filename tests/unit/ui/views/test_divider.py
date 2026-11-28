from fleur import Cond, Model, State, emit
from fleur.core.model import model_ref
from fleur.js.builder import ident
from fleur.ui import Divider, css


class CondModel(Model):
    count: State[int]


model = model_ref(CondModel, ident("model"))


class TestDivider:
    def test_divider_supports_expr_args(self) -> None:
        source = emit(Divider(color=css(Cond.when(model.count > 0, "red", "blue"))).__compile__())

        assert '"--fleur-local-divider-color": ((model.count>0)?"red":"blue")' in source
