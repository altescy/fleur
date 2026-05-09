from fleur import Component, Model, MsgGroup, bloom
from fleur.ui import Text, Theme, theme_style_tag, theme_variables


class _DemoModel(Model):
    pass


class _DemoMsg(MsgGroup):
    pass


class TestBaseTheme:
    def test_theme_style_tag_includes_text_scale_and_body_font_size(self) -> None:
        css = theme_style_tag(Theme())

        assert "--fleur-text-base: 1rem;" in css
        assert "--fleur-text-sm: 0.875rem;" in css
        assert "font-size:var(--fleur-text-base);" in css

    def test_bloom_applies_default_theme_when_omitted(self) -> None:
        html = bloom(Component(_DemoModel(), _DemoMsg.caseof(), Text("demo")))

        assert "--fleur-text-base: 1rem;" in html

    def test_theme_variables_expose_direct_fleur_color_tokens(self) -> None:
        variables = theme_variables(Theme())

        assert "--fleur-color-muted" in variables
        assert "--fleur-color-card" in variables
        assert "--fleur-color-accent" in variables
        assert "--fleur-color-surface" in variables
        assert "--fleur-color-code" in variables
        assert "--fleur-color-selection" in variables

    def test_theme_style_tag_includes_base_styles_for_common_html_elements(self) -> None:
        css = theme_style_tag(Theme())

        assert (
            "::selection{background:var(--fleur-color-selection);color:var(--fleur-color-selection-foreground);}" in css
        )
        assert "h1,h2,h3,h4,h5,h6,p,figure,blockquote,dl,dd{margin:0;}" in css
        assert "table{border-collapse:collapse;border-spacing:0;width:100%;}" in css
        assert "code{background:var(--fleur-color-code);color:var(--fleur-color-code-foreground);" in css
