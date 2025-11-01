from collections.abc import Callable
from typing import Final, Optional, Union, cast

from .ast import (
    GraineASTExpr,
    GraineBinaryOpNode,
    GraineCallNode,
    GraineConditionalNode,
    GraineForOfNode,
    GraineIdentifierNode,
    GraineIfNode,
    GrainePropertyAccessNode,
    GraineReturnNode,
)
from .jit import _GraineBuilder, auto_let, ensure_graine, require_block, use_block
from .types import (
    GraineArrayType,
    GraineBooleanLikeType,
    GraineBooleanType,
    GraineNumberType,
    GraineObject,
    GraineStringType,
    GraineType,
    GraineTypeS_co,
    GraineTypeT,
    GraineTypeT_co,
    GraineUndefinedType,
    PyNumberCompat,
)


def case(
    condition: GraineObject[GraineASTExpr[GraineBooleanLikeType]],
) -> Callable[[Callable], None]:
    def decorator(func: Callable) -> None:
        block = require_block()
        with use_block() as inner:
            ret = func()
            if ret is not None:
                inner.emit(GraineReturnNode(value=ret.__graine_ast__))
        block.emit(
            GraineIfNode(
                condition=condition.__graine_ast__,
                then_branch=inner,
            )
        )

    return decorator


@auto_let
def when(
    condition: GraineObject[GraineASTExpr[GraineBooleanLikeType]],
    /,
    *,
    then: GraineObject[GraineASTExpr[GraineTypeS_co]],
    otherwise: Optional[GraineObject[GraineASTExpr[GraineTypeT_co]]] = None,
) -> GraineObject[GraineConditionalNode[Union[GraineTypeS_co, GraineTypeT_co, GraineUndefinedType]]]:
    return cast(
        GraineObject[GraineConditionalNode[Union[GraineTypeS_co, GraineTypeT_co, GraineUndefinedType]]],
        _GraineBuilder(
            GraineConditionalNode(
                condition=condition.__graine_ast__,
                then_branch=then.__graine_ast__,
                else_branch=otherwise.__graine_ast__ if otherwise is not None else None,
            )
        ),
    )


@auto_let
def instanceof(
    instance: GraineObject[GraineASTExpr[GraineTypeT]],
    cls: Union[type, GraineObject[GraineIdentifierNode]],
) -> GraineObject[GraineBinaryOpNode[GraineBooleanType]]:
    assert isinstance(cls, _GraineBuilder)
    cls_ast = cls.__graine_ast__
    return cast(
        GraineObject[GraineBinaryOpNode[GraineBooleanType]],
        _GraineBuilder(
            GraineBinaryOpNode(
                op="instanceof",
                left=instance.__graine_ast__,
                right=cls_ast,
            )
        ),
    )


@auto_let
def typeof(
    instance: GraineObject[GraineASTExpr[GraineTypeT]],
) -> GraineObject[GraineASTExpr[GraineStringType]]:
    typeof_node = GraineCallNode(
        function=GraineIdentifierNode(name="typeof"),
        arguments=[instance.__graine_ast__],
    )
    return cast(
        GraineObject[GraineASTExpr[GraineStringType]],
        _GraineBuilder(typeof_node),
    )


def foreach(
    iterable: GraineObject[GraineASTExpr[GraineArrayType]],
    /,
) -> Callable[[Callable[[GraineObject[GraineASTExpr[GraineType]]], None]], None]:
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
