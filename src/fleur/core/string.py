from fleur.js.builder import call, member_expr

from .expr import Expr, ensure_expr
from .types import FleurValue


class String:
    @staticmethod
    def includes(value: Expr[str], substring: str | Expr[str]) -> Expr[bool]:
        return Expr[bool](call(member_expr(value.__compile__(), "includes"), ensure_expr(substring)))

    @staticmethod
    def lower(value: Expr[str]) -> Expr[str]:
        return Expr[str](call(member_expr(value.__compile__(), "toLowerCase")))

    @staticmethod
    def upper(value: Expr[str]) -> Expr[str]:
        return Expr[str](call(member_expr(value.__compile__(), "toUpperCase")))

    @staticmethod
    def trim(value: Expr[str]) -> Expr[str]:
        return Expr[str](call(member_expr(value.__compile__(), "trim")))

    @staticmethod
    def split(value: Expr[str], separator: FleurValue | Expr) -> Expr[list[str]]:
        return Expr[list[str]](call(member_expr(value.__compile__(), "split"), ensure_expr(separator)))

    @staticmethod
    def starts_with(value: Expr[str], prefix: str | Expr[str]) -> Expr[bool]:
        return Expr[bool](call(member_expr(value.__compile__(), "startsWith"), ensure_expr(prefix)))

    @staticmethod
    def ends_with(value: Expr[str], suffix: str | Expr[str]) -> Expr[bool]:
        return Expr[bool](call(member_expr(value.__compile__(), "endsWith"), ensure_expr(suffix)))
