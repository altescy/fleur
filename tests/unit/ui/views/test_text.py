from fleur import Cond, Model, State, emit
from fleur.ui import Background, Text, ThemeFontSizeName, ThemeRadiusName, ThemeSpaceName, css


class CondModel(Model):
    count: State[int]
    space: State[ThemeSpaceName]
    radius: State[ThemeRadiusName]
    font: State[ThemeFontSizeName]


class TestText:
    def test_static_raw_css_and_pixel_spacing(self) -> None:
        source = emit(Text("value", bg=css("oklch(65% 0.2 260)"), p=8).__compile__())

        assert '"data-fleur-ui": "text"' in source
        assert '"--fleur-local-bg": "oklch(65% 0.2 260)"' in source
        assert 'padding: "8px"' in source

    def test_text_supports_expr_style_args(self) -> None:
        source = emit(Text("value", fg=css(Cond.when(CondModel.count > 0, "red", "blue"))).__compile__())

        assert 'color: ((model.count>0)?"red":"blue")' in source

    def test_text_expr_color_tokens_are_normalized_to_css_vars(self) -> None:
        source = emit(Text("value", fg=Background.when(CondModel.count > 0, "primary", "transparent")).__compile__())

        assert '"var(--fleur-color-"+((model.count>0)?"primary":"transparent"))+")"' in source

    def test_expr_spacing_radius_and_font_size_tokens_are_normalized(self) -> None:
        source = emit(
            Text(
                "value",
                p=CondModel.space,
                radius=CondModel.radius,
                font_size=CondModel.font,
            ).__compile__()
        )

        assert '"var(--fleur-space-"' in source
        assert '"var(--fleur-radius-"' in source
        assert '"var(--fleur-text-"' in source
        assert "String(model.space)" in source
        assert "String(model.radius)" in source
        assert "String(model.font)" in source
