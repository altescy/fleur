from fleur.js.builder import call, ident, member, member_expr

from .expr import Expr, ensure_expr


class Number:
    @staticmethod
    def from_string(value: str | Expr[str]) -> Expr[int | float]:
        """Convert text using JavaScript Number rules. Empty text becomes zero and invalid text becomes NaN."""
        return Expr(call(ident("Number"), ensure_expr(value)))

    @staticmethod
    def format(value: int | float | Expr[int | float], *, locale: str | Expr[str] | None = None) -> Expr[str]:
        """Format a number for display in the requested locale or the browser's default locale."""
        options = () if locale is None else (ensure_expr(locale),)
        formatter = call(member("Intl", "NumberFormat"), *options)
        return Expr(call(member_expr(formatter, "format"), ensure_expr(value)))

    @staticmethod
    def is_finite(value: Expr[int | float | str]) -> Expr[bool]:
        return Expr[bool](call(member_expr(ident("Number"), "isFinite"), call(ident("Number"), value.__compile__())))

    @staticmethod
    def abs(value: Expr[int]) -> Expr[int]:
        return Expr[int](call(member_expr(ident("Math"), "abs"), value.__compile__()))

    @staticmethod
    def floor(value: Expr[int | float]) -> Expr[int]:
        return Expr[int](call(member_expr(ident("Math"), "floor"), value.__compile__()))

    @staticmethod
    def ceil(value: Expr[int | float]) -> Expr[int]:
        return Expr[int](call(member_expr(ident("Math"), "ceil"), value.__compile__()))

    @staticmethod
    def round(value: Expr[int | float]) -> Expr[int]:
        return Expr[int](call(member_expr(ident("Math"), "round"), value.__compile__()))

    @staticmethod
    def sign(value: Expr[int | float]) -> Expr[int]:
        return Expr[int](call(member_expr(ident("Math"), "sign"), value.__compile__()))
