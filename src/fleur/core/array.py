from collections.abc import Callable, Sequence
from typing import TypeVar, cast, overload

from fleur.js.ast import ESTreeLogicalExpression
from fleur.js.builder import call, literal, member_expr

from .expr import Expr, ensure_expr
from .function import Function, function
from .runtime import runtime_call
from .types import FleurValue, FleurValueT, FleurValueU

_SortKeyT = TypeVar("_SortKeyT", int, float, str)


class Array:
    @staticmethod
    def get(array: Expr[Sequence[FleurValueT]], index: int | Expr[int]) -> Expr[FleurValueT | None]:
        """Read an item that may be out of range, counting negative indices from the end.

        `array[index]` assumes that the item exists. This returns `None` outside the array.
        """
        item = call(member_expr(array.__compile__(), "at"), ensure_expr(index))
        return Expr(ESTreeLogicalExpression(operator="??", left=item, right=literal(None)))

    @staticmethod
    def length(array: Expr[Sequence[FleurValueT]]) -> Expr[int]:
        """Read the number of items in a browser array."""
        return Expr(member_expr(array.__compile__(), "length"))

    @staticmethod
    def join(array: Expr[Sequence[str]], separator: str | Expr[str] = ",") -> Expr[str]:
        """Join a browser array of strings with a separator."""
        return Expr(call(member_expr(array.__compile__(), "join"), ensure_expr(separator)))

    @overload
    @staticmethod
    def sum(array: Expr[Sequence[int]]) -> Expr[int]: ...

    @overload
    @staticmethod
    def sum(array: Expr[Sequence[int | float]]) -> Expr[int | float]: ...

    @staticmethod
    def sum(array: Expr[Sequence[int | float]]) -> Expr[int | float]:
        """Add the numbers in a browser array, using zero for an empty array."""

        def add(total: Expr[int | float], value: Expr[int | float]) -> Expr[int | float]:
            return total + value

        return Expr(call(member_expr(array.__compile__(), "reduce"), function(add).ast, literal(0)))

    @staticmethod
    def map(
        array: "Expr[Sequence[FleurValueT]]",
        fn: Function[[Expr[FleurValueT]], FleurValueU] | Callable[[Expr[FleurValueT]], FleurValueU | Expr[FleurValueU]],
    ) -> "Expr[Sequence[FleurValueU]]":
        if not isinstance(fn, Function):
            fn = function(fn)
        return Expr(call(member_expr(array.__compile__(), "map"), fn.ast))

    @staticmethod
    def filter(
        array: "Expr[Sequence[FleurValueT]]",
        fn: Function[[Expr[FleurValueT]], bool] | Callable[[Expr[FleurValueT]], bool | Expr[bool]],
    ) -> "Expr[Sequence[FleurValueT]]":
        if not isinstance(fn, Function):
            fn = function(fn)
        return Expr(call(member_expr(array.__compile__(), "filter"), fn.ast))

    @staticmethod
    def sort_by(
        array: Expr[Sequence[FleurValueT]],
        key: Function[[Expr[FleurValueT]], _SortKeyT] | Callable[[Expr[FleurValueT]], _SortKeyT | Expr[_SortKeyT]],
        *,
        descending: bool | Expr[bool] = False,
    ) -> Expr[Sequence[FleurValueT]]:
        """Return a stable sorted copy using a numeric or string key evaluated once per item."""
        selector = key if isinstance(key, Function) else function(key)
        return Expr(runtime_call(("sortBy",), array.__compile__(), selector.ast, ensure_expr(descending)))

    @staticmethod
    def includes(
        array: "Expr[Sequence[FleurValueT]]",
        value: FleurValueT | Expr[FleurValueT],
    ) -> "Expr[bool]":
        return Expr[bool](call(member_expr(array.__compile__(), "includes"), ensure_expr(value)))

    @staticmethod
    def update_at(
        array: "Expr[Sequence[FleurValueT]]",
        index: int | Expr[int],
        value: FleurValueT | Expr[FleurValueT],
    ) -> "Expr[Sequence[FleurValueT]]":
        return Expr[Sequence[FleurValueT]](
            call(member_expr(array.__compile__(), "with"), ensure_expr(index), ensure_expr(value))
        )

    @staticmethod
    def concat(
        array: "Expr[Sequence[FleurValueT]]",
        *sequences: Sequence[FleurValueT | Expr[FleurValueT]] | Expr[Sequence[FleurValueT]],
    ) -> "Expr[Sequence[FleurValueT]]":
        expr = array.__compile__()
        for seq in sequences:
            seq = cast(Expr | FleurValue, seq)
            expr = call(member_expr(expr, "concat"), seq.__compile__() if isinstance(seq, Expr) else ensure_expr(seq))
        return Expr[Sequence[FleurValueT]](expr)
