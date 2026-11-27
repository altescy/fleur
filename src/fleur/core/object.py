from collections.abc import Mapping, Sequence
from typing import Any

from fleur.js.ast import ESTreeConditionalExpression, ESTreeMemberExpression
from fleur.js.builder import call, ident, literal, member_expr

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

    @staticmethod
    def get(obj: Expr[Mapping[KeyT, FleurValueT]], key: KeyT | Expr[KeyT]) -> Expr[FleurValueT | None]:
        """Look up a key that may be missing, like Elm's `Dict.get`.

        `obj[key]` assumes that the key exists. This returns `None` for a missing key, including
        names inherited from the object prototype such as `"constructor"`.
        """
        compiled, name = obj.__compile__(), ensure_expr(key)
        has_own = member_expr(member_expr(member_expr(ident("Object"), "prototype"), "hasOwnProperty"), "call")
        value = ESTreeMemberExpression(object=compiled, property=name, computed=True)
        return Expr(
            ESTreeConditionalExpression(test=call(has_own, compiled, name), consequent=value, alternate=literal(None))
        )
