from collections.abc import Callable
from typing import Final, Optional, Union, cast

from .ast import (
    GraineArrayNode,
    GraineASTExpr,
    GraineCallNode,
    GraineForOfNode,
    GraineIdentifierNode,
    GraineIfNode,
    GrainePropertyAccessNode,
)
from .jit import _GraineBuilder, auto_let, ensure_graine, require_block, use_block
from .types import (
    GraineBooleanLikeType,
    GraineNumberType,
    GraineObject,
    GraineTypeS_co,
    GraineTypeT,
    GraineTypeT_co,
    GraineUndefinedType,
    PyNumberCompat,
)


@auto_let
def when(
    condition: GraineObject[GraineASTExpr[GraineBooleanLikeType]],
    /,
    *,
    then: GraineObject[GraineASTExpr[GraineTypeS_co]],
    otherwise: Optional[GraineObject[GraineASTExpr[GraineTypeT_co]]] = None,
) -> GraineObject[GraineIfNode[Union[GraineTypeS_co, GraineTypeT_co, GraineUndefinedType]]]:
    return cast(
        GraineObject[GraineIfNode[Union[GraineTypeS_co, GraineTypeT_co, GraineUndefinedType]]],
        _GraineBuilder(
            GraineIfNode(
                condition=condition.__graine_ast__,
                then_branch=then.__graine_ast__,
                else_branch=otherwise.__graine_ast__ if otherwise is not None else None,
            )
        ),
    )


def foreach(
    iterable: GraineObject[GraineArrayNode[GraineTypeT]],
    /,
) -> Callable[[Callable[[GraineObject[GraineASTExpr[GraineTypeT]]], None]], None]:
    def decorator(func: Callable[[GraineObject[GraineASTExpr[GraineTypeT]]], None]) -> None:
        block = require_block()
        var = cast(GraineObject, _GraineBuilder(block.new_identifier()))

        with use_block() as inner:
            func(var)

        block.emit(
            GraineForOfNode(
                variable=var.__graine_ast__,
                iterator=iterable.__graine_ast__,
                body=inner,
            )
        )

    return decorator


class math:
    _MATH_MODULE: Final = GraineIdentifierNode(name="Math")

    @auto_let
    @staticmethod
    def sqrt(
        value: Union[PyNumberCompat, GraineObject[GraineASTExpr[GraineNumberType]]],
    ) -> GraineObject[GraineASTExpr[GraineNumberType]]:
        value = ensure_graine(value)
        call_node = GraineCallNode(
            function=GrainePropertyAccessNode(
                property_name="sqrt",
                receiver=math._MATH_MODULE,
            ),
            arguments=[value.__graine_ast__],
        )
        return cast(GraineObject[GraineASTExpr[GraineNumberType]], _GraineBuilder(call_node))
