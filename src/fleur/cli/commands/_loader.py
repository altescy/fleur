from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import sys
from pathlib import Path
from typing import Any

_FILE_MODULE_NAME = "__fleur_module__"


def load_component(target: str) -> Any:
    """Load a component callable from a 'module:attribute' target string.

    Accepts either a dotted module name or a file path::

        load_component("myapp:app")
        load_component("path/to/app.py:app")
    """
    if ":" not in target:
        raise ValueError(f"Invalid target '{target}'. Use 'module:attribute' format, e.g. 'myapp:app'.")

    module_path, attr = target.rsplit(":", 1)

    p = Path(module_path)
    if p.suffix == ".py" or p.exists():
        p = p.with_suffix(".py") if not p.suffix else p
        spec = importlib.util.spec_from_file_location(_FILE_MODULE_NAME, p)
        if spec is None or not isinstance(spec.loader, importlib.abc.Loader):
            raise ImportError(f"Cannot load module from path: {p}")
        mod = importlib.util.module_from_spec(spec)
        mod.__name__ = _FILE_MODULE_NAME
        sys.modules[_FILE_MODULE_NAME] = mod
        spec.loader.exec_module(mod)
    else:
        if module_path in sys.modules:
            del sys.modules[module_path]
        mod = importlib.import_module(module_path)

    return getattr(mod, attr)
