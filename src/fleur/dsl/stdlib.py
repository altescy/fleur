from collections.abc import Iterator

from .ir import IRExpr, IRIdentifierExpr, IRRangeStmt
from .runtime import require_block, use_block
from .types import Number


class Range:
    def __init__(self, var: str, start: IRExpr, end: IRExpr) -> None:
        self._var = var
        self._start = start
        self._end = end

    def __iter__(self) -> Iterator[Number]:
        block = require_block()
        with use_block() as inner:
            yield Number(IRIdentifierExpr(self._var))
        block.body.append(
            IRRangeStmt(
                var=self._var,
                start=self._start,
                end=self._end,
                body=inner,
            )
        )
