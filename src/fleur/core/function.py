import dataclasses
import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, ParamSpec, TypeVar, cast

from fleur.js.ast import (
    ESTreeFunctionBody,
    ESTreeFunctionExpression,
    ESTreeGeneratedIdentifier,
    ESTreeIdentifier,
    ESTreeReturnStatement,
)

from .types import FleurValue

if TYPE_CHECKING:
    from .expr import Expr


P = ParamSpec("P")
R = TypeVar("R", bound=FleurValue)


@dataclasses.dataclass
class Function(Generic[P, R]):
    name: str
    ast: ESTreeFunctionExpression

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> "Expr[R]":
        from .expr import Expr

        expr = Expr(ESTreeIdentifier(self.name))
        return cast(Expr[R], expr(*args, **kwargs))  # pyright: ignore[reportCallIssue, reportArgumentType]


def function(fn: Callable[P, "R | Expr[R]"]) -> Function[P, R]:
    from .expr import Expr, ValueRef, ensure_expr

    name = fn.__name__
    sig = inspect.signature(fn)
    params: list[ESTreeIdentifier] = []

    for param in sig.parameters.values():
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
            params.append(ESTreeGeneratedIdentifier())
        else:
            raise TypeError(f"Unsupported parameter kind {param.kind} in function {name}")

    # Arguments read fields as attributes, so a model item can be typed as the model itself.
    result = cast("FleurValue | Expr[FleurValue]", fn(*map(ValueRef, params)))  # pyright: ignore[reportCallIssue]

    if isinstance(result, Expr):
        result_ast = result.__compile__()
    else:
        result_ast = ensure_expr(result)

    return Function(
        name=fn.__name__,
        ast=ESTreeFunctionExpression(
            id=ESTreeIdentifier(fn.__name__),
            params=params,
            body=ESTreeFunctionBody([ESTreeReturnStatement(result_ast)]),
        ),
    )
