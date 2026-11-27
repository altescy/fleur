import logging
import os

from fleur.cli import main

if os.environ.get("FLEUR_DEBUG"):
    LEVEL = logging.DEBUG
else:
    level_name: str = os.environ.get("FLEUR_LOG_LEVEL", "WARNING")
    LEVEL = logging._nameToLevel.get(level_name, logging.WARNING)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=LEVEL)


def run() -> None:
    main(prog="fleur")


if __name__ == "__main__":
    run()
