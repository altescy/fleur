import argparse

from fleur.cli.commands import build, dev
from fleur.cli.commands.base import Subcommand
from fleur.version import VERSION

__all__ = ["create_cli", "build", "dev", "main"]


def create_cli(prog: str | None = None) -> Subcommand:
    parser = argparse.ArgumentParser(usage="%(prog)s", prog=prog)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + VERSION,
    )
    return Subcommand(parser)


def main(prog: str | None = None) -> None:
    app = create_cli(prog)
    app()
