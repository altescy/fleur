from fleur import Cond, emit
from fleur.ui.components import DialogModel, dialog


class TestDialog:
    def test_dialog_supports_expr_arguments(self) -> None:
        source = emit(
            dialog(
                title=Cond.when(DialogModel.open, "Open dialog", "Closed dialog"),
                trigger=Cond.when(DialogModel.open, "Hide", "Show"),
                message=Cond.when(DialogModel.open, "Visible", "Hidden"),
            ).__compile__()
        )

        assert '(model.open?"Open dialog":"Closed dialog")' in source
        assert '(model.open?"Hide":"Show")' in source
        assert '(model.open?"Visible":"Hidden")' in source
