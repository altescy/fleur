from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ._loader import load_component
from .base import Subcommand


@Subcommand.register("build")
class BuildCommand(Subcommand):
    """Build a component to a self-contained HTML file."""

    def setup(self) -> None:
        self.parser.add_argument(
            "target",
            help="Component to build, in 'module:attribute' format (e.g. 'myapp:app' or 'path/to/app.py:app').",
        )
        self.parser.add_argument(
            "-o",
            "--output",
            default=None,
            metavar="FILE",
            help="Output file path. Defaults to stdout if not specified.",
        )

    def run(self, args: argparse.Namespace) -> None:
        from fleur import bloom

        target: str = args.target
        output: str | None = args.output

        cwd = str(Path.cwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)

        try:
            component = load_component(target)
        except Exception as exc:
            print(f"Error loading '{target}': {exc}", file=sys.stderr)
            raise SystemExit(1) from exc

        try:
            html = bloom(component)
        except Exception as exc:
            print(f"Error building '{target}': {exc}", file=sys.stderr)
            raise SystemExit(1) from exc

        if output:
            out = Path(output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
            print(f"Written to {out}")
        else:
            print(html, end="")
