from fleur import Cond, Model, State, emit
from fleur.ui import Text


class CondModel(Model):
    count: State[int]


class TestText:
    def test_text_supports_expr_style_args(self) -> None:
        source = emit(Text("value", fg=Cond.when(CondModel.count > 0, "red", "blue")).__compile__())

        assert '((model.count>0)?"red":"blue").toLowerCase()' in source
        assert '((model.count>0)?"red":"blue"):((' in source

    def test_text_expr_color_tokens_are_normalized_to_css_vars(self) -> None:
        source = emit(Text("value", fg=Cond.when(CondModel.count > 0, "fg-default", "fg-muted")).__compile__())

        assert '"var(--fleur-color-"+((model.count>0)?"fg-default":"fg-muted"))+")"' in source

    def test_expr_spacing_radius_and_font_size_tokens_are_normalized(self) -> None:
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
