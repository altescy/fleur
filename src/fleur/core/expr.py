from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Generic, overload

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeBinaryExpression,
    ESTreeExpression,
    ESTreeMemberExpression,
    ESTreeUnaryExpression,
)
from fleur.js.builder import call, ident, json_expr, member_expr, object_expr
from fleur.types import ICompilable

from .types import FleurValue, FleurValueT, FleurValueT_co


def ensure_expr(value: FleurValue | ICompilable) -> "ESTreeExpression":
    if isinstance(value, ESTreeExpression):
        return value
    elif isinstance(value, ICompilable):
        node = value.__compile__()
        assert isinstance(node, ESTreeExpression), (
            f"Expected ICompilable to compile to ESTreeExpression, got {type(node)}"
        )
        return node
    if isinstance(value, Sequence) and not isinstance(value, str):
        return ESTreeArrayExpression(elements=[ensure_expr(elem) for elem in value])
    if isinstance(value, Mapping):
        return object_expr((key, ensure_expr(val)) for key, val in value.items())
    return json_expr(value)


class Expr(Generic[FleurValueT_co], ICompilable[ESTreeExpression]):
    def __init__(self, expr: ESTreeExpression) -> None:
        self._expr = expr

    def __compile__(self) -> ESTreeExpression:
        return self._expr

    def __bool__(self) -> bool:
        raise TypeError(
            "Fleur Expr cannot be used as a Python boolean; use Expr.when(condition, consequent, alternate)"
        )

    #
    # Binary operators
    #

    @overload
    def __add__(self: "Expr[int]", other: "int | Expr[int]") -> "Expr[int]": ...
    @overload
    def __add__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[int | float]": ...
    @overload
    def __add__(self: "Expr[str]", other: "int | float | str | Expr[int | float | str]") -> "Expr[str]": ...
    def __add__(self, other: "FleurValue | Expr") -> "Expr":
        return Expr(ESTreeBinaryExpression(operator="+", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __sub__(self: "Expr[int]", other: "int | Expr[int]") -> "Expr[int]": ...
    @overload
    def __sub__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[int | float]": ...
    def __sub__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[int | float]":
        return Expr(ESTreeBinaryExpression(operator="-", left=self.__compile__(), right=ensure_expr(other)))

    def __mul__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[int | float]":
        return Expr(ESTreeBinaryExpression(operator="*", left=self.__compile__(), right=ensure_expr(other)))

    def __truediv__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[int | float]":
        return Expr(ESTreeBinaryExpression(operator="/", left=self.__compile__(), right=ensure_expr(other)))

    def __mod__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[int | float]":
        return Expr(ESTreeBinaryExpression(operator="%", left=self.__compile__(), right=ensure_expr(other)))

    def eq(self, other: FleurValue) -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator="===", left=self.__compile__(), right=ensure_expr(other)))

    def ne(self, other: FleurValue) -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator="!=", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __lt__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[bool]": ...
    @overload
    def __lt__(self: "Expr[str]", other: "str | Expr[str]") -> "Expr[bool]": ...
    @overload
    def __lt__(self: "Expr[list[Any]]", other: "list[Any] | Expr[list[Any]]") -> "Expr[bool]": ...
    def __lt__(self, other: "FleurValue | Expr") -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator="<", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __le__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[bool]": ...
    @overload
    def __le__(self: "Expr[str]", other: "str | Expr[str]") -> "Expr[bool]": ...
    @overload
    def __le__(self: "Expr[list[Any]]", other: "list[Any] | Expr[list[Any]]") -> "Expr[bool]": ...
    def __le__(self, other: "FleurValue | Expr") -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator="<=", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __gt__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[bool]": ...
    @overload
    def __gt__(self: "Expr[str]", other: "str | Expr[str]") -> "Expr[bool]": ...
    @overload
    def __gt__(self: "Expr[list[Any]]", other: "list[Any] | Expr[list[Any]]") -> "Expr[bool]": ...
    def __gt__(self, other: "FleurValue | Expr") -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator=">", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __ge__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[bool]": ...
    @overload
    def __ge__(self: "Expr[str]", other: "str | Expr[str]") -> "Expr[bool]": ...
    @overload
    def __ge__(self: "Expr[list[Any]]", other: "list[Any] | Expr[list[Any]]") -> "Expr[bool]": ...
    def __ge__(self, other: "FleurValue | Expr") -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator=">=", left=self.__compile__(), right=ensure_expr(other)))

    def __len__(self: "Expr[Sequence]") -> "Expr[int]":
        return Expr[int](member_expr(self.__compile__(), "length"))

    #
    # Unary operators
    #

    def __neg__(self: "Expr[int | float]") -> "Expr[int | float]":
        return Expr(ESTreeUnaryExpression(operator="-", argument=self.__compile__(), prefix=True))

    def __pos__(self: "Expr[int | float]") -> "Expr[int | float]":
        return self

    def __invert__(self: "Expr[int]") -> "Expr[int]":
        return Expr(ESTreeUnaryExpression(operator="~", argument=self.__compile__(), prefix=True))

    def neg(self: "Expr[bool]") -> "Expr[bool]":
        return Expr(ESTreeUnaryExpression(operator="!", argument=self.__compile__(), prefix=True))

    #
    # Indexing and member access
    #

    def __getitem__(
        self: "Expr[Sequence[FleurValueT_co] | Mapping[str, FleurValueT_co]]", key: int | str | Expr[int | str]
    ) -> "Expr[FleurValueT_co]":
        return Expr[FleurValueT_co](
            ESTreeMemberExpression(
                object=self.__compile__(),
                property=ensure_expr(key),
                computed=True,
            )
        )

    def has(self: "Expr[Mapping[str, Any]]", key: str | Expr[str]) -> "Expr[bool]":
        return Expr[bool](call(member_expr(self.__compile__(), "hasOwnProperty"), ensure_expr(key)))

    #
    # Sequence methods
    #

    def includes(self: "Expr[FleurValueT]", substring: FleurValueT | Expr[FleurValueT]) -> "Expr[bool]":
        return Expr[bool](call(member_expr(self.__compile__(), "includes"), ensure_expr(substring)))

    def update_at(
        self: "Expr[Sequence[FleurValueT]]",
        index: int | Expr[int],
        value: FleurValueT | Expr[FleurValueT],
    ) -> "Expr[FleurValueT_co]":
        return Expr[FleurValueT_co](
            call(member_expr(self.__compile__(), "with"), ensure_expr(index), ensure_expr(value))
        )

    #
    # Number methods
    #

    @overload
    def abs(self: "Expr[int]") -> "Expr[int]": ...
    @overload
    def abs(self: "Expr[float]") -> "Expr[float]": ...
    def abs(self: "Expr[int | float]") -> "Expr[int | float]":
        return Expr[int | float](call(member_expr(ident("Math"), "abs"), self.__compile__()))

    def floor(self: "Expr[int | float]") -> "Expr[int]":
        return Expr[int](call(member_expr(ident("Math"), "floor"), self.__compile__()))

    def ceil(self: "Expr[int | float]") -> "Expr[int]":
        return Expr[int](call(member_expr(ident("Math"), "ceil"), self.__compile__()))

    def round(self: "Expr[int | float]") -> "Expr[int]":
        return Expr[int](call(member_expr(ident("Math"), "round"), self.__compile__()))

    def sign(self: "Expr[int | float]") -> "Expr[int]":
        return Expr[int](call(member_expr(ident("Math"), "sign"), self.__compile__()))

    #
    # String methods
    #

    def lower(self: "Expr[str]") -> "Expr[str]":
        return Expr[str](call(member_expr(self.__compile__(), "toLowerCase")))

    def upper(self: "Expr[str]") -> "Expr[str]":
        return Expr[str](call(member_expr(self.__compile__(), "toUpperCase")))

    def trim(self: "Expr[str]") -> "Expr[str]":
        return Expr[str](call(member_expr(self.__compile__(), "trim")))

    def split(self: "Expr[str]", separator: FleurValue | Expr) -> "Expr[list[str]]":
        return Expr[list[str]](call(member_expr(self.__compile__(), "split"), ensure_expr(separator)))
