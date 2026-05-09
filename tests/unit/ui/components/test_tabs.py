from fleur import Cond, emit
from fleur.ui.components import TabsModel, TabSpec, tabs


class TestTabs:
    def test_tabs_supports_expr_arguments(self) -> None:
        source = emit(
            tabs(
                [
                    TabSpec(
                        label=Cond.when(Cond.equal(TabsModel.active_index, 0), "Home*", "Home"),
                        content=Cond.when(Cond.equal(TabsModel.active_index, 0), "Active", "Inactive"),
                    )
                ],
                title=Cond.when(Cond.equal(TabsModel.active_index, 0), "Tabs*", "Tabs"),
                empty_message=Cond.when(Cond.equal(TabsModel.active_index, 0), "None*", "None"),
            ).__compile__()
        )

        assert '(model.active_index===0)?"Tabs*":"Tabs"' in source
        assert '(model.active_index===0)?"Home*":"Home"' in source

    def test_tabs_does_not_render_default_title_when_omitted(self) -> None:
        source = emit(tabs([TabSpec(label="Home", content="Panel")]).__compile__())

        assert '"Tabs"' not in source

    def test_tabs_supports_custom_wrapper_props(self) -> None:
        source = emit(
            tabs(
                [TabSpec(label="Home", content="Panel")],
                list_props={"data-testid": "tabs-list"},
                panel_props={"data-testid": "tabs-panel"},
            ).__compile__()
        )

        assert '"data-testid": "tabs-list"' in source
        assert '"data-testid": "tabs-panel"' in source
