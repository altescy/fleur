from collections.abc import Callable, Sequence
from typing import cast

from fleur.js.builder import call, member_expr

from .expr import Expr, ensure_expr
from .function import Function, function
from .types import FleurValue, FleurValueT, FleurValueU


class Array:
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
