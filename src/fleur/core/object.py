from collections.abc import Mapping, Sequence
from typing import Any

from fleur.js.builder import call, ident, member_expr

from .expr import Expr, ensure_expr
from .types import FleurValueT, KeyT


class Object:
    @staticmethod
    def has(obj: Expr[Mapping[str, Any]], key: str | Expr[str]) -> Expr[bool]:
        return Expr(call(member_expr(obj.__compile__(), "hasOwnProperty"), ensure_expr(key)))

    @staticmethod
    def keys(obj: Expr[Mapping[KeyT, Any]]) -> Expr[Sequence[KeyT]]:
        return Expr(call(member_expr(ident("Object"), "keys"), obj.__compile__()))

    @staticmethod
    def values(obj: Expr[Mapping[str, FleurValueT]]) -> Expr[Sequence[FleurValueT]]:
        return Expr[Sequence[FleurValueT]](call(member_expr(ident("Object"), "values"), obj.__compile__()))

    @staticmethod
    def entries(obj: Expr[Mapping[KeyT, FleurValueT]]) -> Expr[Sequence[tuple[KeyT, FleurValueT]]]:
        return Expr(call(member_expr(ident("Object"), "entries"), obj.__compile__()))

    @staticmethod
    def assign(
        target: Expr[Mapping[KeyT, FleurValueT]],
        *sources: Mapping[KeyT, FleurValueT] | Expr[Mapping[KeyT, FleurValueT]],
    ) -> Expr[Mapping[KeyT, FleurValueT]]:
        expr = target.__compile__()
        for source in sources:
            expr = call(member_expr(ident("Object"), "assign"), expr, ensure_expr(source))
        return Expr(expr)
