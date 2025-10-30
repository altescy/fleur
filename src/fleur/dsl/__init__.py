from collections.abc import Callable
from contextlib import ExitStack
from typing import Any, Final, Optional, TypeVar, Union, overload

from typing_extensions import Self

from ._utils import as_literal
from .ir import (
    IRBlock,
    IRExpr,
    IRIdentifierExpr,
    IRLetStmt,
    IRLiteralArrayExpr,
    IRLiteralBooleanExpr,
    IRLiteralNumberExpr,
    IRLiteralRecordExpr,
    IRLiteralStringExpr,
)
from .javascript import emit_javascript
from .jit import Cases, Range, define_class, define_function
from .runtime import require_block, use_block
from .stdlib import Math
from .types import (
    Array,
    ArrayElementT,
    ArrayExprT,
    ArrayLike,
    Boolean,
    BooleanLike,
    GraineType,
    Number,
    NumberLike,
    PyBooleanCompat,
    PyNumberCompat,
    PyStringCompat,
    Record,
    RecordExprT,
    RecordLike,
    RecordValueT,
    String,
    StringLike,
)

__all__ = ["graine", "parterre"]


def _make_array_from_elements(elements: list[Any]) -> Array[GraineType, IRLiteralArrayExpr]:
    """Helper to create Array from elements with proper type inference."""
    element_exprs = [as_literal(elem)._expr for elem in elements]
    return Array(IRLiteralArrayExpr(element_exprs))


def _make_record_from_fields(fields: dict[str, Any]) -> Record[GraineType, IRLiteralRecordExpr]:
    """Helper to create Record from fields with proper type inference."""
    field_exprs = {key: as_literal(val)._expr for key, val in fields.items()}
    return Record(IRLiteralRecordExpr(field_exprs))


_ClassT = TypeVar("_ClassT", bound=type)
_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])
_GraineCallableT = TypeVar("_GraineCallableT", bound=Callable[..., Optional[GraineType]])
_ElementT = TypeVar("_ElementT")  # For Array element types


class _GraineProperty(property):
    """Custom property class that can hold graine-specific metadata."""

    def __init__(self, fget: Callable[..., Any]) -> None:
        super().__init__(fget)
        self._graine_getter = True
        self._graine_original_method = fget


class graine:
    Number = Number
    Boolean = Boolean
    String = String
    Array = Array
    Record = Record

    BooleanLike = BooleanLike
    NumberLike = NumberLike
    StringLike = StringLike
    ArrayLike = ArrayLike
    RecordLike = RecordLike

    math: Final = Math

    # Array types
    @overload
    @staticmethod
    def literal(value: list[PyNumberCompat]) -> Array[Number[IRLiteralNumberExpr], IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: list[PyStringCompat]) -> Array[String[IRLiteralStringExpr], IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: list[PyBooleanCompat]) -> Array[Boolean[IRLiteralBooleanExpr], IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Record types
    @overload
    @staticmethod
    def literal(value: dict[str, PyNumberCompat]) -> Record[Number[IRLiteralNumberExpr], IRLiteralRecordExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: dict[str, PyStringCompat]) -> Record[String[IRLiteralStringExpr], IRLiteralRecordExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: dict[str, PyBooleanCompat]) -> Record[Boolean[IRLiteralBooleanExpr], IRLiteralRecordExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Generic list/dict fallback
    @overload
    @staticmethod
    def literal(value: list) -> Array[GraineType, IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: dict) -> Record[GraineType, IRLiteralRecordExpr]: ...

    # Scalar types - must come after list/dict to avoid overlap
    @overload
    @staticmethod
    def literal(value: PyStringCompat) -> String[IRLiteralStringExpr]: ...

    @overload
    @staticmethod
    def literal(value: PyBooleanCompat) -> Boolean[IRLiteralBooleanExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: PyNumberCompat) -> Number[IRLiteralNumberExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @staticmethod
    def literal(value: Any) -> GraineType:
        return as_literal(value)

    # Primitive types
    @overload
    @staticmethod
    def let(init: NumberLike, name: str = "v") -> Number[IRIdentifierExpr]: ...

    @overload
    @staticmethod
    def let(init: BooleanLike, name: str = "v") -> Boolean[IRIdentifierExpr]: ...

    @overload
    @staticmethod
    def let(init: StringLike, name: str = "v") -> String[IRIdentifierExpr]: ...

    @overload
    @staticmethod
    def let(init: list[NumberLike], name: str = "v") -> Array[Number, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def let(init: list[StringLike], name: str = "v") -> Array[String, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def let(init: list[BooleanLike], name: str = "v") -> Array[Boolean, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Array with Graine types
    @overload
    @staticmethod
    def let(init: Array[ArrayElementT, ArrayExprT], name: str = "v") -> Array[ArrayElementT, IRIdentifierExpr]: ...

    # Generic array fallback
    @overload
    @staticmethod
    def let(init: list, name: str = "v") -> Array[GraineType, IRIdentifierExpr]: ...

    # Record types - specific value types
    @overload
    @staticmethod
    def let(init: dict[str, NumberLike], name: str = "v") -> Record[Number, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def let(init: dict[str, StringLike], name: str = "v") -> Record[String, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def let(init: dict[str, BooleanLike], name: str = "v") -> Record[Boolean, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Record with Graine types
    @overload
    @staticmethod
    def let(init: Record[RecordValueT, RecordExprT], name: str = "v") -> Record[RecordValueT, IRIdentifierExpr]: ...

    # Generic record fallback
    @overload
    @staticmethod
    def let(init: dict, name: str = "v") -> Record[GraineType, IRIdentifierExpr]: ...

    @staticmethod
    def let(init: Any, name: str = "v") -> Any:
        block = require_block()
        idx = len(block.body)
        gtype = init if isinstance(init, GraineType) else graine.literal(init)

        # Special case: If init is a ClassWrapper instance (has _graine_class),
        # and it already has an IRIdentifierExpr, just return it
        # This avoids double-wrapping class instances
        if (
            hasattr(type(gtype), "_graine_class")
            and isinstance(gtype._expr, IRIdentifierExpr)
            and gtype._expr.name.startswith("_")
        ):
            return gtype

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

    # Array creation with type tracking
    @overload
    @staticmethod
    def array(elements: list[NumberLike]) -> Array[Number, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def array(elements: list[StringLike]) -> Array[String, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def array(elements: list[BooleanLike]) -> Array[Boolean, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Generic fallback
    @overload
    @staticmethod
    def array(elements: list) -> Array[GraineType, IRLiteralArrayExpr]: ...

    @staticmethod
    def array(elements: list) -> Any:  # pyright: ignore[reportInconsistentOverload]
        return _make_array_from_elements(elements)

    # Record creation with type tracking
    @overload
    @staticmethod
    def record(fields: dict[str, NumberLike]) -> Record[Number, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def record(fields: dict[str, StringLike]) -> Record[String, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def record(fields: dict[str, BooleanLike]) -> Record[Boolean, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Generic fallback
    @overload
    @staticmethod
    def record(fields: dict) -> Record[GraineType, IRLiteralRecordExpr]: ...

    @staticmethod
    def record(fields: dict) -> Any:  # pyright: ignore[reportInconsistentOverload]
        return _make_record_from_fields(fields)

    @overload
    @staticmethod
    def define(fn_or_class: _ClassT) -> _ClassT: ...

    @overload
    @staticmethod
    def define(fn_or_class: _GraineCallableT) -> _GraineCallableT: ...

    @staticmethod
    def define(fn_or_class: Union[type, Callable]) -> Union[type, Callable]:
        """Decorator to define a Graine function or class that transpiles to JavaScript."""
        if isinstance(fn_or_class, type):
            return define_class(fn_or_class)
        else:
            return define_function(fn_or_class)

    @staticmethod
    def static(fn: _CallableT) -> _CallableT:
        """Decorator to mark a method as static."""
        fn._graine_static = True  # type: ignore[attr-defined]
        return fn

    @staticmethod
    def getter(fn: Callable[..., Any]) -> _GraineProperty:
        """Decorator to mark a method as a getter.

        Returns a property object so that type checkers recognize it as a property,
        but stores the original method for code generation.
        """
        return _GraineProperty(fn)


class parterre:
    def __init__(self) -> None:
        self._stack = ExitStack()
        self._block: Optional[IRBlock] = None

    def __enter__(self) -> Self:
        self._stack.__enter__()
        self._stack.enter_context(use_block())
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> Optional[bool]:
        self._block = require_block()
        return self._stack.__exit__(exc_type, exc_value, traceback)

    def germinate(self) -> str:
        return emit_javascript(self._block or require_block())
