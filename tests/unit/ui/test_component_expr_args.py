from fleur import Cond, emit
from fleur.ui.components import DialogModel, TabsModel, TabSpec, dialog, tabs


def test_dialog_supports_expr_arguments() -> None:
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


def test_tabs_supports_expr_arguments() -> None:
    source = emit(
        tabs(
            [
                TabSpec(
                    label=Cond.when(TabsModel.active_index.eq(0), "Home*", "Home"),
                    content=Cond.when(TabsModel.active_index.eq(0), "Active", "Inactive"),
                )
            ],
            title=Cond.when(TabsModel.active_index.eq(0), "Tabs*", "Tabs"),
            empty_message=Cond.when(TabsModel.active_index.eq(0), "None*", "None"),
        ).__compile__()
    )

    assert '(model.active_index===0)?"Tabs*":"Tabs"' in source
    assert '(model.active_index===0)?"Home*":"Home"' in source


def test_tabs_does_not_render_default_title_when_omitted() -> None:
    source = emit(tabs([TabSpec(label="Home", content="Panel")]).__compile__())

    assert '"Tabs"' not in source


def test_tabs_supports_custom_wrapper_props() -> None:
    source = emit(
        tabs(
            [TabSpec(label="Home", content="Panel")],
            list_props={"data-testid": "tabs-list"},
            panel_props={"data-testid": "tabs-panel"},
        ).__compile__()
    )

    assert '"data-testid": "tabs-list"' in source
    assert '"data-testid": "tabs-panel"' in source
