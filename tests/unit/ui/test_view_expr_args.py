from fleur import Cond, Model, State, emit
from fleur.ui import Divider, Grid, GridItem, Text


class CondModel(Model):
    count: State[int]


def test_text_supports_expr_style_args() -> None:
    source = emit(Text("value", fg=Cond.when(CondModel.count > 0, "red", "blue")).__compile__())

    assert '((model.count>0)?"red":"blue").toLowerCase()' in source
    assert '((model.count>0)?"red":"blue"):((' in source


def test_grid_supports_expr_columns() -> None:
    source = emit(Grid("value", columns=Cond.when(CondModel.count > 0, 2, 3)).__compile__())

    assert '"grid-template-columns": (("repeat("+((model.count>0)?2:3))+", minmax(0, 1fr))")' in source


def test_grid_item_and_divider_support_expr_args() -> None:
    grid_item_source = emit(GridItem("value", col_span=Cond.when(CondModel.count > 0, 2, 3)).__compile__())
    divider_source = emit(Divider(color=Cond.when(CondModel.count > 0, "red", "blue")).__compile__())

    assert '"grid-column": ("span "+((model.count>0)?2:3))' in grid_item_source
    assert '"border-top": ("1px solid "+((model.count>0)?"red":"blue"))' in divider_source


def test_text_expr_color_tokens_are_normalized_to_css_vars() -> None:
    source = emit(Text("value", fg=Cond.when(CondModel.count > 0, "fg-default", "fg-muted")).__compile__())

    assert '"var(--fleur-color-"+((model.count>0)?"fg-default":"fg-muted"))+")"' in source


def test_expr_spacing_radius_and_font_size_tokens_are_normalized() -> None:
    source = emit(
        Text(
            "value",
            p=Cond.when(CondModel.count > 0, "sm", "md"),
            radius=Cond.when(CondModel.count > 0, "sm", "md"),
            font_size=Cond.when(CondModel.count > 0, "sm", "lg"),
        ).__compile__()
    )

    assert '"var(--fleur-space-"' in source
    assert '"var(--fleur-radius-"' in source
    assert '"var(--fleur-text-"' in source
    assert '((model.count>0)?"sm":"md")' in source
    assert '((model.count>0)?"sm":"lg")' in source
