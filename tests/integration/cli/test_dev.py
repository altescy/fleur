import os
from pathlib import Path
from unittest.mock import Mock

import pytest

from fleur.cli.commands import dev


def test_reload_detects_rebuilt_assets_outside_app_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app_dir = tmp_path / "example"
    app_dir.mkdir()
    entry = app_dir / "app.py"
    entry.write_text("")
    assets = tuple(tmp_path / path.name for path in dev._EMBEDDED_ASSETS)
    monkeypatch.setattr(dev, "_EMBEDDED_ASSETS", assets)
    for asset in assets:
        asset.touch()
    previous = dev._snapshot(app_dir)
    for name in ("fleur.js", "base.css", "elements.css"):
        asset = tmp_path / name
        asset.write_text("rebuilt")
        stamp = previous[asset] + 1_000_000_000
        os.utime(asset, ns=(stamp, stamp))
        current = dev._snapshot(app_dir)
        assert current != previous
        assert current[entry] == previous[entry]
        previous = current


@pytest.mark.parametrize("file_target", [False, True], ids=["module", "file"])
def test_reload_recovers_after_import_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, file_target: bool) -> None:
    monkeypatch.chdir(tmp_path)
    entry = tmp_path / "app.py"
    entry.write_text(
        "from fleur import Component, Model, MsgGroup\n"
        "from fleur.ui import Text\n"
        "from labels import banner\n"
        "app = Component(init=Model(), update=MsgGroup.cases(), view=Text(banner))\n"
    )
    labels = tmp_path / "labels.py"
    labels.write_text("banner = 'first revision'\n")
    target = f"{entry}:app" if file_target else "app:app"
    broadcast = Mock()
    monkeypatch.setattr(dev, "_broadcast_reload", broadcast)
    monkeypatch.setattr(dev, "_current_html", "")

    dev._rebuild(target, tmp_path)
    first_html = dev._get_html()
    assert "first revision" in first_html
    broadcast.assert_called_once()

    labels.unlink()
    package = tmp_path / "labels"
    package.mkdir()
    exports = package / "__init__.py"
    exports.write_text("from .messages import banner\n")
    dev._rebuild(target, tmp_path)
    assert dev._get_html() == first_html
    broadcast.assert_called_once()

    (package / "messages.py").write_text("banner = 'second revision'\n")
    if not file_target:
        # The dotted entry point can itself move from a module to a package.
        (tmp_path / "app").mkdir()
        entry.rename(tmp_path / "app" / "__init__.py")
    dev._rebuild(target, tmp_path)
    assert "second revision" in dev._get_html()
    assert broadcast.call_count == 2


def test_dev_starts_server_and_watcher_after_initial_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "app.py").write_text("raise ImportError('incomplete edit')\n")
    thread, server = Mock(), Mock()
    monkeypatch.setattr(dev.threading, "Thread", thread)
    monkeypatch.setattr(dev, "_DevServer", server)
    monkeypatch.setattr(dev, "_current_html", "")
    command = dev.DevCommand()
    command(command.parser.parse_args(["app:app", "--reload-dir", str(tmp_path)]))

    assert "Waiting for a successful build" in dev._get_html()
    thread.return_value.start.assert_called_once()
    server.return_value.serve_forever.assert_called_once()
