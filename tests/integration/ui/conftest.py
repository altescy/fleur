import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

import pytest


def _missing_browser_dependency(reason: str) -> NoReturn:
    if os.getenv("FLEUR_REQUIRE_BROWSER_TESTS") == "1":
        pytest.fail(reason)
    pytest.skip(reason)


@pytest.fixture
def playwright_page(tmp_path: Path) -> Callable[[str, Path], str]:
    """Run a Playwright probe against the self-contained HTML produced by bloom."""
    browser = os.getenv("FLEUR_TEST_CHROMIUM") or shutil.which("chromium") or shutil.which("google-chrome")
    node = shutil.which("node")
    if not browser or not node:
        _missing_browser_dependency("browser tests require Chromium and Node")
    if subprocess.run(
        [node, "-e", "require.resolve('playwright-core')"], cwd=Path(__file__).parent, capture_output=True
    ).returncode:
        _missing_browser_dependency("browser tests require playwright-core")

    def run(html: str, probe: Path) -> str:
        page = tmp_path / "page.html"
        page.write_text(html, encoding="utf-8")
        result = subprocess.run(
            [node, str(probe), browser, page.as_uri()], check=True, timeout=60, text=True, stdout=subprocess.PIPE
        )
        return result.stdout

    return run


@pytest.fixture
def chromium_title(playwright_page: Callable[[str, Path], str]) -> Callable[[str], str]:
    """Read a layout probe's document.title after Chromium executes the page."""

    def render(html: str) -> str:
        return playwright_page(html, Path(__file__).with_name("page_title.cjs"))

    return render
