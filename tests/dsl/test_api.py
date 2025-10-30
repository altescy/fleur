"""Tests for the DSL API (graine interface)."""

from fleur.dsl import graine
from fleur.dsl.types import Boolean, Number, String


class TestGraineLiteral:
    """Test graine.literal() API."""

    def test_literal_true_returns_boolean(self):
        """Test that literal(True) returns Boolean."""
        result = graine.literal(True)
        assert isinstance(result, Boolean)

    def test_literal_false_returns_boolean(self):
        """Test that literal(False) returns Boolean."""
        result = graine.literal(False)
        assert isinstance(result, Boolean)

    def test_literal_int_returns_number(self):
        """Test that literal(int) returns Number."""
        result = graine.literal(42)
        assert isinstance(result, Number)

    def test_literal_zero_returns_number(self):
        """Test that literal(0) returns Number."""
        result = graine.literal(0)
        assert isinstance(result, Number)

    def test_literal_negative_returns_number(self):
        """Test that literal(-5) returns Number."""
        result = graine.literal(-5)
        assert isinstance(result, Number)

    def test_literal_float_returns_number(self):
        """Test that literal(float) returns Number."""
        result = graine.literal(3.14)
        assert isinstance(result, Number)

    def test_literal_string_returns_string(self):
        """Test that literal(str) returns String."""
        result = graine.literal("hello")
        assert isinstance(result, String)

    def test_literal_empty_string_returns_string(self):
        """Test that literal("") returns String."""
        result = graine.literal("")
        assert isinstance(result, String)


class TestGraineLet:
    """Test graine.let() API."""

    def test_let_with_number(self, clean_block):
        """Test let with a number value."""
        from fleur.dsl.types import Var

        result = graine.let(graine.literal(42), name="x")

        assert isinstance(result, Var)
        assert result.name == "x_0"  # Variable naming pattern

    def test_let_with_boolean(self, clean_block):
        """Test let with a boolean value."""
        from fleur.dsl.types import Var

        result = graine.let(graine.literal(True), name="flag")

        assert isinstance(result, Var)
        assert result.name == "flag_0"

    def test_let_with_python_int(self, clean_block):
        """Test let with a Python int (auto-conversion)."""
        from fleur.dsl.types import Var

        result = graine.let(42, name="num")

        assert isinstance(result, Var)
        assert result.name == "num_0"

    def test_let_emits_statement(self, clean_block):
        """Test that let emits a statement to the current block."""
        graine.let(graine.literal(10), name="x")

        from fleur.dsl.ir import IRLetStmt

        assert len(clean_block.body) == 1
        assert isinstance(clean_block.body[0], IRLetStmt)
        assert clean_block.body[0].name == "x_0"

    def test_let_sequential_indexing(self, clean_block):
        """Test that sequential lets get incremental indices."""
        from fleur.dsl.types import Var

        var1 = graine.let(graine.literal(1), name="a")
        var2 = graine.let(graine.literal(2), name="b")
        var3 = graine.let(graine.literal(3), name="c")

        assert isinstance(var1, Var) and isinstance(var2, Var) and isinstance(var3, Var)
        assert var1.name == "a_0"
        assert var2.name == "b_1"
        assert var3.name == "c_2"


class TestGraineRange:
    """Test graine.range() API."""

    def test_range_with_int_bounds(self):
        """Test range with integer bounds."""
        range_obj = graine.range(0, 10)

        from fleur.dsl.stdlib import Range

        assert isinstance(range_obj, Range)

    def test_range_with_number_bounds(self):
        """Test range with Number bounds."""
        start = graine.literal(5)
        end = graine.literal(15)
        range_obj = graine.range(start, end)

        from fleur.dsl.stdlib import Range

        assert isinstance(range_obj, Range)

    def test_range_iteration(self, clean_block):
        """Test that range can be iterated in a for loop."""
        iterations = []
        for i in graine.range(0, 3):
            iterations.append(i)
            assert isinstance(i, Number)

        # Range iterator yields once (the loop variable), not multiple times
        assert len(iterations) == 1

    def test_range_emits_loop_statement(self, clean_block):
        """Test that range emits a loop statement."""
        for i in graine.range(0, 5):
            pass

        from fleur.dsl.ir import IRRangeStmt

        assert len(clean_block.body) == 1
        assert isinstance(clean_block.body[0], IRRangeStmt)


class TestGraineFunction:
    """Test graine.function decorator."""

    def test_function_decorator(self, clean_block):
        """Test basic function decoration."""

        @graine.function
        def simple() -> Number:
            return graine.literal(42)

        from fleur.dsl.types import Function

        assert isinstance(simple, Function)
        assert simple.name == "simple"

    def test_function_with_parameters(self, clean_block):
        """Test function with parameters."""
        from fleur.dsl.types import Function

        @graine.function
        def add(x: Number, y: Number) -> Number:
            return x + y

        assert isinstance(add, Function)
        assert len(add.params) == 2
        assert add.params[0][0] == "x"
        assert add.params[1][0] == "y"

    def test_function_emits_definition(self, clean_block):
        """Test that function decorator emits a function definition."""

        @graine.function
        def double(x: Number) -> Number:
            return x + x

        from fleur.dsl.ir import IRFunctionStmt

        assert len(clean_block.body) == 1
        assert isinstance(clean_block.body[0], IRFunctionStmt)
        assert clean_block.body[0].name == "double"

    def test_function_callable(self, clean_block):
        """Test that decorated function is callable."""

        @graine.function
        def get_answer() -> Number:
            return graine.literal(42)

        result = get_answer()
        assert isinstance(result, Number)

    def test_function_call_with_args(self, clean_block):
        """Test calling function with arguments."""

        @graine.function
        def triple(x: Number) -> Number:
            return x + x + x

        arg = graine.literal(10)
        result = triple(arg)

        assert isinstance(result, Number)

    def test_nested_function_calls(self, clean_block):
        """Test nested function calls."""

        @graine.function
        def double(x: Number) -> Number:
            return x + x

        @graine.function
        def quadruple(x: Number) -> Number:
            return double(double(x))

        # Should have emitted both function definitions
        from fleur.dsl.ir import IRFunctionStmt

        func_stmts = [s for s in clean_block.body if isinstance(s, IRFunctionStmt)]
        assert len(func_stmts) == 2


class TestGraineTypeAliases:
    """Test graine type aliases."""

    def test_graine_number_alias(self):
        """Test that graine.Number is an alias to Number type."""
        assert graine.Number is Number

    def test_graine_boolean_alias(self):
        """Test that graine.Boolean is an alias to Boolean type."""
        assert graine.Boolean is Boolean

    def test_graine_string_alias(self):
        """Test that graine.String is an alias to String type."""
        assert graine.String is String


class TestGraineLikeAliases:
    """Test graine *Like type aliases."""

    def test_graine_number_like_alias(self):
        """Test that graine.NumberLike exists."""
        from fleur.dsl.types import NumberLike

        assert graine.NumberLike is NumberLike

    def test_graine_boolean_like_alias(self):
        """Test that graine.BooleanLike exists."""
        from fleur.dsl.types import BooleanLike

        assert graine.BooleanLike is BooleanLike

    def test_graine_string_like_alias(self):
        """Test that graine.StringLike exists."""
        from fleur.dsl.types import StringLike

        assert graine.StringLike is StringLike


class TestDSLIntegration:
    """Test DSL integration scenarios."""

    def test_simple_calculation(self, clean_block):
        """Test a simple calculation using the DSL."""
        x = graine.let(graine.literal(10), name="x")
        y = graine.let(graine.literal(20), name="y")
        x += y

        # Should have emitted let statements and an assignment
        assert len(clean_block.body) == 3

    def test_function_with_loop(self, clean_block):
        """Test function containing a loop."""

        @graine.function
        def sum_range(n: Number) -> Number:
            total = graine.let(graine.literal(0), name="total")
            for i in graine.range(0, n):
                total += i
            return total

        # Should emit function definition
        from fleur.dsl.ir import IRFunctionStmt

        assert any(isinstance(s, IRFunctionStmt) for s in clean_block.body)

    def test_multiple_functions(self, clean_block):
        """Test defining multiple functions."""

        @graine.function
        def double(x: Number) -> Number:
            return x + x

        @graine.function
        def triple(x: Number) -> Number:
            return x + x + x

        from fleur.dsl.ir import IRFunctionStmt

        func_stmts = [s for s in clean_block.body if isinstance(s, IRFunctionStmt)]
        assert len(func_stmts) == 2
        assert func_stmts[0].name == "double"
        assert func_stmts[1].name == "triple"
