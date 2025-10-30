"""Tests for standard library components."""

from fleur.dsl.ir import IRIdentifierExpr, IRLiteralNumberExpr
from fleur.dsl.runtime import use_block
from fleur.dsl.stdlib import Range
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

            @graine.function
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
