from contextlib import ExitStack
from typing import Any, Optional

from typing_extensions import Self

from . import ast, graine, jit
from .javascript import emit_javascript

__all__ = ["graine", "parterre"]


class parterre:
    def __init__(self) -> None:
        self._stack = ExitStack()
        self._block: Optional[ast.GraineBlockNode] = None

    def __enter__(self) -> Self:
        self._stack.__enter__()
        self._stack.enter_context(jit.use_block())
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> Optional[bool]:
        self._block = jit.require_block()
        return self._stack.__exit__(exc_type, exc_value, traceback)

    def germinate(self) -> str:
        return emit_javascript(self._block or jit.require_block())
