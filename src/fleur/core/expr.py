from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Generic, overload

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeBinaryExpression,
    ESTreeExpression,
    ESTreeMemberExpression,
    ESTreeUnaryExpression,
)
from fleur.js.builder import call, ident, json_expr, member_expr, object_expr
from fleur.types import ICompilable

from .function import Function
from .types import FleurValue, FleurValueT, FleurValueT_co, KeyT, ModelT

if TYPE_CHECKING:
    from .model import Model


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
            "Fleur Expr cannot be used as a Python boolean; use Cond.when(condition, consequent, alternate)"
        )

    def __format__(self, format_spec: str) -> str:
        raise TypeError(
            "Fleur Expr cannot be formatted into a Python string, which is built before the page runs; "
            'join text with `+`, as in "Count: " + model.count'
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
    def __add__(self, other: "FleurValue | Expr[FleurValue]") -> "Expr[FleurValue]":
        return Expr(ESTreeBinaryExpression(operator="+", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __radd__(self: "Expr[int]", other: "int | Expr[int]") -> "Expr[int]": ...
    @overload
    def __radd__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[int | float]": ...
    @overload
    def __radd__(self: "Expr[str]", other: "int | float | str | Expr[int | float | str]") -> "Expr[str]": ...
    @overload
    def __radd__(self: "Expr[int | float]", other: str) -> "Expr[str]": ...
    def __radd__(self, other: "FleurValue | Expr[FleurValue]") -> "Expr[FleurValue]":
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
    def __lt__(self, other: "FleurValue | Expr[FleurValue]") -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator="<", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __le__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[bool]": ...
    @overload
    def __le__(self: "Expr[str]", other: "str | Expr[str]") -> "Expr[bool]": ...
    @overload
    def __le__(self: "Expr[list[Any]]", other: "list[Any] | Expr[list[Any]]") -> "Expr[bool]": ...
    def __le__(self, other: "FleurValue | Expr[FleurValue]") -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator="<=", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __gt__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[bool]": ...
    @overload
    def __gt__(self: "Expr[str]", other: "str | Expr[str]") -> "Expr[bool]": ...
    @overload
    def __gt__(self: "Expr[list[Any]]", other: "list[Any] | Expr[list[Any]]") -> "Expr[bool]": ...
    def __gt__(self, other: "FleurValue | Expr[FleurValue]") -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator=">", left=self.__compile__(), right=ensure_expr(other)))

    @overload
    def __ge__(self: "Expr[int | float]", other: "int | Expr[int | float]") -> "Expr[bool]": ...
    @overload
    def __ge__(self: "Expr[str]", other: "str | Expr[str]") -> "Expr[bool]": ...
    @overload
    def __ge__(self: "Expr[list[Any]]", other: "list[Any] | Expr[list[Any]]") -> "Expr[bool]": ...
    def __ge__(self, other: "FleurValue | Expr[FleurValue]") -> "Expr[bool]":
        return Expr[bool](ESTreeBinaryExpression(operator=">=", left=self.__compile__(), right=ensure_expr(other)))

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

    # A model item is returned as an instance of its model, whose fields read as attributes.
    # Models are also FleurValues, so these overlap the general overloads below; they come first
    # so that the checker picks them for model items, which is the intent.
    @overload
    def __getitem__(  # pyright: ignore[reportOverlappingOverload]
        self: "Expr[Sequence[ModelT]]", key: int | Expr[int]
    ) -> ModelT: ...

    @overload
    def __getitem__(  # pyright: ignore[reportOverlappingOverload]
        self: "Expr[Mapping[KeyT, ModelT]]", key: KeyT | Expr[KeyT]
    ) -> ModelT: ...

    @overload
    def __getitem__(
        self: "Expr[Sequence[FleurValueT]]",
        key: int | Expr[int],
    ) -> "Expr[FleurValueT]": ...

    @overload
    def __getitem__(
        self: "Expr[Mapping[KeyT, FleurValueT]]",
        key: KeyT | Expr[KeyT],
    ) -> "Expr[FleurValueT]": ...

    def __getitem__(
        self: "Expr[Sequence[FleurValueT] | Mapping[str, FleurValueT]]",
        key: int | str | Expr[int | str],
    ) -> "Expr[FleurValueT] | Model":
        """Read an item or key that is known to exist.

        Like `dict[key]` in Python, the result type assumes the item is present. Use `Object.get`
        or `Array.get` for a lookup that may miss; they return `None` instead. Read a field of a
        model value, such as a list item, as an attribute: `todo.title`.
        """
        return ValueRef(ESTreeMemberExpression(object=self.__compile__(), property=ensure_expr(key), computed=True))

    #
    # Function
    #
    def __call__(self: "Expr[Function[..., FleurValueT]]", *args: FleurValue | Expr[FleurValue]) -> "Expr[FleurValueT]":
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


class ValueRef(Expr[Any]):
    """An expression for a value whose fields are read as attributes, such as a model list item.

    The type checker sees such a value as an instance of its model, so `todo.title` is an
    `Expr[str]` and a misspelled field is a type error; at runtime each attribute becomes a
    JavaScript member access. Names starting with `_` are left to Python.
    """

    def __getattr__(self, name: str) -> "ValueRef":
        if name.startswith("_"):
            raise AttributeError(name)
        return ValueRef(member_expr(self.__compile__(), name))
