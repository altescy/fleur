from fleur import Component, Model, MsgGroup, bloom
from fleur.ui import BASIC_THEME, Button, Text, Theme, theme_style_tag, theme_variables


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
        html = bloom(Component(_DemoModel(), _DemoMsg.cases(), Text("demo")))

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


def test_partial_dark_palette_uses_only_same_mode_layers() -> None:
    base = Theme(colors={"border": "gray"}, light={"primary": "pink"}, dark={"primary": "navy"})
    theme = Theme(mode="dark", light={"foreground": "red"}, dark={"secondary": "purple"})

    values = theme_variables(theme, base_theme=base)
    assert values["--fleur-color-primary"] == "navy"
    assert values["--fleur-color-secondary"] == "purple"
    assert values["--fleur-color-foreground"] == BASIC_THEME.dark.get("foreground")
    assert values["--fleur-color-border"] == "gray"


def test_bloom_connects_typed_scales_and_button_shorthands() -> None:
    theme = Theme(colors={"primary": "#2457a6"}, space={"lg": 20}, radii={"sm": 3})
    html = bloom(
        Component(_DemoModel(), _DemoMsg.cases(), Button("Save", bg="primary", p="lg", radius="sm")), theme=theme
    )

    assert "--fleur-color-primary: #2457a6;" in html
    assert "--fleur-space-lg: 20px;" in html
    assert "--fleur-radius-sm: 3px;" in html
    assert '"--fleur-local-bg": "var(--fleur-color-primary)"' in html
    assert "background:var(--fleur-local-bg)" in html
    assert 'padding: "var(--fleur-space-lg)"' in html
    assert '"border-radius": "var(--fleur-radius-sm)"' in html
    assert '"padding-left":' not in html
