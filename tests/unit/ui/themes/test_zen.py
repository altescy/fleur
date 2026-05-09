from fleur import emit
from fleur.ui import ZEN_THEME, Text, theme_variables


class TestZenTheme:
    def test_zen_preset_exposes_expected_palette(self) -> None:
        variables = theme_variables(ZEN_THEME)

        assert variables["--fleur-color-bg-canvas"] == "oklch(0.9195 0.0169 88.0030)"
        assert variables["--fleur-font-body"] == '"Inter", sans-serif'

    def test_text_font_size_token_uses_text_scale_variable(self) -> None:
        source = emit(Text("label", font_size="sm").__compile__())

        assert '"font-size": "var(--fleur-text-sm)"' in source
