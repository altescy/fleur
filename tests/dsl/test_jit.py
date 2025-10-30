"""Tests for standard library components."""

from fleur.dsl.ir import IRIdentifierExpr, IRLiteralNumberExpr
from fleur.dsl.jit import Cases, Range
from fleur.dsl.runtime import use_block
from fleur.dsl.types import Number


class TestRange:
    """Test Range implementation."""

    def test_range_creation(self):
        """Test creating a Range object."""
        start = IRLiteralNumberExpr(0)
        end = IRLiteralNumberExpr(10)
        range_obj = Range(var="i", start=start, end=end)

        assert range_obj._var == "i"
        assert range_obj._start == start
        assert range_obj._end == end

    def test_range_iteration_yields_numbers(self):
        """Test that iterating Range yields Number instances."""
        with use_block():
            start = IRLiteralNumberExpr(0)
            end = IRLiteralNumberExpr(5)
            range_obj = Range(var="i", start=start, end=end)

            items = list(range_obj)

        # Should yield exactly one Number (the loop variable)
        assert len(items) == 1
        assert isinstance(items[0], Number)

    def test_range_iteration_uses_correct_variable_name(self):
        """Test that Range uses the correct variable name."""
        with use_block():
            start = IRLiteralNumberExpr(0)
            end = IRLiteralNumberExpr(3)
            range_obj = Range(var="my_index", start=start, end=end)

            items = list(range_obj)

        assert items[0]._expr.name == "my_index"  # type: ignore

    def test_range_emits_loop_statement(self):
        """Test that Range iteration emits a loop statement."""
        with use_block() as block:
            start = IRLiteralNumberExpr(0)
            end = IRLiteralNumberExpr(10)
            range_obj = Range(var="i", start=start, end=end)

            # Consume the iterator
            list(range_obj)

        from fleur.dsl.ir import IRRangeStmt

        assert len(block.body) == 1
        assert isinstance(block.body[0], IRRangeStmt)
        assert block.body[0].var == "i"
        assert block.body[0].start == start
        assert block.body[0].end == end

    def test_range_with_identifier_expressions(self):
        """Test Range with identifier expressions as bounds."""
        with use_block() as block:
            start = IRIdentifierExpr("start_var")
            end = IRIdentifierExpr("end_var")
            range_obj = Range(var="j", start=start, end=end)

            list(range_obj)

        from fleur.dsl.ir import IRRangeStmt

        loop_stmt = block.body[0]
        assert isinstance(loop_stmt, IRRangeStmt)
        assert isinstance(loop_stmt.start, IRIdentifierExpr)
        assert loop_stmt.start.name == "start_var"  # type: ignore
        assert isinstance(loop_stmt.end, IRIdentifierExpr)
        assert loop_stmt.end.name == "end_var"  # type: ignore

    def test_range_body_is_separate_block(self):
        """Test that Range creates a separate block for its body."""
        with use_block() as outer_block:
            range_obj = Range(var="i", start=IRLiteralNumberExpr(0), end=IRLiteralNumberExpr(5))

            # Iterate and do something in the loop
            for i in range_obj:
                # The loop variable is a Number
                assert isinstance(i, Number)

        from fleur.dsl.ir import IRRangeStmt

        loop_stmt = outer_block.body[0]
        assert isinstance(loop_stmt, IRRangeStmt)
        # The loop body should be a separate block
        assert loop_stmt.body is not outer_block

    def test_nested_ranges(self):
        """Test nested Range iterations."""
        with use_block() as block:
            outer_range = Range(var="i", start=IRLiteralNumberExpr(0), end=IRLiteralNumberExpr(3))

            for i in outer_range:
                inner_range = Range(var="j", start=IRLiteralNumberExpr(0), end=IRLiteralNumberExpr(2))
                for j in inner_range:
                    # Both should be Numbers
                    assert isinstance(i, Number)
                    assert isinstance(j, Number)

        from fleur.dsl.ir import IRRangeStmt

        # Outer block should have one loop
        assert len(block.body) == 1
        outer_loop = block.body[0]
        assert isinstance(outer_loop, IRRangeStmt)
        assert outer_loop.var == "i"

        # Inner loop should be in the outer loop's body
        assert len(outer_loop.body.body) == 1
        inner_loop = outer_loop.body.body[0]
        assert isinstance(inner_loop, IRRangeStmt)
        assert inner_loop.var == "j"

    def test_range_in_function_context(self):
        """Test Range usage within a function definition context."""
        from fleur.dsl import graine

        with use_block() as block:

            @graine.define
            def test_func(n: Number) -> Number:
                total = graine.let(graine.literal(0), name="total")
                for i in graine.range(0, n):
                    total += i
                return total

        from fleur.dsl.ir import IRFunctionStmt

        # Should have a function with a loop inside
        assert len(block.body) == 1
        func_stmt = block.body[0]
        assert isinstance(func_stmt, IRFunctionStmt)

        # Function body should contain a loop
        from fleur.dsl.ir import IRRangeStmt

        loop_stmts = [s for s in func_stmt.body.body if isinstance(s, IRRangeStmt)]
        assert len(loop_stmts) == 1


class TestCases:
    """Test Cases statement implementation."""

    def test_cases_creation(self):
        """Test creating a Cases object."""
        cases = Cases()
        assert cases._whens == []

    def test_cases_with_single_when(self):
        """Test cases with single when clause."""
        from fleur.dsl import graine

        with use_block() as block:
            x = graine.let(10, name="x")

            with graine.cases() as when:
                with when(x > 5):
                    graine.let(100, name="result")  # noqa: F841

        from fleur.dsl.ir import IRIfStmt

        assert len(block.body) == 2
        if_stmt = block.body[1]
        assert isinstance(if_stmt, IRIfStmt)
        assert if_stmt.else_body is None

    def test_cases_with_multiple_whens(self):
        """Test cases with multiple when clauses."""
        from fleur.dsl import graine

        with use_block() as block:
            x = graine.let(10, name="x")

            with graine.cases() as when:
                with when(x < 0):
                    graine.let(-1, name="neg")  # noqa: F841
                with when(x == 0):
                    graine.let(0, name="zero")  # noqa: F841
                with when(x > 0):
                    graine.let(1, name="pos")  # noqa: F841

        from fleur.dsl.ir import IRIfStmt

        # Should have let and if statement
        assert len(block.body) == 2
        if_stmt = block.body[1]
        assert isinstance(if_stmt, IRIfStmt)

        # Check nested structure: if -> else -> if -> else -> if
        assert if_stmt.else_body is not None
        assert len(if_stmt.else_body.body) == 1
        second_if = if_stmt.else_body.body[0]
        assert isinstance(second_if, IRIfStmt)
        assert second_if.else_body is not None

    def test_cases_with_default(self):
        """Test cases with default when clause."""
        from fleur.dsl import graine

        with use_block() as block:
            x = graine.let(10, name="x")

            with graine.cases() as when:
                with when(x < 0):
                    graine.let(-1, name="result")  # noqa: F841
                with when.default():
                    graine.let(0, name="result_default")  # noqa: F841

        from fleur.dsl.ir import IRIfStmt

        assert len(block.body) == 2
        if_stmt = block.body[1]
        assert isinstance(if_stmt, IRIfStmt)
        # Default when should be in else body
        assert if_stmt.else_body is not None

    def test_cases_in_function(self):
        """Test cases inside function."""
        from fleur.dsl import graine

        with use_block() as block:

            @graine.define
            def sign(x: Number) -> Number:
                result = graine.let(0, name="result")

                with graine.cases() as when:
                    with when(x < 0):
                        result = graine.let(-1, name="result")  # noqa: F841
                    with when(x == 0):
                        result = graine.let(0, name="result")  # noqa: F841
                    with when.default():
                        result = graine.let(1, name="result")  # noqa: F841

                return result

        from fleur.dsl.ir import IRFunctionStmt, IRIfStmt

        assert len(block.body) == 1
        func_stmt = block.body[0]
        assert isinstance(func_stmt, IRFunctionStmt)

        # Function should contain let and if statements
        assert len(func_stmt.body.body) >= 2
        # Find the if statement
        if_stmts = [s for s in func_stmt.body.body if isinstance(s, IRIfStmt)]
        assert len(if_stmts) == 1
