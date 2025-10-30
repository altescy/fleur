"""Tests for JavaScript code generation."""

import pytest

from fleur.dsl.ir import (
    IRAssignStmt,
    IRBinaryOperator,
    IRBinaryOpExpr,
    IRBlock,
    IRCallExpr,
    IRExprStmt,
    IRFunctionStmt,
    IRIdentifierExpr,
    IRLetStmt,
    IRLiteralBooleanExpr,
    IRLiteralNumberExpr,
    IRLiteralStringExpr,
    IRRangeStmt,
    IRReturnStmt,
)
from fleur.dsl.javascript import emit_javascript


class TestEmitExpressions:
    """Test JavaScript emission for expressions."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (42, "42"),
            (0, "0"),
            (-10, "-10"),
            (3.14, "3.14"),
            (-2.5, "-2.5"),
        ],
    )
    def test_emit_literal_number(self, value, expected):
        """Test emitting number literals."""
        expr = IRLiteralNumberExpr(value)
        result = emit_javascript(expr)
        assert result == f"{expected};"

    @pytest.mark.parametrize(
        "value,expected",
        [
            (True, "true"),
            (False, "false"),
        ],
    )
    def test_emit_literal_boolean(self, value, expected):
        """Test emitting boolean literals."""
        expr = IRLiteralBooleanExpr(value)
        result = emit_javascript(expr)
        assert result == f"{expected};"

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("hello", '"hello"'),
            ("", '""'),
            ("hello world", '"hello world"'),
        ],
    )
    def test_emit_literal_string(self, value, expected):
        """Test emitting string literals."""
        expr = IRLiteralStringExpr(value)
        result = emit_javascript(expr)
        assert result == f"{expected};"

    def test_emit_identifier(self):
        """Test emitting identifier."""
        expr = IRIdentifierExpr("my_var")
        result = emit_javascript(expr)
        assert result == "my_var;"

    @pytest.mark.parametrize(
        "operator,expected_op",
        [
            (IRBinaryOperator.ADD, "+"),
            (IRBinaryOperator.SUBTRACT, "-"),
            (IRBinaryOperator.MULTIPLY, "*"),
            (IRBinaryOperator.DIVIDE, "/"),
        ],
    )
    def test_emit_binary_operation(self, operator, expected_op):
        """Test emitting binary operations."""
        left = IRLiteralNumberExpr(10)
        right = IRLiteralNumberExpr(20)
        expr = IRBinaryOpExpr(operator=operator, left=left, right=right)
        result = emit_javascript(expr)
        assert result == f"(10 {expected_op} 20);"

    def test_emit_nested_binary_operation(self):
        """Test emitting nested binary operations."""
        # (10 + 20) * 30
        inner = IRBinaryOpExpr(
            operator=IRBinaryOperator.ADD,
            left=IRLiteralNumberExpr(10),
            right=IRLiteralNumberExpr(20),
        )
        expr = IRBinaryOpExpr(operator=IRBinaryOperator.MULTIPLY, left=inner, right=IRLiteralNumberExpr(30))
        result = emit_javascript(expr)
        assert result == "((10 + 20) * 30);"

    def test_emit_call_no_args(self):
        """Test emitting function call with no arguments."""
        expr = IRCallExpr(function="foo", args=[])
        result = emit_javascript(expr)
        assert result == "foo();"

    def test_emit_call_with_args(self):
        """Test emitting function call with arguments."""
        from fleur.dsl.ir import IRExpr

        args: list[IRExpr] = [IRLiteralNumberExpr(1), IRLiteralNumberExpr(2), IRLiteralNumberExpr(3)]
        expr = IRCallExpr(function="add", args=args)
        result = emit_javascript(expr)
        assert result == "add(1, 2, 3);"

    def test_emit_call_with_expression_args(self):
        """Test emitting function call with expression arguments."""
        args = [
            IRBinaryOpExpr(
                operator=IRBinaryOperator.ADD,
                left=IRLiteralNumberExpr(1),
                right=IRLiteralNumberExpr(2),
            ),
            IRIdentifierExpr("x"),
        ]
        expr = IRCallExpr(function="process", args=args)
        result = emit_javascript(expr)
        assert result == "process((1 + 2), x);"


class TestEmitStatements:
    """Test JavaScript emission for statements."""

    def test_emit_let_stmt(self):
        """Test emitting variable declaration."""
        stmt = IRLetStmt(name="x", value=IRLiteralNumberExpr(42))
        result = emit_javascript(stmt)
        assert result == "let x = 42;\n"

    def test_emit_assign_stmt(self):
        """Test emitting variable assignment."""
        stmt = IRAssignStmt(name="x", value=IRLiteralNumberExpr(100))
        result = emit_javascript(stmt)
        assert result == "x = 100;\n"

    def test_emit_expr_stmt(self):
        """Test emitting expression statement."""
        expr = IRCallExpr(function="console.log", args=[IRLiteralStringExpr("hello")])
        stmt = IRExprStmt(expr=expr)
        result = emit_javascript(stmt)
        assert result == 'console.log("hello");\n'

    def test_emit_return_stmt(self):
        """Test emitting return statement."""
        stmt = IRReturnStmt(value=IRLiteralNumberExpr(42))
        result = emit_javascript(stmt)
        assert result == "return 42;\n"

    def test_emit_range_stmt_simple(self):
        """Test emitting simple range statement."""
        body = IRBlock(body=[IRExprStmt(expr=IRIdentifierExpr("i"))])
        stmt = IRRangeStmt(var="i", start=IRLiteralNumberExpr(0), end=IRLiteralNumberExpr(10), body=body)
        result = emit_javascript(stmt)

        expected = "for (let i = 0; i < 10; i++) {\n  i;\n}\n"
        assert result == expected

    def test_emit_range_stmt_with_identifier_bounds(self):
        """Test emitting range with identifier bounds."""
        body = IRBlock(body=[])
        stmt = IRRangeStmt(var="i", start=IRIdentifierExpr("start"), end=IRIdentifierExpr("end"), body=body)
        result = emit_javascript(stmt)

        expected = "for (let i = start; i < end; i++) {\n}\n"
        assert result == expected

    def test_emit_function_stmt_no_params(self):
        """Test emitting function with no parameters."""
        body = IRBlock(body=[IRReturnStmt(value=IRLiteralNumberExpr(42))])
        stmt = IRFunctionStmt(name="get_answer", params=[], body=body)
        result = emit_javascript(stmt)

        expected = "function get_answer() {\n  return 42;\n}\n"
        assert result == expected

    def test_emit_function_stmt_with_params(self):
        """Test emitting function with parameters."""
        body = IRBlock(
            body=[
                IRReturnStmt(
                    value=IRBinaryOpExpr(
                        operator=IRBinaryOperator.ADD,
                        left=IRIdentifierExpr("x"),
                        right=IRIdentifierExpr("y"),
                    )
                )
            ]
        )
        stmt = IRFunctionStmt(name="add", params=["x", "y"], body=body)
        result = emit_javascript(stmt)

        expected = "function add(x, y) {\n  return (x + y);\n}\n"
        assert result == expected

    def test_emit_block_empty(self):
        """Test emitting empty block."""
        block = IRBlock(body=[])
        result = emit_javascript(block)
        assert result == ""

    def test_emit_block_multiple_statements(self):
        """Test emitting block with multiple statements."""
        block = IRBlock(
            body=[
                IRLetStmt(name="x", value=IRLiteralNumberExpr(10)),
                IRLetStmt(name="y", value=IRLiteralNumberExpr(20)),
                IRReturnStmt(
                    value=IRBinaryOpExpr(
                        operator=IRBinaryOperator.ADD,
                        left=IRIdentifierExpr("x"),
                        right=IRIdentifierExpr("y"),
                    )
                ),
            ]
        )
        result = emit_javascript(block)

        expected = "let x = 10;\nlet y = 20;\nreturn (x + y);\n"
        assert result == expected


class TestEmitComplexStructures:
    """Test JavaScript emission for complex structures."""

    def test_emit_nested_loops(self):
        """Test emitting nested loops."""
        inner_body = IRBlock(
            body=[
                IRExprStmt(
                    expr=IRCallExpr(
                        function="console.log",
                        args=[IRIdentifierExpr("i"), IRIdentifierExpr("j")],
                    )
                )
            ]
        )
        inner_loop = IRRangeStmt(var="j", start=IRLiteralNumberExpr(0), end=IRLiteralNumberExpr(3), body=inner_body)
        outer_body = IRBlock(body=[inner_loop])
        outer_loop = IRRangeStmt(var="i", start=IRLiteralNumberExpr(0), end=IRLiteralNumberExpr(2), body=outer_body)

        result = emit_javascript(outer_loop)

        expected = "for (let i = 0; i < 2; i++) {\n  for (let j = 0; j < 3; j++) {\n    console.log(i, j);\n  }\n}\n"
        assert result == expected

    def test_emit_function_with_loop(self):
        """Test emitting function containing a loop."""
        loop_body = IRBlock(
            body=[
                IRAssignStmt(
                    name="sum",
                    value=IRBinaryOpExpr(
                        operator=IRBinaryOperator.ADD,
                        left=IRIdentifierExpr("sum"),
                        right=IRIdentifierExpr("i"),
                    ),
                )
            ]
        )
        func_body = IRBlock(
            body=[
                IRLetStmt(name="sum", value=IRLiteralNumberExpr(0)),
                IRRangeStmt(var="i", start=IRLiteralNumberExpr(1), end=IRIdentifierExpr("n"), body=loop_body),
                IRReturnStmt(value=IRIdentifierExpr("sum")),
            ]
        )
        func = IRFunctionStmt(name="sum_range", params=["n"], body=func_body)

        result = emit_javascript(func)

        expected = (
            "function sum_range(n) {\n"
            "  let sum = 0;\n"
            "  for (let i = 1; i < n; i++) {\n"
            "    sum = (sum + i);\n"
            "  }\n"
            "  return sum;\n"
            "}\n"
        )
        assert result == expected

    def test_emit_multiple_functions(self):
        """Test emitting multiple functions."""
        func1 = IRFunctionStmt(
            name="double",
            params=["x"],
            body=IRBlock(
                body=[
                    IRReturnStmt(
                        value=IRBinaryOpExpr(
                            operator=IRBinaryOperator.MULTIPLY,
                            left=IRIdentifierExpr("x"),
                            right=IRLiteralNumberExpr(2),
                        )
                    )
                ]
            ),
        )

        func2 = IRFunctionStmt(
            name="triple",
            params=["x"],
            body=IRBlock(
                body=[
                    IRReturnStmt(
                        value=IRBinaryOpExpr(
                            operator=IRBinaryOperator.MULTIPLY,
                            left=IRIdentifierExpr("x"),
                            right=IRLiteralNumberExpr(3),
                        )
                    )
                ]
            ),
        )

        result = emit_javascript(func1, func2)

        expected = "function double(x) {\n  return (x * 2);\n}\n\nfunction triple(x) {\n  return (x * 3);\n}\n"
        assert result == expected

    def test_emit_preserves_indentation(self):
        """Test that indentation is properly preserved in nested structures."""
        deeply_nested = IRBlock(
            body=[
                IRRangeStmt(
                    var="i",
                    start=IRLiteralNumberExpr(0),
                    end=IRLiteralNumberExpr(3),
                    body=IRBlock(
                        body=[
                            IRRangeStmt(
                                var="j",
                                start=IRLiteralNumberExpr(0),
                                end=IRLiteralNumberExpr(2),
                                body=IRBlock(body=[IRLetStmt(name="x", value=IRLiteralNumberExpr(42))]),
                            )
                        ]
                    ),
                )
            ]
        )

        result = emit_javascript(deeply_nested)

        # Check that indentation increases with nesting
        lines = result.split("\n")
        assert lines[0].startswith("for")  # No indent
        assert lines[1].startswith("  for")  # 2 spaces
        assert lines[2].startswith("    let")  # 4 spaces


class TestEmitEdgeCases:
    """Test edge cases in JavaScript emission."""

    def test_emit_unsupported_expr_raises(self):
        """Test that unsupported expression types raise an error."""

        class UnsupportedExpr:
            pass

        with pytest.raises(ValueError, match="Unsupported"):
            emit_javascript(UnsupportedExpr())  # type: ignore

    def test_emit_unsupported_stmt_raises(self):
        """Test that unsupported statement types raise an error."""

        class UnsupportedStmt:
            pass

        with pytest.raises(ValueError, match="Unsupported"):
            emit_javascript(UnsupportedStmt())  # type: ignore
