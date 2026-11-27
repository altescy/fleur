from collections.abc import Callable
from pathlib import Path

from fleur import bloom
from fleur.cli.commands._loader import load_component


def test_switching_themes_with_radio_groups_preserves_input(playwright_page: Callable[[str, Path], str]) -> None:
    example = Path(__file__).resolve().parents[3] / "examples/theme_switcher.py"
    playwright_page(bloom(load_component(f"{example}:app")), Path(__file__).with_name("theme_switcher.cjs"))
