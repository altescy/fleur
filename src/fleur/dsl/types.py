import inspect
from collections.abc import Callable
from typing import Generic, TypeVar, Union

from .ir import (
    IRAssignStmt,
    IRBinaryOperator,
    IRBinaryOpExpr,
    IRCallExpr,
    IRExpr,
    IRIdentifierExpr,
    IRLetStmt,
    IRLiteralNumberExpr,
)
from .runtime import require_block

PyStringCompat = str
PyBooleanCompat = bool
PyNumberCompat = Union[int, float]
PyGraineCompat = Union[PyStringCompat, PyBooleanCompat, PyNumberCompat]


class GraineType:
    def __init__(self, expr: IRExpr) -> None:
        self._expr = expr


class Number(GraineType):
    __slots__ = ("_expr",)

    def __init__(self, expr: IRExpr) -> None:
        super().__init__(expr=expr)

    def __add__(self, other: Union["Number", int, float]) -> "Number":
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.ADD,
                left=self._expr,
                right=rhs,
            )
        )

    def __radd__(self, other: Union["Number", int, float]) -> "Number":
        lhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.ADD,
                left=lhs,
                right=self._expr,
            )
        )

    def __sub__(self, other: Union["Number", int, float]) -> "Number":
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.SUBTRACT,
                left=self._expr,
                right=rhs,
            )
        )

    def __rsub__(self, other: Union["Number", int, float]) -> "Number":
        lhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.SUBTRACT,
                left=lhs,
                right=self._expr,
            )
        )

    def __mul__(self, other: Union["Number", int, float]) -> "Number":
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.MULTIPLY,
                left=self._expr,
                right=rhs,
            )
        )

    def __rmul__(self, other: Union["Number", int, float]) -> "Number":
        lhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.MULTIPLY,
                left=lhs,
                right=self._expr,
            )
        )

    def __truediv__(self, other: Union["Number", int, float]) -> "Number":
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.DIVIDE,
                left=self._expr,
                right=rhs,
            )
        )

    def __rtruediv__(self, other: Union["Number", int, float]) -> "Number":
        lhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.DIVIDE,
                left=lhs,
                right=self._expr,
            )
        )

    def __eq__(self, other: Union["Number", int, float]) -> "Boolean":  # type: ignore[override]
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.EQUAL,
                left=self._expr,
                right=rhs,
            )
        )

    def __ne__(self, other: Union["Number", int, float]) -> "Boolean":  # type: ignore[override]
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.NOT_EQUAL,
                left=self._expr,
                right=rhs,
            )
        )

    def __lt__(self, other: Union["Number", int, float]) -> "Boolean":
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.LESS_THAN,
                left=self._expr,
                right=rhs,
            )
        )

    def __le__(self, other: Union["Number", int, float]) -> "Boolean":
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.LESS_THAN_OR_EQUAL,
                left=self._expr,
                right=rhs,
            )
        )

    def __gt__(self, other: Union["Number", int, float]) -> "Boolean":
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.GREATER_THAN,
                left=self._expr,
                right=rhs,
            )
        )

    def __ge__(self, other: Union["Number", int, float]) -> "Boolean":
        rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.GREATER_THAN_OR_EQUAL,
                left=self._expr,
                right=rhs,
            )
        )

    def __iadd__(self, other: Union["Number", int, float]) -> "Number":
        # For += operator: x += y becomes x = x + y
        # Extract variable name from IRIdentifierExpr if possible
        if isinstance(self._expr, IRIdentifierExpr):
            var_name = self._expr.name
            rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
            new_expr = IRAssignStmt(
                name=var_name,
                value=IRBinaryOpExpr(
                    operator=IRBinaryOperator.ADD,
                    left=self._expr,
                    right=rhs,
                ),
            )
            require_block().emit(new_expr)
            return self
        raise TypeError("Can only use += on variables created with graine.let()")


class Boolean(GraineType):
    __slots__ = ("_expr",)

    def __init__(self, expr: IRExpr) -> None:
        super().__init__(expr=expr)

    def __bool__(self) -> bool:
        raise TypeError("Boolean instances cannot be converted to bool directly")


class String(GraineType):
    __slots__ = ("_expr",)

    def __init__(self, expr: IRExpr) -> None:
        super().__init__(expr=expr)


BooleanLike = Union[PyBooleanCompat, Boolean]
NumberLike = Union[PyNumberCompat, float, Number]
StringLike = Union[PyStringCompat, String]
GraineLike = Union[BooleanLike, NumberLike, StringLike]


_GraineT = TypeVar("_GraineT", bound=GraineType)


class Function(GraineType, Generic[_GraineT]):
    def __init__(
        self,
        name: str,
        fn: Callable[..., _GraineT],
    ) -> None:
        self.name = name
        self.fn = fn
        signature = inspect.signature(fn)
        self.params: tuple[tuple[str, type[GraineType]], ...] = tuple(
            (param.name, param.annotation) for param in signature.parameters.values()
        )
        self.ret_type: type[_GraineT] = signature.return_annotation

    def __call__(self, *args: GraineType) -> _GraineT:
        arg_exprs = [arg._expr for arg in args]
        call_expr = IRCallExpr(function=self.name, args=arg_exprs)
        var_name = f"_ret_{len(require_block().body)}"
        assign_stmt = IRLetStmt(
            value=call_expr,
            name=var_name,
        )
        require_block().emit(assign_stmt)
        return self.ret_type(expr=IRIdentifierExpr(name=var_name))
