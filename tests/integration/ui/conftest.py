import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Literal, NoReturn, cast

import pytest


def _missing_browser_dependency(reason: str) -> NoReturn:
    if os.getenv("FLEUR_REQUIRE_BROWSER_TESTS") == "1":
        pytest.fail(reason)
    pytest.skip(reason)


def _playwright_page(tmp_path: Path, engine: Literal["chromium", "webkit"]) -> Callable[[str, Path], str]:
    node = shutil.which("node")
    if not node:
        _missing_browser_dependency("browser tests require Node")
    if subprocess.run(
        [node, "-e", "require.resolve('playwright-core')"], cwd=Path(__file__).parent, capture_output=True
    ).returncode:
        _missing_browser_dependency("browser tests require playwright-core")

    if engine == "chromium":
        browser = os.getenv("FLEUR_TEST_CHROMIUM") or shutil.which("chromium") or shutil.which("google-chrome")
        if not browser:
            _missing_browser_dependency("browser tests require Chromium")
    else:
        browser = subprocess.check_output(
            [node, "-p", "require('playwright-core').webkit.executablePath()"], cwd=Path(__file__).parent, text=True
        ).strip()
        if not Path(browser).is_file():
            _missing_browser_dependency("browser tests require Playwright WebKit (install webkit)")

    def run(html: str, probe: Path) -> str:
        page = tmp_path / "page.html"
        page.write_text(html, encoding="utf-8")
        result = subprocess.run(
            [node, str(probe), browser, page.as_uri(), engine],
            check=True,
            timeout=60,
            text=True,
            stdout=subprocess.PIPE,
        )
        return result.stdout

    return run


@pytest.fixture
def playwright_page(tmp_path: Path) -> Callable[[str, Path], str]:
    """Run a Chromium probe against the self-contained HTML produced by bloom."""
    return _playwright_page(tmp_path, "chromium")


@pytest.fixture(params=["chromium", "webkit"])
def overlay_focus_page(request: pytest.FixtureRequest, tmp_path: Path) -> Callable[[str, Path], str]:
    return _playwright_page(tmp_path, cast(Literal["chromium", "webkit"], request.param))


@pytest.fixture
def chromium_title(playwright_page: Callable[[str, Path], str]) -> Callable[[str], str]:
    """Read a layout probe's document.title after Chromium executes the page."""

    def render(html: str) -> str:
        return playwright_page(html, Path(__file__).with_name("page_title.cjs"))

    return render
