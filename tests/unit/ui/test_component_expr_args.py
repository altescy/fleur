from fleur import Expr, compile_component, emit
from fleur.ui.components import DialogModel, TabsModel, TabSpec, dialog, tabs


def test_dialog_supports_expr_arguments() -> None:
    source = emit(
        compile_component(
            dialog(
                title=Expr.when(DialogModel.open, "Open dialog", "Closed dialog"),
                trigger=Expr.when(DialogModel.open, "Hide", "Show"),
                message=Expr.when(DialogModel.open, "Visible", "Hidden"),
            )
        )
    )

    assert '(model.open?"Open dialog":"Closed dialog")' in source
    assert '(model.open?"Hide":"Show")' in source
    assert '(model.open?"Visible":"Hidden")' in source


def test_tabs_supports_expr_arguments() -> None:
    source = emit(
        compile_component(
            tabs(
                [
                    TabSpec(
                        label=Expr.when(TabsModel.active_index.equals(0), "Home*", "Home"),
                        content=Expr.when(TabsModel.active_index.equals(0), "Active", "Inactive"),
                    )
                ],
                title=Expr.when(TabsModel.active_index.equals(0), "Tabs*", "Tabs"),
                empty_message=Expr.when(TabsModel.active_index.equals(0), "None*", "None"),
            )
        )
    )

    assert '(model.active_index===0)?"Tabs*":"Tabs"' in source
    assert '(model.active_index===0)?"Home*":"Home"' in source
