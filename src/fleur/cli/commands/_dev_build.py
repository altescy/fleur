"""Build one dev-server revision in a fresh interpreter."""

import sys
from pathlib import Path

from fleur import bloom

from ._loader import load_component

if __name__ == "__main__":
    target, watch_dir, output = sys.argv[1:]
    sys.path.insert(0, watch_dir)
    Path(output).write_text(bloom(load_component(target)), encoding="utf-8")
