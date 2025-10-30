import typing
from typing import Any, Optional, Union, overload

from .ir import IRLiteralNumberExpr, IRLiteralStringExpr
from .types import (
    Boolean,
    GraineType,
    Number,
    PyBooleanCompat,
    PyGraineCompat,
    PyNumberCompat,
    PyStringCompat,
    String,
)


@overload
def as_literal(value: PyStringCompat) -> String: ...


@overload
def as_literal(value: PyBooleanCompat) -> Boolean: ...  # pyright: ignore[reportOverlappingOverload]


@overload
def as_literal(value: PyNumberCompat) -> Number: ...  # pyright: ignore[reportOverlappingOverload]


def as_literal(value: PyGraineCompat) -> GraineType:
    if isinstance(value, GraineType):
        return value
    if isinstance(value, bool):
        return Boolean(IRLiteralNumberExpr(1 if value else 0))
    if isinstance(value, (int, float)):
        return Number(IRLiteralNumberExpr(value))
    if isinstance(value, str):
        return String(IRLiteralStringExpr(value))
    raise TypeError(f"Unsupported literal type: {type(value)}")


def extract_first_grainetype(annotation: Any) -> type[GraineType]:
    def _dfs(annotation: Any) -> Optional[type[GraineType]]:
        if isinstance(annotation, type) and issubclass(annotation, GraineType):
            return annotation
        origin = typing.get_origin(annotation)
        args = typing.get_args(annotation)
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
