from collections.abc import Callable
from pathlib import Path

from fleur import bloom
from fleur.cli.commands._loader import load_component


def test_expense_sort_with_category_filter(playwright_page: Callable[[str, Path], str]) -> None:
    example = Path(__file__).resolve().parents[3] / "examples/expense_report.py"
    playwright_page(bloom(load_component(f"{example}:app")), Path(__file__).with_name("expense_sort.cjs"))
