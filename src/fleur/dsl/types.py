import inspect
from collections.abc import Callable, Mapping, Sequence
from typing import Generic, Union, overload

from typing_extensions import Never, TypeVar

from .ir import (
    IRAssignStmt,
    IRBinaryOperator,
    IRBinaryOpExpr,
    IRCallExpr,
    IRExpr,
    IRIdentifierExpr,
    IRIndexAccessExpr,
    IRLetStmt,
    IRLiteralNumberExpr,
    IRLiteralStringExpr,
    IRMethodCallExpr,
    IRPropertyAccessExpr,
    IRPropertyAssignStmt,
    IRThisExpr,
)
from .runtime import require_block

PyStringCompat = str
PyBooleanCompat = bool
PyNumberCompat = Union[int, float]

# Use Any for now since GraineLike is defined later
# These will be properly typed as generic aliases after GraineLike is defined
PyArrayCompat = Sequence  # type: ignore[type-arg]
PyRecordCompat = Mapping  # type: ignore[type-arg]
PyGraineCompat = Union[PyStringCompat, PyBooleanCompat, PyNumberCompat, PyArrayCompat, PyRecordCompat]  # type: ignore[type-arg]

ExprT = TypeVar("ExprT", bound=IRExpr, covariant=True)


class _GraineMethod:
    """Helper class to handle method calls and property access on GraineType."""

    def __init__(self, target: IRExpr, method: str) -> None:
        self._target = target
        self._method = method
        # Make it compatible with Number operations by providing _expr for property access
        self._expr = IRPropertyAccessExpr(target=target, property=method)

    def __call__(self, *args: Union["GraineType", int, float, str, bool]) -> "GraineType":
        """Call the method with arguments."""
        arg_exprs: list[IRExpr] = []
        # Convert args to IRExpr
        for arg in args:
            if isinstance(arg, GraineType):
                arg_exprs.append(arg._expr)
            elif isinstance(arg, bool):
                from .ir import IRLiteralBooleanExpr

                arg_exprs.append(IRLiteralBooleanExpr(arg))
            elif isinstance(arg, (int, float)):
                arg_exprs.append(IRLiteralNumberExpr(arg))
            elif isinstance(arg, str):
                from .ir import IRLiteralStringExpr

                arg_exprs.append(IRLiteralStringExpr(arg))
            else:
                arg_exprs.append(arg)

        from .ir import IRMethodCallExpr

        # Return GraineType with method call expression
        return GraineType(expr=IRMethodCallExpr(target=self._target, method=self._method, args=arg_exprs))

    def __getattr__(self, name: str) -> "_GraineMethod":
        """Support method chaining like obj.prop.method()."""
        if name.startswith("_"):
            raise AttributeError(f"'_GraineMethod' object has no attribute '{name}'")
        # Return new _GraineMethod for chained access
        return _GraineMethod(target=self._expr, method=name)

    def _as_number(self) -> "Number":
        """Convert this property access to a Number."""
        return Number(expr=self._expr)

    # Support arithmetic operations on the method result (for cases like obj.method + 1)
    def __add__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        # First get the property value, then add
        prop_value = self._as_number()
        if isinstance(other, _GraineMethod):
            return prop_value + other._as_number()
        return prop_value + other

    def __radd__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        prop_value = self._as_number()
        if isinstance(other, _GraineMethod):
            return other._as_number() + prop_value
        return other + prop_value  # type: ignore[return-value]

    def __sub__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        prop_value = self._as_number()
        if isinstance(other, _GraineMethod):
            return prop_value - other._as_number()
        return prop_value - other

    def __rsub__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        prop_value = self._as_number()
        if isinstance(other, _GraineMethod):
            return other._as_number() - prop_value
        return other - prop_value  # type: ignore[return-value]

    def __mul__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        prop_value = self._as_number()
        if isinstance(other, _GraineMethod):
            return prop_value * other._as_number()
        return prop_value * other

    def __rmul__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        prop_value = self._as_number()
        if isinstance(other, _GraineMethod):
            return other._as_number() * prop_value
        return other * prop_value  # type: ignore[return-value]

    def __truediv__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        prop_value = self._as_number()
        if isinstance(other, _GraineMethod):
            return prop_value / other._as_number()
        return prop_value / other

    def __rtruediv__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        prop_value = self._as_number()
        if isinstance(other, _GraineMethod):
            return other._as_number() / prop_value
        return other / prop_value  # type: ignore[return-value]

    def __pow__(self, exponent: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "Number":
        prop_value = self._as_number()
        exp_value: Number
        if isinstance(exponent, _GraineMethod):
            exp_value = exponent._as_number()
        elif isinstance(exponent, Number):
            exp_value = exponent
        else:
            exp_value = Number(IRLiteralNumberExpr(exponent))
        return Number(
            expr=IRCallExpr(
                function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="pow"),
                args=[prop_value._expr, exp_value._expr],
            )
        )

    # Support augmented assignment operators (+=, -=, *=, /=) for properties
    def __iadd__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "_GraineMethod":
        """Support += on properties like this.x += 1."""
        if not isinstance(self._expr, IRPropertyAccessExpr):
            raise TypeError("Can only use += on properties")

        if isinstance(other, _GraineMethod):
            rhs = other._expr
        elif isinstance(other, Number):
            rhs = other._expr
        else:
            rhs = IRLiteralNumberExpr(other)

        require_block().emit(
            IRPropertyAssignStmt(
                target=self._expr, value=IRBinaryOpExpr(operator=IRBinaryOperator.ADD, left=self._expr, right=rhs)
            )
        )
        return self

    def __isub__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "_GraineMethod":
        """Support -= on properties like this.x -= 1."""
        if not isinstance(self._expr, IRPropertyAccessExpr):
            raise TypeError("Can only use -= on properties")

        if isinstance(other, _GraineMethod):
            rhs = other._expr
        elif isinstance(other, Number):
            rhs = other._expr
        else:
            rhs = IRLiteralNumberExpr(other)

        require_block().emit(
            IRPropertyAssignStmt(
                target=self._expr, value=IRBinaryOpExpr(operator=IRBinaryOperator.SUBTRACT, left=self._expr, right=rhs)
            )
        )
        return self

    def __imul__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "_GraineMethod":
        """Support *= on properties like this.x *= 2."""
        if not isinstance(self._expr, IRPropertyAccessExpr):
            raise TypeError("Can only use *= on properties")

        if isinstance(other, _GraineMethod):
            rhs = other._expr
        elif isinstance(other, Number):
            rhs = other._expr
        else:
            rhs = IRLiteralNumberExpr(other)

        require_block().emit(
            IRPropertyAssignStmt(
                target=self._expr, value=IRBinaryOpExpr(operator=IRBinaryOperator.MULTIPLY, left=self._expr, right=rhs)
            )
        )
        return self

    def __itruediv__(self, other: Union["Number", PyNumberCompat, "_GraineMethod"]) -> "_GraineMethod":
        """Support /= on properties like this.x /= 2."""
        if not isinstance(self._expr, IRPropertyAccessExpr):
            raise TypeError("Can only use /= on properties")

        if isinstance(other, _GraineMethod):
            rhs = other._expr
        elif isinstance(other, Number):
            rhs = other._expr
        else:
            rhs = IRLiteralNumberExpr(other)

        require_block().emit(
            IRPropertyAssignStmt(
                target=self._expr, value=IRBinaryOpExpr(operator=IRBinaryOperator.DIVIDE, left=self._expr, right=rhs)
            )
        )
        return self


NumberExprT = TypeVar("NumberExprT", bound=IRExpr)
BooleanExprT = TypeVar("BooleanExprT", bound=IRExpr)
StringExprT = TypeVar("StringExprT", bound=IRExpr)
ArrayExprT = TypeVar("ArrayExprT", bound=IRExpr, default=IRExpr)
RecordExprT = TypeVar("RecordExprT", bound=IRExpr, default=IRExpr)

# Element/Value type variables for Array and Record
ArrayElementT = TypeVar("ArrayElementT", bound="GraineType")
RecordValueT = TypeVar("RecordValueT", bound="GraineType")


class GraineType(Generic[ExprT]):
    def __init__(self, expr: ExprT) -> None:
        self._expr: ExprT = expr

    def __getitem__(self, index: Union[int, "Number"]) -> "GraineType":
        """Support array-like indexing on GraineType."""
        index_expr = index._expr if isinstance(index, Number) else IRLiteralNumberExpr(index)
        return GraineType(expr=IRIndexAccessExpr(target=self._expr, index=index_expr))

    def __getattr__(self, name: str) -> _GraineMethod:
        """Support property access and method calls on GraineType.

        Returns a _GraineMethod object that can be:
        - Called as a method: obj.method()
        - Used as a property in arithmetic: obj.prop * 2
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        # Return _GraineMethod which supports both property access and method calls
        return _GraineMethod(target=self._expr, method=name)


class Number(GraineType[NumberExprT], Generic[NumberExprT]):
    __slots__ = ("_expr",)

    def __init__(self, expr: NumberExprT) -> None:
        super().__init__(expr=expr)

    def __add__(self, other: Union["Number", int, float, "_GraineMethod"]) -> "Number":
        if isinstance(other, _GraineMethod):
            rhs = other._expr
        elif isinstance(other, Number):
            rhs = other._expr
        else:
            rhs = IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.ADD,
                left=self._expr,
                right=rhs,
            )
        )

    def __radd__(self, other: Union["Number", int, float, "_GraineMethod"]) -> "Number":
        if isinstance(other, _GraineMethod):
            lhs = other._expr
        elif isinstance(other, Number):
            lhs = other._expr
        else:
            lhs = IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.ADD,
                left=lhs,
                right=self._expr,
            )
        )

    def __sub__(self, other: Union["Number", int, float, "_GraineMethod"]) -> "Number":
        if isinstance(other, _GraineMethod):
            rhs = other._expr
        elif isinstance(other, Number):
            rhs = other._expr
        else:
            rhs = IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.SUBTRACT,
                left=self._expr,
                right=rhs,
            )
        )

    def __rsub__(self, other: Union["Number", int, float, "_GraineMethod"]) -> "Number":
        if isinstance(other, _GraineMethod):
            lhs = other._expr
        elif isinstance(other, Number):
            lhs = other._expr
        else:
            lhs = IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.SUBTRACT,
                left=lhs,
                right=self._expr,
            )
        )

    def __mul__(self, other: Union["Number", int, float, "_GraineMethod"]) -> "Number":
        if isinstance(other, _GraineMethod):
            rhs = other._expr
        elif isinstance(other, Number):
            rhs = other._expr
        else:
            rhs = IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.MULTIPLY,
                left=self._expr,
                right=rhs,
            )
        )

    def __rmul__(self, other: Union["Number", int, float, "_GraineMethod"]) -> "Number":
        if isinstance(other, _GraineMethod):
            lhs = other._expr
        elif isinstance(other, Number):
            lhs = other._expr
        else:
            lhs = IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.MULTIPLY,
                left=lhs,
                right=self._expr,
            )
        )

    def __truediv__(self, other: Union["Number", int, float, "_GraineMethod"]) -> "Number":
        if isinstance(other, _GraineMethod):
            rhs = other._expr
        elif isinstance(other, Number):
            rhs = other._expr
        else:
            rhs = IRLiteralNumberExpr(other)
        return Number(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.DIVIDE,
                left=self._expr,
                right=rhs,
            )
        )

    def __rtruediv__(self, other: Union["Number", int, float, "_GraineMethod"]) -> "Number":
        if isinstance(other, _GraineMethod):
            lhs = other._expr
        elif isinstance(other, Number):
            lhs = other._expr
        else:
            lhs = IRLiteralNumberExpr(other)
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

    def toFixed(self, digits: Union[int, "Number"] = 0) -> "String":
        """Format number with fixed decimal places."""
        digits_expr = digits._expr if isinstance(digits, Number) else IRLiteralNumberExpr(digits)
        return String(expr=IRMethodCallExpr(target=self._expr, method="toFixed", args=[digits_expr]))

    def toString(self) -> "String":
        """Convert number to string."""
        return String(expr=IRMethodCallExpr(target=self._expr, method="toString", args=[]))

    # Number[IRIdentifierExpr] and Number[IRPropertyAccessExpr] support +=
    @overload
    def __iadd__(
        self: "Number[IRIdentifierExpr]", other: Union["Number", int, float]
    ) -> "Number[IRIdentifierExpr]": ...

    @overload
    def __iadd__(
        self: "Number[IRPropertyAccessExpr]", other: Union["Number", int, float]
    ) -> "Number[IRPropertyAccessExpr]": ...

    @overload
    def __iadd__(self: "Number[IRLiteralNumberExpr]", other: Union["Number", int, float]) -> Never: ...

    @overload
    def __iadd__(self: "Number[IRBinaryOpExpr]", other: Union["Number", int, float]) -> Never: ...

    def __iadd__(
        self, other: Union["Number", int, float]
    ) -> Union["Number[IRIdentifierExpr]", "Number[IRPropertyAccessExpr]", Never]:
        # For += operator: x += y becomes x = x + y
        # This method is valid for Number[IRIdentifierExpr] (variables) and Number[IRPropertyAccessExpr] (properties)
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
        elif isinstance(self._expr, IRPropertyAccessExpr):
            # For property access like this.x += 1
            rhs = other._expr if isinstance(other, Number) else IRLiteralNumberExpr(other)
            from .ir import IRPropertyAssignStmt

            new_expr = IRPropertyAssignStmt(
                target=self._expr,
                value=IRBinaryOpExpr(
                    operator=IRBinaryOperator.ADD,
                    left=self._expr,
                    right=rhs,
                ),
            )
            require_block().emit(new_expr)
            return self  # type: ignore[return-value]
        raise TypeError("Can only use += on variables or properties")


class Boolean(GraineType[BooleanExprT], Generic[BooleanExprT]):
    __slots__ = ("_expr",)

    def __init__(self, expr: BooleanExprT) -> None:
        super().__init__(expr=expr)

    def __bool__(self) -> bool:
        raise TypeError("Boolean instances cannot be converted to bool directly")

    def __and__(self, other: Union["Boolean", bool]) -> "Boolean":
        """Logical AND operator (&)."""
        from .ir import IRLiteralBooleanExpr

        if isinstance(other, Boolean):
            rhs = other._expr
        else:
            rhs = IRLiteralBooleanExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.AND,
                left=self._expr,
                right=rhs,
            )
        )

    def __rand__(self, other: Union["Boolean", bool]) -> "Boolean":
        """Reverse logical AND operator (&)."""
        from .ir import IRLiteralBooleanExpr

        if isinstance(other, Boolean):
            lhs = other._expr
        else:
            lhs = IRLiteralBooleanExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.AND,
                left=lhs,
                right=self._expr,
            )
        )

    def __or__(self, other: Union["Boolean", bool]) -> "Boolean":
        """Logical OR operator (|)."""
        from .ir import IRLiteralBooleanExpr

        if isinstance(other, Boolean):
            rhs = other._expr
        else:
            rhs = IRLiteralBooleanExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.OR,
                left=self._expr,
                right=rhs,
            )
        )

    def __ror__(self, other: Union["Boolean", bool]) -> "Boolean":
        """Reverse logical OR operator (|)."""
        from .ir import IRLiteralBooleanExpr

        if isinstance(other, Boolean):
            lhs = other._expr
        else:
            lhs = IRLiteralBooleanExpr(other)
        return Boolean(
            expr=IRBinaryOpExpr(
                operator=IRBinaryOperator.OR,
                left=lhs,
                right=self._expr,
            )
        )


class String(GraineType[StringExprT], Generic[StringExprT]):
    __slots__ = ("_expr",)

    def __init__(self, expr: StringExprT) -> None:
        super().__init__(expr=expr)

    @property
    def length(self) -> "Number":
        """Get the length of the string."""
        return Number(expr=IRPropertyAccessExpr(target=self._expr, property="length"))

    def toUpperCase(self) -> "String":
        """Convert string to uppercase."""
        return String(expr=IRMethodCallExpr(target=self._expr, method="toUpperCase", args=[]))

    def toLowerCase(self) -> "String":
        """Convert string to lowercase."""
        return String(expr=IRMethodCallExpr(target=self._expr, method="toLowerCase", args=[]))

    def substring(self, start: Union[int, "Number"], end: Union[int, "Number", None] = None) -> "String":
        """Extract a substring."""
        start_expr = start._expr if isinstance(start, Number) else IRLiteralNumberExpr(start)
        args: list[IRExpr] = [start_expr]
        if end is not None:
            end_expr = end._expr if isinstance(end, Number) else IRLiteralNumberExpr(end)
            args.append(end_expr)
        return String(expr=IRMethodCallExpr(target=self._expr, method="substring", args=args))

    def indexOf(self, search: Union[str, "String"]) -> "Number":
        """Find the index of a substring."""
        search_expr = search._expr if isinstance(search, String) else IRLiteralStringExpr(search)
        return Number(expr=IRMethodCallExpr(target=self._expr, method="indexOf", args=[search_expr]))

    def split(self, separator: Union[str, "String"]) -> "Array[String, IRExpr]":
        """Split string into an array."""
        sep_expr = separator._expr if isinstance(separator, String) else IRLiteralStringExpr(separator)
        return Array(expr=IRMethodCallExpr(target=self._expr, method="split", args=[sep_expr]))

    def trim(self) -> "String":
        """Remove whitespace from both ends."""
        return String(expr=IRMethodCallExpr(target=self._expr, method="trim", args=[]))

    def replace(self, search: Union[str, "String"], replacement: Union[str, "String"]) -> "String":
        """Replace first occurrence of a substring."""
        search_expr = search._expr if isinstance(search, String) else IRLiteralStringExpr(search)
        replacement_expr = replacement._expr if isinstance(replacement, String) else IRLiteralStringExpr(replacement)
        return String(expr=IRMethodCallExpr(target=self._expr, method="replace", args=[search_expr, replacement_expr]))


class Array(GraineType[ArrayExprT], Generic[ArrayElementT, ArrayExprT]):
    __slots__ = ("_expr",)

    def __init__(self, expr: ArrayExprT) -> None:
        super().__init__(expr=expr)

    def __getitem__(self, index: Union[int, "Number"]) -> ArrayElementT:  # type: ignore[override]
        """Access array element by index."""
        index_expr = index._expr if isinstance(index, Number) else IRLiteralNumberExpr(index)
        # Return a generic GraineType; the actual element type is determined by the type parameter
        return GraineType(expr=IRIndexAccessExpr(target=self._expr, index=index_expr))  # type: ignore[return-value]

    @property
    def length(self) -> "Number":
        """Get the length of the array."""
        return Number(expr=IRPropertyAccessExpr(target=self._expr, property="length"))

    def push(self, *elements: Union[ArrayElementT, int, float, str, bool]) -> "Number":
        """Push elements to the array and return new length."""
        args = []
        for elem in elements:
            if isinstance(elem, GraineType):
                args.append(elem._expr)
            elif isinstance(elem, bool):
                args.append(IRLiteralNumberExpr(1 if elem else 0))
            elif isinstance(elem, (int, float)):
                args.append(IRLiteralNumberExpr(elem))
            elif isinstance(elem, str):
                args.append(IRLiteralStringExpr(elem))
            else:
                args.append(elem)
        return Number(expr=IRMethodCallExpr(target=self._expr, method="push", args=args))

    def pop(self) -> ArrayElementT:
        """Remove and return the last element."""
        return GraineType(expr=IRMethodCallExpr(target=self._expr, method="pop", args=[]))  # type: ignore[return-value]

    def join(self, separator: Union[str, "String"] = ",") -> "String":
        """Join array elements into a string."""
        sep_expr = separator._expr if isinstance(separator, String) else IRLiteralStringExpr(separator)
        return String(expr=IRMethodCallExpr(target=self._expr, method="join", args=[sep_expr]))

    def slice(
        self, start: Union[int, "Number"], end: Union[int, "Number", None] = None
    ) -> "Array[ArrayElementT, IRExpr]":
        """Return a slice of the array."""
        start_expr = start._expr if isinstance(start, Number) else IRLiteralNumberExpr(start)
        args: list[IRExpr] = [start_expr]
        if end is not None:
            end_expr = end._expr if isinstance(end, Number) else IRLiteralNumberExpr(end)
            args.append(end_expr)
        return Array(expr=IRMethodCallExpr(target=self._expr, method="slice", args=args))


class Record(GraineType[RecordExprT], Generic[RecordValueT, RecordExprT]):
    __slots__ = ("_expr",)

    def __init__(self, expr: RecordExprT) -> None:
        super().__init__(expr=expr)

    def __getattr__(self, name: str) -> RecordValueT:  # type: ignore[override]
        """Access record property by name."""
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        # Return a generic GraineType; the actual value type is determined by the type parameter
        return GraineType(expr=IRPropertyAccessExpr(target=self._expr, property=name))  # type: ignore[return-value]


BooleanLike = Union[PyBooleanCompat, Boolean]
NumberLike = Union[PyNumberCompat, float, Number]
StringLike = Union[PyStringCompat, String]
ArrayLike = Union[list, "Array"]
RecordLike = Union[dict, "Record"]
GraineLike = Union[BooleanLike, NumberLike, StringLike, ArrayLike, RecordLike]

# Type aliases for commonly used Array and Record types with element/value types
# These allow simpler syntax like Array[Number] instead of Array[Number, IRExpr]
# Note: For runtime use with explicit IR types, use the full Array[ElementT, ExprT] syntax


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


class This(GraineType[IRThisExpr]):
    """Represents 'this' in JavaScript class methods."""

    def __init__(self) -> None:
        super().__init__(expr=IRThisExpr())

    def __getattr__(self, name: str) -> _GraineMethod:
        """Support property access on This.

        Returns _GraineMethod which supports:
        - Arithmetic operations (self.x + 1)
        - Augmented assignment (self.x += 1)
        - Method calls (self.foo())
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        # Return _GraineMethod so that arithmetic operations and augmented assignments work
        return _GraineMethod(target=self._expr, method=name)

    def __setattr__(self, name: str, value: GraineLike) -> None:
        """Handle property assignment: self.x = value

        Args:
            name: Property name
            value: Value to assign (can be any Graine-compatible type)
        """
        if name.startswith("_"):
            # Internal attributes
            object.__setattr__(self, name, value)
        else:
            # Generate property assignment
            from ._utils import as_literal

            # Handle GraineType, _GraineMethod, or plain Python values
            if isinstance(value, GraineType):
                val_expr = value._expr
            elif hasattr(value, "_expr"):
                val_expr = value._expr  # type: ignore[attr-defined]
            else:
                val_expr = as_literal(value)._expr

            prop_access = IRPropertyAccessExpr(target=IRThisExpr(), property=name)

            # Skip self-assignment like this.x = this.x (which can occur from += operations)
            if (
                isinstance(val_expr, IRPropertyAccessExpr)
                and isinstance(val_expr.target, IRThisExpr)
                and val_expr.property == name
            ):
                # This is a self-assignment, skip it
                return

            require_block().emit(IRPropertyAssignStmt(target=prop_access, value=val_expr))
