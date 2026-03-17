from __future__ import annotations

from typing import Any, Generic, TypeAlias, TypeVar, cast

from fleur.js.ast import ESTreeBinaryExpression, ESTreeConditionalExpression, ESTreeExpression, ESTreeLogicalExpression
from fleur.js.builder import json_expr
from fleur.types import ICompilable

ValueT = TypeVar("ValueT", bound=object)
OperandValue: TypeAlias = Any


def compile_operand(operand: OperandValue) -> ESTreeExpression:
    if isinstance(operand, ESTreeExpression):
        return operand
    if isinstance(operand, ICompilable):
        return operand.__compile__()
    return json_expr(operand)


class Expr(Generic[ValueT], ICompilable[ESTreeExpression]):
    def __init__(self, expr: ESTreeExpression) -> None:
        self._expr = expr

    def __compile__(self) -> ESTreeExpression:
        return self._expr

    def __bool__(self) -> bool:
        raise TypeError(
            "Fleur Expr cannot be used as a Python boolean; use Expr.when(condition, consequent, alternate)"
        )

    @staticmethod
    def when(condition: OperandValue, consequent: OperandValue, alternate: OperandValue) -> "Expr[Any]":
        return Expr(
            ESTreeConditionalExpression(
                test=compile_operand(condition),
                consequent=compile_operand(consequent),
                alternate=compile_operand(alternate),
            )
        )

    @staticmethod
    def _logical_fold(operator: str, values: tuple[OperandValue, ...], *, empty_value: bool) -> "Expr[bool]":
        if not values:
            return cast(Expr[bool], Expr(json_expr(empty_value)))

        expr = compile_operand(values[0])
        for value in values[1:]:
            expr = ESTreeLogicalExpression(operator=cast(Any, operator), left=expr, right=compile_operand(value))
        return cast(Expr[bool], Expr(expr))

    @staticmethod
    def some(*conditions: OperandValue) -> "Expr[bool]":
        return Expr._logical_fold("||", conditions, empty_value=False)

    @staticmethod
    def every(*conditions: OperandValue) -> "Expr[bool]":
        return Expr._logical_fold("&&", conditions, empty_value=True)

    def _binary(self, operator: str, other: OperandValue) -> "Expr[Any]":
        return Expr(
            ESTreeBinaryExpression(operator=cast(Any, operator), left=self.__compile__(), right=compile_operand(other))
        )

    def __add__(self, other: OperandValue) -> "Expr[Any]":
        return self._binary("+", other)

    def __sub__(self, other: OperandValue) -> "Expr[Any]":
        return self._binary("-", other)

    def __mul__(self, other: OperandValue) -> "Expr[Any]":
        return self._binary("*", other)

    def __truediv__(self, other: OperandValue) -> "Expr[Any]":
        return self._binary("/", other)

    def __mod__(self, other: OperandValue) -> "Expr[Any]":
        return self._binary("%", other)

    def equals(self, other: OperandValue) -> "Expr[bool]":
        return cast(Expr[bool], self._binary("===", other))

    def not_equals(self, other: OperandValue) -> "Expr[bool]":
        return cast(Expr[bool], self._binary("!==", other))

    def __lt__(self, other: OperandValue) -> "Expr[bool]":
        return cast(Expr[bool], self._binary("<", other))

    def __le__(self, other: OperandValue) -> "Expr[bool]":
        return cast(Expr[bool], self._binary("<=", other))

    def __gt__(self, other: OperandValue) -> "Expr[bool]":
        return cast(Expr[bool], self._binary(">", other))

    def __ge__(self, other: OperandValue) -> "Expr[bool]":
        return cast(Expr[bool], self._binary(">=", other))
