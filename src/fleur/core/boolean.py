from fleur.js.ast import ESTreeUnaryExpression

from .expr import Expr, ensure_expr


class Boolean:
    @staticmethod
    def negate(
        condition: bool | Expr[bool],
    ) -> "Expr[bool]":
        return Expr[bool](
            ESTreeUnaryExpression(
                operator="!",
                prefix=True,
                argument=ensure_expr(condition),
            )
        )
