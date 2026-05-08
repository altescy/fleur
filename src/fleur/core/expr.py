from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, Generic, cast, overload

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeBinaryExpression,
    ESTreeExpression,
    ESTreeMemberExpression,
    ESTreeUnaryExpression,
)
from fleur.js.builder import call, ident, json_expr, member_expr, object_expr
from fleur.types import ICompilable

from .function import Function, function
from .types import FleurValue, FleurValueT, FleurValueT_co, FleurValueU


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
    if isinstance(value, Function):
        return ident(value.name)
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
    def __radd__(self: "Expr[int]", other: "int | Expr[int]") -> "Expr[int]": ...
    @overload
    def __radd__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[int | float]": ...
    @overload
    def __radd__(self: "Expr[str]", other: "int | float | str | Expr[int | float | str]") -> "Expr[str]": ...
    @overload
    def __radd__(self, other: "FleurValue | Expr") -> "Expr": ...
    def __radd__(self, other: "FleurValue | Expr") -> "Expr":
        return Expr(ESTreeBinaryExpression(operator="+", left=ensure_expr(other), right=self.__compile__()))

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

    #
    # Indexing and member access
    #

    def __getitem__(
        self: "Expr[Sequence[FleurValueT] | Mapping[str, FleurValueT]]",
        key: int | str | Expr[int | str],
    ) -> "Expr[FleurValueT]":
        return Expr(
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

    def concat(
        self: "Expr[Sequence[FleurValueT]]",
        *sequences: Sequence[FleurValueT | Expr[FleurValueT]] | Expr[Sequence[FleurValueT]],
    ) -> "Expr[Sequence[FleurValueT]]":
        expr = self.__compile__()
        for seq in sequences:
            seq = cast(Expr | FleurValue, seq)
            expr = call(member_expr(expr, "concat"), seq.__compile__() if isinstance(seq, Expr) else ensure_expr(seq))
        return Expr[Sequence[FleurValueT]](expr)

    def map(
        self: "Expr[Sequence[FleurValueT]]",
        fn: Function[[Expr[FleurValueT]], FleurValueU] | Callable[[Expr[FleurValueT]], FleurValueU | Expr[FleurValueU]],
    ) -> "Expr[Sequence[FleurValueU]]":
        if not isinstance(fn, Function):
            fn = function(fn)
        return Expr(call(member_expr(self.__compile__(), "map"), fn.ast))

    def filter(
        self: "Expr[Sequence[FleurValueT]]",
        fn: Function[[Expr[FleurValueT]], bool] | Callable[[Expr[FleurValueT]], bool | Expr[bool]],
    ) -> "Expr[Sequence[FleurValueT]]":
        if not isinstance(fn, Function):
            fn = function(fn)
        return Expr(call(member_expr(self.__compile__(), "filter"), fn.ast))

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

    #
    # Object methods
    #
    def keys(self: "Expr[Mapping[str, Any]]") -> "Expr[Sequence[str]]":
        return Expr[Sequence[str]](call(member_expr(ident("Object"), "keys"), self.__compile__()))

    def values(self: "Expr[Mapping[str, FleurValueT]]") -> "Expr[Sequence[FleurValueT]]":
        return Expr[Sequence[FleurValueT]](call(member_expr(ident("Object"), "values"), self.__compile__()))

    def entries(self: "Expr[Mapping[str, FleurValueT]]") -> "Expr[Sequence[tuple[str, FleurValueT]]]":
        return Expr[Sequence[tuple[str, FleurValueT]]](
            call(member_expr(ident("Object"), "entries"), self.__compile__())
        )

    def assign(
        self: "Expr[Mapping[str, FleurValueT]]",
        *sources: Mapping[str, FleurValueT] | Expr[Mapping[str, FleurValueT]],
    ) -> "Expr[Mapping[str, FleurValueT]]":
        expr = self.__compile__()
        for source in sources:
            source_expr = ensure_expr(source)
            expr = call(member_expr(ident("Object"), "assign"), expr, source_expr)
        return Expr[Mapping[str, FleurValueT]](expr)

    #
    # Function
    #
    def __call__(self: "Expr[Function[..., FleurValueT]]", *args: FleurValue | Expr) -> "Expr[FleurValueT]":
        return Expr(call(self.__compile__(), *(ensure_expr(arg) for arg in args)))


def boolean(value: bool) -> Expr[bool]:
    return Expr(json_expr(value))


def number(value: int | float) -> Expr[int | float]:
    return Expr(json_expr(value))


def string(value: str) -> Expr[str]:
    return Expr(json_expr(value))


def array(value: Sequence[FleurValueT | Expr[FleurValueT]]) -> Expr[Sequence[FleurValueT]]:
    exprs = [ensure_expr(elem) for elem in value]
    return Expr(ESTreeArrayExpression(elements=exprs))


def record(value: Mapping[str, FleurValueT | Expr[FleurValueT]]) -> Expr[Mapping[str, FleurValueT]]:
    properties = ((key, ensure_expr(val)) for key, val in value.items())
    return Expr(object_expr(properties))
