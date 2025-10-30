from collections.abc import Callable
from typing import Any, TypeVar, Union, cast, overload

from ._utils import as_literal, extract_first_grainetype
from .ir import IRFunctionStmt, IRIdentifierExpr, IRLetStmt, IRLiteralNumberExpr, IRReturnStmt
from .javascript import emit_javascript
from .runtime import require_block, use_block
from .stdlib import Cases, Range
from .types import (
    Boolean,
    BooleanLike,
    Function,
    GraineType,
    Number,
    NumberLike,
    PyBooleanCompat,
    PyGraineCompat,
    PyNumberCompat,
    PyStringCompat,
    String,
    StringLike,
)

__all__ = ["graine", "emit_javascript", "require_block"]


_GraineCallable = TypeVar("_GraineCallable", bound=Callable[..., GraineType])


class graine:
    Number = Number
    Boolean = Boolean
    String = String

    BooleanLike = BooleanLike
    NumberLike = NumberLike
    StringLike = StringLike

    @overload
    @staticmethod
    def literal(value: PyStringCompat) -> String: ...

    @overload
    @staticmethod
    def literal(value: PyBooleanCompat) -> Boolean: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: PyNumberCompat) -> Number: ...  # pyright: ignore[reportOverlappingOverload]

    @staticmethod
    def literal(value: PyGraineCompat) -> GraineType:
        return as_literal(value)

    @overload
    @staticmethod
    def let(init: NumberLike, name: str = "v") -> Number: ...

    @overload
    @staticmethod
    def let(init: BooleanLike, name: str = "v") -> Boolean: ...

    @overload
    @staticmethod
    def let(init: StringLike, name: str = "v") -> String: ...

    @staticmethod
    def let(init: Any, name: str = "v") -> Any:
        block = require_block()
        idx = len(block.body)
        gtype = init if isinstance(init, GraineType) else graine.literal(init)
        var_name = f"{name}_{idx}"
        block.emit(IRLetStmt(name=var_name, value=gtype._expr))
        return type(gtype)(IRIdentifierExpr(var_name))

    @staticmethod
    def range(start: Union[int, float, Number], end: Union[int, float, Number]) -> Range:
        var_name = f"i_{len(require_block().body)}"
        start_expr = start._expr if isinstance(start, Number) else IRLiteralNumberExpr(start)
        end_expr = end._expr if isinstance(end, Number) else IRLiteralNumberExpr(end)
        return Range(var=var_name, start=start_expr, end=end_expr)

    @staticmethod
    def cases() -> Cases:
        return Cases()

    @staticmethod
    def function(fn: _GraineCallable) -> _GraineCallable:
        function = Function(name=fn.__name__, fn=fn)

        with use_block() as block:
            args = [extract_first_grainetype(type_)(IRIdentifierExpr(name)) for name, type_ in function.params]
            ret = fn(*args)
            if ret:
                block.emit(IRReturnStmt(value=ret._expr))

        require_block().emit(
            IRFunctionStmt(
                name=function.name,
                params=[name for name, _ in function.params],
                body=block,
            )
        )

        return cast(_GraineCallable, function)
