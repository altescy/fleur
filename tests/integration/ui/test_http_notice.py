from collections.abc import Callable
from pathlib import Path

from fleur import bloom
from fleur.cli.commands._loader import load_component


def test_http_notice_retries_failed_request(playwright_page: Callable[[str, Path], str]) -> None:
    example = Path(__file__).resolve().parents[3] / "examples/http_status/app.py"
    playwright_page(bloom(load_component(f"{example}:app")), Path(__file__).with_name("http_notice.cjs"))
