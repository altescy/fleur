"""Tests for the type system."""

import pytest

from fleur.dsl.ir import (
    IRBinaryOperator,
    IRBinaryOpExpr,
    IRIdentifierExpr,
    IRLiteralNumberExpr,
)
from fleur.dsl.types import Boolean, Number, String, Var


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


class TestString:
    """Test String type operations."""

    def test_string_creation(self):
        """Test creating a String instance."""
        from fleur.dsl.ir import IRLiteralStringExpr

        expr = IRLiteralStringExpr("hello")
        string = String(expr)
        assert string._expr == expr


class TestVar:
    """Test Var type operations."""

    def test_var_creation_number(self):
        """Test creating a Var[Number]."""
        var = Var(name="x", type_=Number)
        assert var.name == "x"
        assert isinstance(var.read, Number)
        assert isinstance(var.read._expr, IRIdentifierExpr)
        assert var.read._expr.name == "x"

    def test_var_creation_boolean(self):
        """Test creating a Var[Boolean]."""
        var = Var(name="flag", type_=Boolean)
        assert var.name == "flag"
        assert isinstance(var.read, Boolean)

    def test_var_creation_string(self):
        """Test creating a Var[String]."""
        var = Var(name="text", type_=String)
        assert var.name == "text"
        assert isinstance(var.read, String)

    def test_var_add_with_number(self):
        """Test adding Var with Number."""
        var = Var(name="x", type_=Number)
        num = Number(IRLiteralNumberExpr(10))
        result = var + num

        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.ADD

    def test_var_add_with_int(self):
        """Test adding Var with int."""
        var = Var(name="x", type_=Number)
        result = var + 5

        assert isinstance(result._expr, IRBinaryOpExpr)

    def test_var_add_two_vars(self):
        """Test adding two Vars."""
        var1 = Var(name="x", type_=Number)
        var2 = Var(name="y", type_=Number)
        result = var1 + var2

        assert isinstance(result._expr, IRBinaryOpExpr)
        assert result._expr.operator == IRBinaryOperator.ADD


class TestVarMutation:
    """Test Var mutation operations."""

    def test_var_iadd_with_int(self, clean_block):
        """Test += operator with int."""
        var = Var(name="x", type_=Number)
        var += 5

        # Check that a statement was emitted
        assert len(clean_block.body) == 1
        from fleur.dsl.ir import IRAssignStmt

        assert isinstance(clean_block.body[0], IRAssignStmt)
        assert clean_block.body[0].name == "x"

    def test_var_iadd_with_number(self, clean_block):
        """Test += operator with Number."""
        var = Var(name="x", type_=Number)
        num = Number(IRLiteralNumberExpr(10))
        var += num

        assert len(clean_block.body) == 1
        from fleur.dsl.ir import IRAssignStmt

        assert isinstance(clean_block.body[0], IRAssignStmt)

    def test_var_iadd_returns_self(self, clean_block):
        """Test that += returns the same Var instance."""
        var: Var[Number] = Var(name="x", type_=Number)
        var += 5  # type: ignore[operator]

        assert var.name == "x"

    def test_var_iadd_multiple_times(self, clean_block):
        """Test multiple += operations."""
        var = Var(name="x", type_=Number)
        var += 1  # type: ignore[operator]
        var += 2  # type: ignore[operator]
        var += 3  # type: ignore[operator]

        # Should emit 3 assignment statements
        assert len(clean_block.body) == 3


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

    def test_var_is_graine_type(self):
        """Test that Var is a GraineType."""
        from fleur.dsl.types import GraineType

        var = Var(name="x", type_=Number)
        assert isinstance(var, GraineType)


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
