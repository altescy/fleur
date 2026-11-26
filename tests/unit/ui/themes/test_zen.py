from dataclasses import replace

from fleur import emit
from fleur.ui import BASIC_THEME, ZEN_THEME, Text, theme_variables


class TestZenTheme:
    def test_zen_preset_exposes_expected_palette(self) -> None:
        variables = theme_variables(ZEN_THEME)

        assert variables["--fleur-color-bg-canvas"] == "oklch(0.9195 0.0169 88.0030)"
        assert variables["--fleur-font-body"] == '"Inter", sans-serif'

    def test_text_font_size_token_uses_text_scale_variable(self) -> None:
        source = emit(Text("label", font_size="sm").__compile__())

        assert '"font-size": "var(--fleur-text-sm)"' in source


def test_zen_dark_inherits_basic_dark_and_keeps_zen_typography() -> None:
    values = theme_variables(replace(ZEN_THEME, mode="dark"))
    assert values["--fleur-color-background"] == BASIC_THEME.dark.get("background")
    assert values["--fleur-color-primary"] == BASIC_THEME.dark.get("primary")
    assert values["--fleur-font-body"] == ZEN_THEME.theme.get("font-sans")
