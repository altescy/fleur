from __future__ import annotations

import argparse
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

from .base import Subcommand


def _load_component(target: str) -> Any:
    """Load a component callable from 'module:attribute' target string."""
    if ":" not in target:
        raise ValueError(f"Invalid target '{target}'. Use 'module:attribute' format, e.g. 'myapp:App'.")

    module_path, attr = target.rsplit(":", 1)

    p = Path(module_path)
    if p.suffix == ".py" or p.exists():
        p = p.with_suffix(".py") if not p.suffix else p
        spec = importlib.util.spec_from_file_location("__fleur_build_module__", p)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from path: {p}")
        mod = importlib.util.module_from_spec(spec)
        mod.__name__ = "__fleur_build_module__"
        sys.modules["__fleur_build_module__"] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    else:
        if module_path in sys.modules:
            del sys.modules[module_path]
        mod = importlib.import_module(module_path)

    return getattr(mod, attr)


@Subcommand.register("build")
class BuildCommand(Subcommand):
    """Build a component to a self-contained HTML file."""

    def setup(self) -> None:
        self.parser.add_argument(
            "target",
            help="Component to build, in 'module:attribute' format (e.g. 'myapp:App' or 'path/to/app.py:App').",
        )
        self.parser.add_argument(
            "-o",
            "--output",
            default=None,
            metavar="FILE",
            help="Output file path. Defaults to stdout if not specified.",
        )

    def run(self, args: argparse.Namespace) -> None:
        import sys as _sys

        from fleur import bloom

        target: str = args.target
        output: str | None = args.output

        # Add cwd to sys.path so local modules can be imported
        cwd = str(Path.cwd())
        if cwd not in _sys.path:
            _sys.path.insert(0, cwd)

        try:
            component = _load_component(target)
        except Exception as exc:
            print(f"Error loading '{target}': {exc}", file=_sys.stderr)
            raise SystemExit(1) from exc

        try:
            html = bloom(component)
        except Exception as exc:
            print(f"Error building '{target}': {exc}", file=_sys.stderr)
            raise SystemExit(1) from exc

        if output:
            out = Path(output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
            print(f"Written to {out}")
        else:
            print(html, end="")
