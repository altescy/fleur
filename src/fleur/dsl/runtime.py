from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from .ir import IRBlock

_CURRENT_BLOCK: ContextVar[IRBlock] = ContextVar("_CURRENT_BLOCK", default=IRBlock(body=[]))


def require_block() -> IRBlock:
    return _CURRENT_BLOCK.get()


@contextmanager
def use_block() -> Iterator[IRBlock]:
    block = IRBlock(body=[])
    token = _CURRENT_BLOCK.set(block)
    try:
        yield block
    finally:
        _CURRENT_BLOCK.reset(token)
