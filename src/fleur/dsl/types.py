import inspect
from collections.abc import Callable
from typing import Any, Generic, TypeVar, Union, overload

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

    def __add__(self, other: Union["Number", "Var[Number]", int, float]) -> "Number":
        rhs = other.read if isinstance(other, Var) else other
        rhs = rhs._expr if isinstance(rhs, Number) else IRLiteralNumberExpr(rhs)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.ADD,
                left=self._expr,
                right=rhs,
            )
        )

    def __radd__(self, other: Union["Number", "Var[Number]", int, float]) -> "Number":
        lhs = other.read if isinstance(other, Var) else other
        lhs = lhs._expr if isinstance(lhs, Number) else IRLiteralNumberExpr(lhs)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.ADD,
                left=lhs,
                right=self._expr,
            )
        )

    def __sub__(self, other: Union["Number", "Var[Number]", int, float]) -> "Number":
        rhs = other.read if isinstance(other, Var) else other
        rhs = rhs._expr if isinstance(rhs, Number) else IRLiteralNumberExpr(rhs)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.SUBTRACT,
                left=self._expr,
                right=rhs,
            )
        )

    def __rsub__(self, other: Union["Number", "Var[Number]", int, float]) -> "Number":
        lhs = other.read if isinstance(other, Var) else other
        lhs = lhs._expr if isinstance(lhs, Number) else IRLiteralNumberExpr(lhs)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.SUBTRACT,
                left=lhs,
                right=self._expr,
            )
        )


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


class Var(GraineType, Generic[_GraineT]):
    __slots__ = ("name", "read")

    def __init__(self, name: str, type_: type[_GraineT]) -> None:
        self.name = name
        self.read = type_(expr=IRIdentifierExpr(name=name))
        super().__init__(expr=self.read._expr)

    def __add__(self, other: Any) -> GraineType:
        if isinstance(other, Var):
            return self.read + other.read
        return self.read + other

    @overload
    def __iadd__(self: "Var[Union[Number, Boolean]]", other: Union[_GraineT, bool, int, float]) -> "Var[Number]": ...

    @overload
    def __iadd__(self: "Var[String]", other: Union[_GraineT, str]) -> "Var[String]": ...

    def __iadd__(self, other: Any) -> "Var":
        rhs = other._expr if isinstance(other, GraineType) else IRLiteralNumberExpr(other)
        new_expr = IRAssignStmt(
            name=self.name,
            value=IRBinaryOpExpr(
                operator=IRBinaryOperator.ADD,
                left=self.read._expr,
                right=rhs,
            ),
        )
        require_block().emit(new_expr)
        return self


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
