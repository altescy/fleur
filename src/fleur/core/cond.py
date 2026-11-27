from fleur.js.ast import (
    ESTreeBinaryExpression,
    ESTreeConditionalExpression,
    ESTreeLogicalExpression,
)

from .expr import Expr, ensure_expr
from .types import FleurValue, FleurValueT, FleurValueU


class Cond:
    @staticmethod
    def when(
        condition: bool | Expr[bool],
        consequent: FleurValueT | Expr[FleurValueT],
        alternate: FleurValueU | Expr[FleurValueU],
    ) -> "Expr[FleurValueT | FleurValueU]":
        return Expr[FleurValueT | FleurValueU](
            ESTreeConditionalExpression(
                test=ensure_expr(condition),
                consequent=ensure_expr(consequent),
                alternate=ensure_expr(alternate),
            )
        )

    @staticmethod
    def some(
        *conditions: bool | Expr[bool],
    ) -> "Expr[bool]":
        if not conditions:
            return Expr[bool](ensure_expr(False))

        expr = ensure_expr(conditions[0])
        for condition in conditions[1:]:
            expr = ESTreeLogicalExpression(operator="||", left=expr, right=ensure_expr(condition))
        return Expr[bool](expr)

    @staticmethod
    def every(
        *conditions: bool | Expr[bool],
    ) -> "Expr[bool]":
        if not conditions:
            return Expr[bool](ensure_expr(True))

        expr = ensure_expr(conditions[0])
        for condition in conditions[1:]:
            expr = ESTreeLogicalExpression(operator="&&", left=expr, right=ensure_expr(condition))
        return Expr[bool](expr)

    @staticmethod
    def equal(
        left: FleurValue | Expr[FleurValue],
        right: FleurValue | Expr[FleurValue],
    ) -> "Expr[bool]":
        """Compare strictly, except that comparing with `None` also matches a missing (`undefined`) value."""
        return Expr[bool](
            ESTreeBinaryExpression(
                operator="==" if left is None or right is None else "===",
                left=ensure_expr(left),
                right=ensure_expr(right),
            )
        )

    @staticmethod
    def not_equal(
        left: FleurValue | Expr[FleurValue],
        right: FleurValue | Expr[FleurValue],
    ) -> "Expr[bool]":
        """Negation of `Cond.equal`, so a missing value also counts as `None`."""
        return Expr[bool](
            ESTreeBinaryExpression(
                operator="!=" if left is None or right is None else "!==",
                left=ensure_expr(left),
                right=ensure_expr(right),
            )
        )
