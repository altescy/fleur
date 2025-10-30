"""Standard library for Fleur DSL.

This module provides wrappers for JavaScript standard library functions.
"""

from typing import Any, Final, Union

from .ir import IRCallExpr, IRExpr, IRIdentifierExpr, IRPropertyAccessExpr
from .types import Number


def _to_ir_expr(value: Any) -> IRExpr:
    """Convert a value to an IRExpr.

    Handles Number, _GraineMethod (property access), and Python primitives.
    """
    from .ir import IRLiteralNumberExpr

    if hasattr(value, "_expr"):
        return value._expr  # type: ignore[attr-defined,no-any-return]
    elif isinstance(value, (int, float)):
        return IRLiteralNumberExpr(value)
    else:
        # Fallback: assume it's already an IRExpr or can be converted
        return value  # type: ignore[return-value]


class Math:
    """Wrapper for JavaScript Math object.

    Provides static methods that map to JavaScript Math functions.
    """

    # Mathematical constants
    PI: Final[Number] = Number(expr=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="PI"))
    """The mathematical constant π (pi)."""

    E: Final[Number] = Number(expr=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="E"))
    """Euler's number (e)."""

    # Basic math functions
    @staticmethod
    def abs(x: Union[Number, int, float]) -> Number:
        """Return the absolute value of x.

        Args:
            x: Input number

        Returns:
            Absolute value of x
        """
        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="abs"), args=[arg])
        )

    @staticmethod
    def ceil(x: Union[Number, int, float]) -> Number:
        """Return the smallest integer greater than or equal to x.

        Args:
            x: Input number

        Returns:
            Ceiling of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="ceil"), args=[arg])
        )

    @staticmethod
    def floor(x: Union[Number, int, float]) -> Number:
        """Return the largest integer less than or equal to x.

        Args:
            x: Input number

        Returns:
            Floor of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(
                function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="floor"), args=[arg]
            )
        )

    @staticmethod
    def round(x: Union[Number, int, float]) -> Number:
        """Return the value of x rounded to the nearest integer.

        Args:
            x: Input number

        Returns:
            Rounded value of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(
                function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="round"), args=[arg]
            )
        )

    @staticmethod
    def max(*values: Union[Number, int, float]) -> Number:
        """Return the largest of the input values.

        Args:
            *values: Variable number of values

        Returns:
            Maximum value
        """
        from .ir import IRExpr

        args: list[IRExpr] = [_to_ir_expr(v) for v in values]
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="max"), args=args)
        )

    @staticmethod
    def min(*values: Union[Number, int, float]) -> Number:
        """Return the smallest of the input values.

        Args:
            *values: Variable number of values

        Returns:
            Minimum value
        """
        from .ir import IRExpr

        args: list[IRExpr] = [_to_ir_expr(v) for v in values]
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="min"), args=args)
        )

    @staticmethod
    def pow(x: Union[Number, int, float], y: Union[Number, int, float]) -> Number:
        """Return x raised to the power of y.

        Args:
            x: Base number
            y: Exponent

        Returns:
            x raised to the power y
        """

        x_arg = _to_ir_expr(x)
        y_arg = _to_ir_expr(y)
        return Number(
            expr=IRCallExpr(
                function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="pow"), args=[x_arg, y_arg]
            )
        )

    @staticmethod
    def sqrt(x: Union[Number, int, float]) -> Number:
        """Return the square root of x.

        Args:
            x: Input number

        Returns:
            Square root of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="sqrt"), args=[arg])
        )

    # Trigonometric functions
    @staticmethod
    def sin(x: Union[Number, int, float]) -> Number:
        """Return the sine of x (x is in radians).

        Args:
            x: Angle in radians

        Returns:
            Sine of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="sin"), args=[arg])
        )

    @staticmethod
    def cos(x: Union[Number, int, float]) -> Number:
        """Return the cosine of x (x is in radians).

        Args:
            x: Angle in radians

        Returns:
            Cosine of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="cos"), args=[arg])
        )

    @staticmethod
    def tan(x: Union[Number, int, float]) -> Number:
        """Return the tangent of x (x is in radians).

        Args:
            x: Angle in radians

        Returns:
            Tangent of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="tan"), args=[arg])
        )

    @staticmethod
    def asin(x: Union[Number, int, float]) -> Number:
        """Return the arcsine of x, in radians.

        Args:
            x: Input value (must be between -1 and 1)

        Returns:
            Arcsine of x in radians
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="asin"), args=[arg])
        )

    @staticmethod
    def acos(x: Union[Number, int, float]) -> Number:
        """Return the arccosine of x, in radians.

        Args:
            x: Input value (must be between -1 and 1)

        Returns:
            Arccosine of x in radians
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="acos"), args=[arg])
        )

    @staticmethod
    def atan(x: Union[Number, int, float]) -> Number:
        """Return the arctangent of x, in radians.

        Args:
            x: Input value

        Returns:
            Arctangent of x in radians
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="atan"), args=[arg])
        )

    @staticmethod
    def atan2(y: Union[Number, int, float], x: Union[Number, int, float]) -> Number:
        """Return the arctangent of y/x, in radians.

        Args:
            y: Y coordinate
            x: X coordinate

        Returns:
            Arctangent of y/x in radians
        """

        y_arg = _to_ir_expr(y)
        x_arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(
                function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="atan2"), args=[y_arg, x_arg]
            )
        )

    # Exponential and logarithmic functions
    @staticmethod
    def exp(x: Union[Number, int, float]) -> Number:
        """Return e raised to the power of x.

        Args:
            x: Exponent

        Returns:
            e^x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="exp"), args=[arg])
        )

    @staticmethod
    def log(x: Union[Number, int, float]) -> Number:
        """Return the natural logarithm (base e) of x.

        Args:
            x: Input value (must be positive)

        Returns:
            Natural logarithm of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="log"), args=[arg])
        )

    @staticmethod
    def log10(x: Union[Number, int, float]) -> Number:
        """Return the base-10 logarithm of x.

        Args:
            x: Input value (must be positive)

        Returns:
            Base-10 logarithm of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(
                function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="log10"), args=[arg]
            )
        )

    @staticmethod
    def log2(x: Union[Number, int, float]) -> Number:
        """Return the base-2 logarithm of x.

        Args:
            x: Input value (must be positive)

        Returns:
            Base-2 logarithm of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="log2"), args=[arg])
        )

    # Random
    @staticmethod
    def random() -> Number:
        """Return a pseudo-random number between 0 (inclusive) and 1 (exclusive).

        Returns:
            Random number in [0, 1)
        """
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="random"), args=[])
        )

    # Other useful functions
    @staticmethod
    def sign(x: Union[Number, int, float]) -> Number:
        """Return the sign of x (-1, 0, or 1).

        Args:
            x: Input number

        Returns:
            Sign of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="sign"), args=[arg])
        )

    @staticmethod
    def trunc(x: Union[Number, int, float]) -> Number:
        """Return the integer part of x by removing any fractional digits.

        Args:
            x: Input number

        Returns:
            Integer part of x
        """

        arg = _to_ir_expr(x)
        return Number(
            expr=IRCallExpr(
                function=IRPropertyAccessExpr(target=IRIdentifierExpr("Math"), property="trunc"), args=[arg]
            )
        )
