from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar, cast, overload

from fleur.js.ast import (
    ESTreeBinaryExpression,
    ESTreeConditionalExpression,
    ESTreeGeneratedIdentifier,
    ESTreeLogicalExpression,
    ESTreeReturnStatement,
)
from fleur.js.builder import call, function_expr, literal

from .expr import Expr, ValueRef, ensure_expr
from .types import FleurValue, FleurValueT, FleurValueU, ModelT

if TYPE_CHECKING:
    from .model import Model

_PresentT = TypeVar("_PresentT", bound=FleurValue)
# The implementation takes either form of callback; the overloads above are the contract.
_ArgT = TypeVar("_ArgT")


class Cond:
    # Model branches give a model instance, whose fields read as attributes. Models are also
    # FleurValues, so this overlaps the general overload; it comes first so that the checker
    # picks it for models, which is the intent.
    @overload
    @staticmethod
    def when(  # pyright: ignore[reportOverlappingOverload]
        condition: bool | Expr[bool],
        consequent: ModelT,
        alternate: ModelT,
    ) -> ModelT: ...

    @overload
    @staticmethod
    def when(
        condition: bool | Expr[bool],
        consequent: FleurValueT | Expr[FleurValueT],
        alternate: FleurValueU | Expr[FleurValueU],
    ) -> "Expr[FleurValueT | FleurValueU]": ...

    @staticmethod
    def when(
        condition: bool | Expr[bool],
        consequent: FleurValueT | Expr[FleurValueT],
        alternate: FleurValueU | Expr[FleurValueU],
    ) -> "Expr[FleurValueT | FleurValueU] | Model":
        return ValueRef(
            ESTreeConditionalExpression(
                test=ensure_expr(condition),
                consequent=ensure_expr(consequent),
                alternate=ensure_expr(alternate),
            )
        )

    @overload
    @staticmethod
    def when_some(  # pyright: ignore[reportOverlappingOverload]
        value: "Expr[ModelT | None]",
        then: Callable[[ModelT], FleurValueT | Expr[FleurValueT]],
        *,
        otherwise: FleurValueU | Expr[FleurValueU] = None,
    ) -> "Expr[FleurValueT | FleurValueU]": ...

    @overload
    @staticmethod
    def when_some(
        value: "Expr[_PresentT | None]",
        then: Callable[[Expr[_PresentT]], FleurValueT | Expr[FleurValueT]],
        *,
        otherwise: FleurValueU | Expr[FleurValueU] = None,
    ) -> "Expr[FleurValueT | FleurValueU]": ...

    @staticmethod
    def when_some(
        value: "Expr[_PresentT | None]",
        then: Callable[[_ArgT], FleurValueT | Expr[FleurValueT]],
        *,
        otherwise: FleurValueU | Expr[FleurValueU] = None,
    ) -> "Expr[FleurValueT | FleurValueU]":
        """Use the value when it is present, like Elm's `Maybe.map` with a default.

        `then` receives the value without `None`: a model as an instance of its model, whose fields
        read as attributes, and any other value as an expression. A missing value (`None` or
        `undefined`) gives `otherwise`. The value is evaluated once.
        """
        present = ESTreeGeneratedIdentifier()
        result = ensure_expr(then(cast(_ArgT, ValueRef(present))))
        body = ESTreeConditionalExpression(
            test=ESTreeBinaryExpression(operator="!=", left=present, right=literal(None)),
            consequent=result,
            alternate=ensure_expr(otherwise),
        )
        return ValueRef(call(function_expr([present], ESTreeReturnStatement(body)), value.__compile__()))

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
