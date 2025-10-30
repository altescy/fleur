import inspect
from collections.abc import Callable
from typing import Generic, TypeVar, Union, overload

from typing_extensions import Never

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

ExprT = TypeVar("ExprT", bound=IRExpr, covariant=True)
NumberExprT = TypeVar("NumberExprT", bound=IRExpr)
BooleanExprT = TypeVar("BooleanExprT", bound=IRExpr)
StringExprT = TypeVar("StringExprT", bound=IRExpr)


class GraineType(Generic[ExprT]):
    def __init__(self, expr: ExprT) -> None:
        self._expr: ExprT = expr


class Number(GraineType[NumberExprT], Generic[NumberExprT]):
    __slots__ = ("_expr",)

    def __init__(self, expr: NumberExprT) -> None:
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

    # Only Number[IRIdentifierExpr] (variables) support +=
    # Using overload to explicitly reject non-identifier numbers
    @overload
    def __iadd__(
        self: "Number[IRIdentifierExpr]", other: Union["Number", int, float]
    ) -> "Number[IRIdentifierExpr]": ...

    @overload
    def __iadd__(self: "Number[IRLiteralNumberExpr]", other: Union["Number", int, float]) -> Never: ...

    @overload
    def __iadd__(self: "Number[IRBinaryOpExpr]", other: Union["Number", int, float]) -> Never: ...

    def __iadd__(self, other: Union["Number", int, float]) -> Union["Number[IRIdentifierExpr]", Never]:
        # For += operator: x += y becomes x = x + y
        # This method is only valid for Number[IRIdentifierExpr] (variables)
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
            return self  # type: ignore[return-value]
        raise TypeError("Can only use += on variables created with graine.let()")


class Boolean(GraineType[BooleanExprT], Generic[BooleanExprT]):
    __slots__ = ("_expr",)

    def __init__(self, expr: BooleanExprT) -> None:
        super().__init__(expr=expr)

    def __bool__(self) -> bool:
        raise TypeError("Boolean instances cannot be converted to bool directly")


class String(GraineType[StringExprT], Generic[StringExprT]):
    __slots__ = ("_expr",)

    def __init__(self, expr: StringExprT) -> None:
        super().__init__(expr=expr)


BooleanLike = Union[PyBooleanCompat, Boolean]
NumberLike = Union[PyNumberCompat, float, Number]
StringLike = Union[PyStringCompat, String]
GraineLike = Union[BooleanLike, NumberLike, StringLike]


GraineT = TypeVar("GraineT", bound=GraineType[IRExpr])


class Function(GraineType[IRIdentifierExpr], Generic[GraineT]):
    def __init__(
        self,
        name: str,
        fn: Callable[..., GraineT],
    ) -> None:
        # Function is identified by its name
        super().__init__(expr=IRIdentifierExpr(name))
        self.name = name
        self.fn = fn
        signature = inspect.signature(fn)
        self.params: tuple[tuple[str, type[GraineType]], ...] = tuple(
            (param.name, param.annotation) for param in signature.parameters.values()
        )
        self.ret_type: type[GraineT] = signature.return_annotation

    def __call__(self, *args: GraineType[IRExpr]) -> GraineT:
        arg_exprs = [arg._expr for arg in args]
        call_expr = IRCallExpr(function=self.name, args=arg_exprs)
        var_name = f"_ret_{len(require_block().body)}"
        assign_stmt = IRLetStmt(
            value=call_expr,
            name=var_name,
        )
        require_block().emit(assign_stmt)
        return self.ret_type(expr=IRIdentifierExpr(name=var_name))
