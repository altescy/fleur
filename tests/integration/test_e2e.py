"""End-to-end integration tests."""

from fleur.dsl import emit_javascript, graine
from fleur.dsl.runtime import use_block


class TestEndToEnd:
    """Test complete DSL to JavaScript compilation."""

    def test_simple_function(self):
        """Test compiling a simple function."""
        with use_block() as block:

            @graine.function
            def get_answer() -> graine.Number:
                return graine.literal(42)

            js = emit_javascript(block)

        assert "function get_answer()" in js
        assert "return 42" in js

    def test_function_with_parameters(self):
        """Test compiling a function with parameters."""
        with use_block() as block:

            @graine.function
            def add(x: graine.Number, y: graine.Number) -> graine.Number:
                return x + y

            js = emit_javascript(block)

        assert "function add(x, y)" in js
        assert "return (x + y)" in js

    def test_function_with_loop(self):
        """Test compiling a function with a loop."""
        with use_block() as block:

            @graine.function
            def sum_range(n: graine.Number) -> graine.Number:
                total = graine.let(graine.literal(0), name="total")
                for i in graine.range(0, n):
                    total += i
                return total

            js = emit_javascript(block)

        assert "function sum_range(n)" in js
        assert "let total_0 = 0" in js
        assert "for (let i_" in js
        assert "i_1 < n" in js
        assert "total_0 = (total_0 + i_1)" in js
        assert "return total_0" in js

    def test_nested_loops(self):
        """Test compiling nested loops."""
        with use_block() as block:

            @graine.function
            def nested(n: graine.Number, m: graine.Number) -> graine.Number:
                sum_val = graine.let(graine.literal(0), name="sum")
                for i in graine.range(0, n):
                    for j in graine.range(0, m):
                        sum_val += i + j
                return sum_val

            js = emit_javascript(block)

        assert "function nested(n, m)" in js
        # Both loops use their respective variables
        assert "for (let i_" in js
        # The inner loop variable is also "i_" (different index)
        # Check for nested structure (indentation)
        lines = js.split("\n")
        assert any("  for" in line for line in lines)  # Nested for loop

    def test_multiple_functions(self):
        """Test compiling multiple functions."""
        with use_block() as block:

            @graine.function
            def double(x: graine.Number) -> graine.Number:
                return x + x

            @graine.function
            def quadruple(x: graine.Number) -> graine.Number:
                return double(double(x))

            js = emit_javascript(block)

        assert "function double(x)" in js
        assert "function quadruple(x)" in js
        assert js.index("function double") < js.index("function quadruple")

    def test_arithmetic_operations(self):
        """Test various arithmetic operations."""
        with use_block() as block:

            @graine.function
            def calc(a: graine.Number, b: graine.Number) -> graine.Number:
                sum_val = graine.let(a + b, name="sum")
                diff = graine.let(a - b, name="diff")
                return sum_val + diff

            js = emit_javascript(block)

        assert "let sum_" in js
        assert "let diff_" in js
        assert "(a + b)" in js
        assert "(a - b)" in js

    def test_variable_mutation(self):
        """Test variable mutation with +=."""
        with use_block() as block:

            @graine.function
            def accumulate(n: graine.Number) -> graine.Number:
                acc = graine.let(graine.literal(0), name="acc")
                for i in graine.range(0, n):
                    acc += graine.literal(1)
                return acc

            js = emit_javascript(block)

        assert "let acc_0 = 0" in js
        assert "acc_0 = (acc_0 + 1)" in js

    def test_function_calls_in_expressions(self):
        """Test function calls within expressions."""
        with use_block() as block:

            @graine.function
            def inc(x: graine.Number) -> graine.Number:
                return x + graine.literal(1)

            @graine.function
            def process(n: graine.Number) -> graine.Number:
                result = graine.let(inc(n), name="result")
                return result + graine.literal(10)

            js = emit_javascript(block)

        assert "function inc(x)" in js
        assert "function process(n)" in js
        assert "inc(n)" in js


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_sum_arithmetic_sequence(self):
        """Test the arithmetic sequence sum example."""
        with use_block() as block:

            @graine.function
            def sum_arithmetic_sequence(
                first: graine.Number, diff: graine.Number, count: graine.Number
            ) -> graine.Number:
                total = graine.let(graine.literal(0), name="total")
                current = graine.let(first, name="current")

                for _ in graine.range(0, count):
                    total += current
                    current += diff

                return total

            js = emit_javascript(block)

        assert "function sum_arithmetic_sequence(first, diff, count)" in js
        assert "let total_0 = 0" in js
        assert "let current_1 = first" in js
        assert "total_0 = (total_0 + current_1)" in js
        assert "current_1 = (current_1 + diff)" in js

    def test_triangle_number(self):
        """Test triangle number calculation."""
        with use_block() as block:

            @graine.function
            def sum_range(start: graine.Number, end: graine.Number) -> graine.Number:
                total = graine.let(graine.literal(0), name="total")
                for i in graine.range(start, end):
                    total += i
                return total

            @graine.function
            def triangle_number(n: graine.Number) -> graine.Number:
                return sum_range(graine.literal(1), n + graine.literal(1))

            js = emit_javascript(block)

        assert "function sum_range(start, end)" in js
        assert "function triangle_number(n)" in js
        assert "sum_range(1, (n + 1))" in js

    def test_complex_calculation(self):
        """Test a complex calculation with multiple variables and operations."""
        with use_block() as block:

            @graine.function
            def complex_calc(x: graine.Number, y: graine.Number, z: graine.Number) -> graine.Number:
                a = graine.let(x + y, name="a")
                b = graine.let(y + z, name="b")
                c = graine.let(a + b, name="c")

                result = graine.let(graine.literal(0), name="result")
                for i in graine.range(0, c):
                    temp = graine.let(i + a, name="temp")
                    result += temp

                return result

            js = emit_javascript(block)

        # Verify structure
        assert "function complex_calc(x, y, z)" in js
        assert "let a_" in js
        assert "let b_" in js
        assert "let c_" in js
        assert "let result_" in js
        assert "for (let i_" in js


class TestEdgeCases:
    """Test edge cases in end-to-end compilation."""

    def test_empty_function_body(self):
        """Test function with minimal body."""
        with use_block() as block:

            @graine.function
            def returns_zero() -> graine.Number:
                return graine.literal(0)

            js = emit_javascript(block)

        assert "function returns_zero()" in js
        assert "return 0" in js

    def test_deeply_nested_operations(self):
        """Test deeply nested arithmetic operations."""
        with use_block() as block:

            @graine.function
            def nested_ops(x: graine.Number) -> graine.Number:
                return ((x + graine.literal(1)) + graine.literal(2)) + graine.literal(3)

            js = emit_javascript(block)

        assert "function nested_ops(x)" in js
        # Should have nested parentheses
        assert "(((" in js or "((" in js

    def test_sequential_variable_declarations(self):
        """Test many sequential variable declarations."""
        with use_block() as block:

            @graine.function
            def many_vars() -> graine.Number:
                v1 = graine.let(graine.literal(1), name="v")
                v2 = graine.let(graine.literal(2), name="v")
                v3 = graine.let(graine.literal(3), name="v")
                v4 = graine.let(graine.literal(4), name="v")
                return v1 + v2 + v3 + v4

            js = emit_javascript(block)

        # Should have unique variable names
        assert "let v_0" in js
        assert "let v_1" in js
        assert "let v_2" in js
        assert "let v_3" in js


class TestJavaScriptValidity:
    """Test that generated JavaScript is syntactically valid."""

    def test_proper_semicolons(self):
        """Test that statements have proper semicolons."""
        with use_block() as block:

            @graine.function
            def test_func(x: graine.Number) -> graine.Number:
                y = graine.let(x + graine.literal(1), name="y")
                return y

            js = emit_javascript(block)

        # All statement lines should end with semicolons (except braces)
        lines = [line.strip() for line in js.split("\n") if line.strip() and not line.strip().endswith("{")]
        statement_lines = [line for line in lines if line and not line.endswith("}")]
        for line in statement_lines:
            assert line.endswith(";"), f"Line should end with semicolon: {line}"

    def test_proper_indentation(self):
        """Test that generated code has proper indentation."""
        with use_block() as block:

            @graine.function
            def indented(n: graine.Number) -> graine.Number:
                total = graine.let(graine.literal(0), name="total")
                for i in graine.range(0, n):
                    total += i
                return total

            js = emit_javascript(block)

        lines = js.split("\n")
        # Function body should be indented
        assert any(line.startswith("  ") for line in lines)
        # Loop body should be double-indented
        assert any(line.startswith("    ") for line in lines)

    def test_no_trailing_commas(self):
        """Test that function parameters don't have trailing commas."""
        with use_block() as block:

            @graine.function
            def multi_param(a: graine.Number, b: graine.Number, c: graine.Number) -> graine.Number:
                return a + b + c

            js = emit_javascript(block)

        # Should be "a, b, c)" not "a, b, c,)"
        assert ",)" not in js
