from fleur.js.builder import call, ident, member_expr

from .expr import Expr


class Number:
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
