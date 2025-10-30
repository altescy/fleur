from collections.abc import Iterator
from types import TracebackType
from typing import Optional

from .ir import IRBlock, IRExpr, IRIdentifierExpr, IRIfStmt, IRRangeStmt
from .runtime import require_block, use_block
from .types import Boolean, Number


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


class When:
    """Represents a when clause in a cases statement."""

    def __init__(self, cases: "Cases", condition: Optional[Boolean] = None) -> None:
        self._cases = cases
        self._condition = condition._expr if condition is not None else None
        self._block_ctx = None

    def __enter__(self) -> None:
        # Start a new block context
        self._block_ctx = use_block()
        self._block = self._block_ctx.__enter__()

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # Exit the block context
        if self._block_ctx is not None:
            self._block_ctx.__exit__(exc_type, exc_val, exc_tb)
            # Register this when clause with the cases
            self._cases._add_when(self._condition, self._block)


class Cases:
    """Cases statement for conditional branching with multiple conditions."""

    def __init__(self) -> None:
        self._whens: list[tuple[Optional[IRExpr], "IRBlock"]] = []

    def __call__(self, condition: Boolean) -> When:
        """Create a when clause with a condition."""
        return When(self, condition)

    def default(self) -> When:
        """Create a default when clause (always true)."""
        return When(self, None)

    def _add_when(self, condition: Optional[IRExpr], body: "IRBlock") -> None:
        """Add a when clause to the cases."""
        self._whens.append((condition, body))

    def __enter__(self) -> "Cases":
        return self

    def __exit__(self, *args: object) -> None:
        """Build the if-else chain from all when clauses."""
        if not self._whens:
            return

        # Build nested if-else statements from the when clauses
        # First when becomes the outermost if
        # Subsequent whens become else-if (else { if { ... } })
        # Default when (condition=None) becomes the final else

        def build_if_chain(whens: list[tuple[Optional[IRExpr], "IRBlock"]]) -> Optional[IRIfStmt]:
            if not whens:
                return None

            condition, then_body = whens[0]
            remaining = whens[1:]

            if condition is None:
                # This is a default when - should not generate an if statement
                # Return None and let the caller use then_body as else_body
                return None

            # Build the else body from remaining whens
            else_body = None
            if remaining:
                next_if = build_if_chain(remaining)
                if next_if is not None:
                    # Wrap in a block
                    from .ir import IRBlock

                    else_body = IRBlock(body=[next_if])
                else:
                    # The remaining when was a default, use its body
                    if remaining and remaining[0][0] is None:
                        else_body = remaining[0][1]

            return IRIfStmt(
                condition=condition,
                then_body=then_body,
                else_body=else_body,
            )

        first_if = build_if_chain(self._whens)
        if first_if is not None:
            require_block().emit(first_if)
