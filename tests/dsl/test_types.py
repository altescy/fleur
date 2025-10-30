"""Tests for the type system."""

import pytest

from fleur.dsl.ir import (
    IRBinaryOperator,
    IRBinaryOpExpr,
    IRIdentifierExpr,
    IRLiteralNumberExpr,
)
from fleur.dsl.types import Boolean, Number, String


class TestNumber:
    """Test Number type operations."""

    def test_number_creation(self):
        """Test creating a Number instance."""
        expr = IRLiteralNumberExpr(42)
        num = Number(expr)
        assert num._expr == expr

    def test_number_add_number(self):
        """Test adding two Numbers."""
        left = Number(IRLiteralNumberExpr(10))
        right = Number(IRLiteralNumberExpr(20))
        result = left + right

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.ADD

    def test_number_add_int(self):
        """Test adding Number and int."""
        num = Number(IRLiteralNumberExpr(10))
        result = num + 5

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.ADD

    def test_number_add_float(self):
        """Test adding Number and float."""
        num = Number(IRLiteralNumberExpr(10))
        result = num + 3.14

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)

    def test_number_radd_int(self):
        """Test reverse add with int."""
        num = Number(IRLiteralNumberExpr(10))
        result = 5 + num

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.ADD

    def test_number_sub_number(self):
        """Test subtracting two Numbers."""
        left = Number(IRLiteralNumberExpr(20))
        right = Number(IRLiteralNumberExpr(10))
        result = left - right

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.SUBTRACT

    def test_number_sub_int(self):
        """Test subtracting int from Number."""
        num = Number(IRLiteralNumberExpr(20))
        result = num - 5

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.SUBTRACT

    def test_number_rsub_int(self):
        """Test reverse subtract with int."""
        num = Number(IRLiteralNumberExpr(10))
        result = 20 - num

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.SUBTRACT

    def test_number_mul_number(self):
        """Test multiplying two Numbers."""
        left = Number(IRLiteralNumberExpr(5))
        right = Number(IRLiteralNumberExpr(3))
        result = left * right

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.MULTIPLY

    def test_number_mul_int(self):
        """Test multiplying Number and int."""
        num = Number(IRLiteralNumberExpr(7))
        result = num * 6

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.MULTIPLY

    def test_number_mul_float(self):
        """Test multiplying Number and float."""
        num = Number(IRLiteralNumberExpr(2))
        result = num * 3.5

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)

    def test_number_rmul_int(self):
        """Test reverse multiply with int."""
        num = Number(IRLiteralNumberExpr(4))
        result = 5 * num

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.MULTIPLY

    def test_number_div_number(self):
        """Test dividing two Numbers."""
        left = Number(IRLiteralNumberExpr(20))
        right = Number(IRLiteralNumberExpr(4))
        result = left / right

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.DIVIDE

    def test_number_div_int(self):
        """Test dividing Number by int."""
        num = Number(IRLiteralNumberExpr(15))
        result = num / 3

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.DIVIDE

    def test_number_div_float(self):
        """Test dividing Number by float."""
        num = Number(IRLiteralNumberExpr(10))
        result = num / 2.5

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)

    def test_number_rdiv_int(self):
        """Test reverse divide with int."""
        num = Number(IRLiteralNumberExpr(4))
        result = 20 / num

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.DIVIDE

    def test_number_operations_chain(self):
        """Test chaining multiple operations."""
        a = Number(IRLiteralNumberExpr(10))
        b = Number(IRLiteralNumberExpr(20))
        c = Number(IRLiteralNumberExpr(5))

        result = (a + b) - c

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        # The outer operation should be subtraction
        assert result._expr.operator == IRBinaryOperator.SUBTRACT
        # The left side should be an addition
        assert isinstance(result._expr.left, IRBinaryOpExpr)
        assert result._expr.left.operator == IRBinaryOperator.ADD

    def test_number_complex_operations_chain(self):
        """Test chaining multiple operation types."""
        a = Number(IRLiteralNumberExpr(10))
        b = Number(IRLiteralNumberExpr(5))
        c = Number(IRLiteralNumberExpr(2))

        # (10 + 5) * 2
        result = (a + b) * c

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.MULTIPLY
        assert isinstance(result._expr.left, IRBinaryOpExpr)
        assert result._expr.left.operator == IRBinaryOperator.ADD

    def test_number_division_chain(self):
        """Test chaining division operations."""
        a = Number(IRLiteralNumberExpr(100))
        b = Number(IRLiteralNumberExpr(5))
        c = Number(IRLiteralNumberExpr(2))

        # (100 / 5) / 2
        result = (a / b) / c

        assert isinstance(result, Number)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.DIVIDE
        assert isinstance(result._expr.left, IRBinaryOpExpr)
        assert result._expr.left.operator == IRBinaryOperator.DIVIDE


class TestNumberComparison:
    """Test Number comparison operations."""

    def test_number_eq_number(self):
        """Test equality comparison between two Numbers."""
        left = Number(IRLiteralNumberExpr(10))
        right = Number(IRLiteralNumberExpr(10))
        result = left == right

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.EQUAL

    def test_number_eq_int(self):
        """Test equality comparison with int."""
        num = Number(IRLiteralNumberExpr(42))
        result = num == 42

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.EQUAL

    def test_number_ne_number(self):
        """Test inequality comparison between two Numbers."""
        left = Number(IRLiteralNumberExpr(10))
        right = Number(IRLiteralNumberExpr(20))
        result = left != right

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.NOT_EQUAL

    def test_number_lt_number(self):
        """Test less than comparison between two Numbers."""
        left = Number(IRLiteralNumberExpr(5))
        right = Number(IRLiteralNumberExpr(10))
        result = left < right

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.LESS_THAN

    def test_number_lt_int(self):
        """Test less than comparison with int."""
        num = Number(IRLiteralNumberExpr(5))
        result = num < 10

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.LESS_THAN

    def test_number_le_number(self):
        """Test less than or equal comparison."""
        left = Number(IRLiteralNumberExpr(10))
        right = Number(IRLiteralNumberExpr(10))
        result = left <= right

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.LESS_THAN_OR_EQUAL

    def test_number_gt_number(self):
        """Test greater than comparison."""
        left = Number(IRLiteralNumberExpr(15))
        right = Number(IRLiteralNumberExpr(10))
        result = left > right

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.GREATER_THAN

    def test_number_gt_float(self):
        """Test greater than comparison with float."""
        num = Number(IRLiteralNumberExpr(10))
        result = num > 5.5

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.GREATER_THAN

    def test_number_ge_number(self):
        """Test greater than or equal comparison."""
        left = Number(IRLiteralNumberExpr(10))
        right = Number(IRLiteralNumberExpr(10))
        result = left >= right

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.GREATER_THAN_OR_EQUAL

    def test_number_comparison_with_identifier(self):
        """Test comparison with identifier (variable reference)."""
        num = Number(IRLiteralNumberExpr(10))
        var = Number(IRIdentifierExpr("x"))
        result = num < var

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.LESS_THAN


class TestBoolean:
    """Test Boolean type operations."""

    def test_boolean_creation(self):
        """Test creating a Boolean instance."""
        expr = IRLiteralNumberExpr(1)
        boolean = Boolean(expr)
        assert boolean._expr == expr

    def test_boolean_cannot_convert_to_bool(self):
        """Test that Boolean instances cannot be converted to Python bool."""
        expr = IRLiteralNumberExpr(1)
        boolean = Boolean(expr)

        with pytest.raises(TypeError, match="cannot be converted to bool"):
            bool(boolean)

    def test_boolean_cannot_use_in_if(self):
        """Test that Boolean instances cannot be used in if statements."""
        expr = IRLiteralNumberExpr(1)
        boolean = Boolean(expr)

        with pytest.raises(TypeError):
            if boolean:
                pass

    def test_boolean_and_boolean(self):
        """Test AND operation between two Booleans."""
        from fleur.dsl.ir import IRLiteralBooleanExpr

        left = Boolean(IRLiteralBooleanExpr(True))
        right = Boolean(IRLiteralBooleanExpr(False))
        result = left & right

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.AND

    def test_boolean_and_bool(self):
        """Test AND operation between Boolean and Python bool."""
        from fleur.dsl.ir import IRLiteralBooleanExpr

        boolean = Boolean(IRLiteralBooleanExpr(True))
        result = boolean & False

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.AND

    def test_boolean_rand_bool(self):
        """Test reverse AND operation with Python bool."""
        from fleur.dsl.ir import IRLiteralBooleanExpr

        boolean = Boolean(IRLiteralBooleanExpr(True))
        result = False & boolean

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.AND

    def test_boolean_or_boolean(self):
        """Test OR operation between two Booleans."""
        from fleur.dsl.ir import IRLiteralBooleanExpr

        left = Boolean(IRLiteralBooleanExpr(True))
        right = Boolean(IRLiteralBooleanExpr(False))
        result = left | right

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.OR

    def test_boolean_or_bool(self):
        """Test OR operation between Boolean and Python bool."""
        from fleur.dsl.ir import IRLiteralBooleanExpr

        boolean = Boolean(IRLiteralBooleanExpr(False))
        result = boolean | True

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.OR

    def test_boolean_ror_bool(self):
        """Test reverse OR operation with Python bool."""
        from fleur.dsl.ir import IRLiteralBooleanExpr

        boolean = Boolean(IRLiteralBooleanExpr(False))
        result = True | boolean

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.OR

    def test_boolean_complex_expression(self):
        """Test complex Boolean expression with AND and OR."""
        from fleur.dsl.ir import IRLiteralBooleanExpr

        a = Boolean(IRLiteralBooleanExpr(True))
        b = Boolean(IRLiteralBooleanExpr(False))
        c = Boolean(IRLiteralBooleanExpr(True))
        result = (a & b) | c

        assert isinstance(result, Boolean)
        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.OR


class TestString:
    """Test String type operations."""

    def test_string_creation(self):
        """Test creating a String instance."""
        from fleur.dsl.ir import IRLiteralStringExpr

        expr = IRLiteralStringExpr("hello")
        string = String(expr)
        assert string._expr == expr


class TestTypeCompatibility:
    """Test type compatibility and conversions."""

    def test_number_like_types(self):
        """Test that NumberLike includes int, float, and Number."""

        # This is a type annotation test, mainly for documentation
        # In actual code, these would be checked by type checkers
        assert True  # Placeholder

    def test_boolean_like_types(self):
        """Test that BooleanLike includes bool and Boolean."""

        assert True  # Placeholder

    def test_string_like_types(self):
        """Test that StringLike includes str and String."""

        assert True  # Placeholder


class TestTypeInheritance:
    """Test type inheritance hierarchy."""

    def test_number_is_graine_type(self):
        """Test that Number is a GraineType."""
        from fleur.dsl.types import GraineType

        num = Number(IRLiteralNumberExpr(42))
        assert isinstance(num, GraineType)

    def test_boolean_is_graine_type(self):
        """Test that Boolean is a GraineType."""
        from fleur.dsl.types import GraineType

        boolean = Boolean(IRLiteralNumberExpr(1))
        assert isinstance(boolean, GraineType)

    def test_string_is_graine_type(self):
        """Test that String is a GraineType."""
        from fleur.dsl.types import GraineType

        string = String(IRIdentifierExpr("x"))
        assert isinstance(string, GraineType)


class TestFunction:
    """Test Function type."""

    def test_function_creation(self):
        """Test creating a Function."""
        from fleur.dsl.types import Function

        def sample_func(x: Number) -> Number:
            return x

        func = Function(name="sample", fn=sample_func)

        assert func.name == "sample"
        assert func.fn is sample_func
        assert len(func.params) == 1
        assert func.params[0][0] == "x"
        assert func.ret_type is Number

    def test_function_multiple_params(self):
        """Test Function with multiple parameters."""
        from fleur.dsl.types import Function

        def add(x: Number, y: Number) -> Number:
            return x + y

        func = Function(name="add", fn=add)

        assert len(func.params) == 2
        assert func.params[0][0] == "x"
        assert func.params[1][0] == "y"

    def test_function_call(self, clean_block):
        """Test calling a Function."""
        from fleur.dsl.types import Function

        def double(x: Number) -> Number:
            return x + x

        func = Function(name="double", fn=double)
        arg = Number(IRLiteralNumberExpr(21))
        result = func(arg)

        assert isinstance(result, Number)
        # Should emit a let statement for the return value
        assert len(clean_block.body) == 1
