from typing import Literal

from fleur.js.builder import call, ident, member_expr

from .expr import Expr, ensure_expr
from .types import FleurValue


class String:
    @staticmethod
    def or_empty(value: Expr[str | None]) -> Expr[str]:
        from .cond import Cond

        return Expr(Cond.when(Cond.equal(value, None), "", value).__compile__())

    @staticmethod
    def normalize(value: Expr[str], *, form: Literal["NFC", "NFD", "NFKC", "NFKD"] = "NFC") -> Expr[str]:
        return Expr(call(member_expr(value.__compile__(), "normalize"), ensure_expr(form)))

    @staticmethod
    def from_number(value: int | float | Expr[int | float]) -> Expr[str]:
        """Convert a number to text using the browser's plain number representation."""
        return String.from_value(value)

    @staticmethod
    def from_value(value: str | int | float | Expr[str | int | float]) -> Expr[str]:
        """Convert a string or number to text."""
        return Expr(call(ident("String"), ensure_expr(value)))

    @staticmethod
    def replace_all(value: Expr[str], search: str | Expr[str], replacement: str | Expr[str]) -> Expr[str]:
        """Replace every occurrence of the search text using JavaScript replacement rules."""
        return Expr(call(member_expr(value.__compile__(), "replaceAll"), ensure_expr(search), ensure_expr(replacement)))

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
