import typing
from typing import Any, Optional, Union, overload

from .ir import (
    IRLiteralArrayExpr,
    IRLiteralBooleanExpr,
    IRLiteralNumberExpr,
    IRLiteralRecordExpr,
    IRLiteralStringExpr,
)
from .types import (
    Array,
    Boolean,
    BooleanLike,
    GraineType,
    Number,
    NumberLike,
    PyBooleanCompat,
    PyNumberCompat,
    PyStringCompat,
    Record,
    String,
    StringLike,
)


# More specific array types first
@overload
def as_literal(value: list[NumberLike]) -> Array[Number, IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]


@overload
def as_literal(value: list[StringLike]) -> Array[String, IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]


@overload
def as_literal(value: list[BooleanLike]) -> Array[Boolean, IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]


# Generic list/dict fallback
@overload
def as_literal(value: list) -> Array[GraineType, IRLiteralArrayExpr]: ...


@overload
def as_literal(value: dict) -> Record[GraineType, IRLiteralRecordExpr]: ...


# Scalar types - must come after list/dict to avoid overlap
@overload
def as_literal(value: PyStringCompat) -> String[IRLiteralStringExpr]: ...


@overload
def as_literal(value: PyBooleanCompat) -> Boolean[IRLiteralBooleanExpr]: ...  # pyright: ignore[reportOverlappingOverload]


@overload
def as_literal(value: PyNumberCompat) -> Number[IRLiteralNumberExpr]: ...  # pyright: ignore[reportOverlappingOverload]


def as_literal(value: Any) -> GraineType:
    if isinstance(value, GraineType):
        return value
    if isinstance(value, bool):
        return Boolean(IRLiteralNumberExpr(1 if value else 0))
    if isinstance(value, (int, float)):
        return Number(IRLiteralNumberExpr(value))
    if isinstance(value, str):
        return String(IRLiteralStringExpr(value))
    if isinstance(value, list):
        elements = [as_literal(elem)._expr for elem in value]
        return Array(IRLiteralArrayExpr(elements))
    if isinstance(value, dict):
        fields = {key: as_literal(val)._expr for key, val in value.items()}
        return Record(IRLiteralRecordExpr(fields))
    raise TypeError(f"Unsupported literal type: {type(value)}")


def extract_first_grainetype(annotation: Any) -> type[GraineType]:
    def _dfs(annotation: Any) -> Optional[type[GraineType]]:
        if isinstance(annotation, type) and issubclass(annotation, GraineType):
            return annotation
        origin = typing.get_origin(annotation)
        args = typing.get_args(annotation)
        # Check if origin is a GraineType (for Generic types like Array[Number])
        if origin is not None and isinstance(origin, type) and issubclass(origin, GraineType):
            return origin
        if origin is Union or str(origin) == "types.UnionType":
            for arg in args:
                res = _dfs(arg)
                if res is not None:
                    return res
        return None

    result = _dfs(annotation)
    if result is None:
        raise TypeError(f"No IRExpr type found in annotation: {annotation}")
    return result
