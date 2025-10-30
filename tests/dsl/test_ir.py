"""Tests for the Intermediate Representation (IR) module."""

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


class TestIRExpressions:
    """Test IR expression nodes."""

    def test_literal_number_expr_int(self):
        """Test integer literal expression."""
        expr = IRLiteralNumberExpr(42)
        assert expr.value == 42

    def test_literal_number_expr_float(self):
        """Test float literal expression."""
        expr = IRLiteralNumberExpr(3.14)
        assert expr.value == 3.14

    def test_literal_boolean_expr_true(self):
        """Test boolean true literal expression."""
        expr = IRLiteralBooleanExpr(True)
        assert expr.value is True

    def test_literal_boolean_expr_false(self):
        """Test boolean false literal expression."""
        expr = IRLiteralBooleanExpr(False)
        assert expr.value is False

    def test_literal_string_expr(self):
        """Test string literal expression."""
        expr = IRLiteralStringExpr("hello")
        assert expr.value == "hello"

    def test_literal_string_expr_empty(self):
        """Test empty string literal expression."""
        expr = IRLiteralStringExpr("")
        assert expr.value == ""

    def test_identifier_expr(self):
        """Test identifier expression."""
        expr = IRIdentifierExpr("my_var")
        assert expr.name == "my_var"

    @pytest.mark.parametrize(
        "operator,expected",
        [
            (IRBinaryOperator.ADD, "+"),
            (IRBinaryOperator.SUBTRACT, "-"),
            (IRBinaryOperator.MULTIPLY, "*"),
            (IRBinaryOperator.DIVIDE, "/"),
        ],
    )
    def test_binary_operator_values(self, operator, expected):
        """Test binary operator enum values."""
        assert operator.value == expected

    def test_binary_op_expr(self):
        """Test binary operation expression."""
        left = IRLiteralNumberExpr(10)
        right = IRLiteralNumberExpr(20)
        expr = IRBinaryOpExpr(operator=IRBinaryOperator.ADD, left=left, right=right)

        assert expr.operator == IRBinaryOperator.ADD
        assert expr.left == left
        assert expr.right == right

    def test_binary_op_expr_nested(self):
        """Test nested binary operation expression."""
        # (10 + 20) * 30
        left = IRBinaryOpExpr(
            operator=IRBinaryOperator.ADD,
            left=IRLiteralNumberExpr(10),
            right=IRLiteralNumberExpr(20),
        )
        right = IRLiteralNumberExpr(30)
        expr = IRBinaryOpExpr(operator=IRBinaryOperator.MULTIPLY, left=left, right=right)

        assert expr.operator == IRBinaryOperator.MULTIPLY
        assert isinstance(expr.left, IRBinaryOpExpr)
        assert expr.right == right

    def test_call_expr_no_args(self):
        """Test call expression with no arguments."""
        expr = IRCallExpr(function="foo", args=[])
        assert expr.function == "foo"
        assert expr.args == []

    def test_call_expr_with_args(self):
        """Test call expression with arguments."""
        from fleur.dsl.ir import IRExpr

        args: list[IRExpr] = [IRLiteralNumberExpr(1), IRLiteralNumberExpr(2)]
        expr = IRCallExpr(function="add", args=args)
        assert expr.function == "add"
        assert expr.args == args

    def test_ir_nodes_are_immutable(self):
        """Test that IR nodes are frozen (immutable)."""
        expr = IRLiteralNumberExpr(42)
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            expr.value = 100  # type: ignore


class TestIRStatements:
    """Test IR statement nodes."""

    def test_let_stmt(self):
        """Test variable declaration statement."""
        value = IRLiteralNumberExpr(42)
        stmt = IRLetStmt(name="x", value=value)
        assert stmt.name == "x"
        assert stmt.value == value

    def test_assign_stmt(self):
        """Test variable assignment statement."""
        value = IRLiteralNumberExpr(100)
        stmt = IRAssignStmt(name="x", value=value)
        assert stmt.name == "x"
        assert stmt.value == value

    def test_expr_stmt(self):
        """Test expression statement."""
        expr = IRCallExpr(function="print", args=[IRLiteralStringExpr("hello")])
        stmt = IRExprStmt(expr=expr)
        assert stmt.expr == expr

    def test_return_stmt(self):
        """Test return statement."""
        value = IRLiteralNumberExpr(42)
        stmt = IRReturnStmt(value=value)
        assert stmt.value == value

    def test_range_stmt(self):
        """Test range/for-loop statement."""
        start = IRLiteralNumberExpr(0)
        end = IRLiteralNumberExpr(10)
        body = IRBlock(body=[])
        stmt = IRRangeStmt(var="i", start=start, end=end, body=body)

        assert stmt.var == "i"
        assert stmt.start == start
        assert stmt.end == end
        assert stmt.body == body

    def test_function_stmt(self):
        """Test function definition statement."""
        params = ["x", "y"]
        body = IRBlock(body=[IRReturnStmt(IRLiteralNumberExpr(0))])
        stmt = IRFunctionStmt(name="add", params=params, body=body)

        assert stmt.name == "add"
        assert stmt.params == params
        assert stmt.body == body

    def test_block_empty(self):
        """Test empty block."""
        block = IRBlock(body=[])
        assert block.body == []

    def test_block_with_statements(self):
        """Test block with statements."""
        stmts = [
            IRLetStmt(name="x", value=IRLiteralNumberExpr(10)),
            IRReturnStmt(value=IRIdentifierExpr("x")),
        ]
        block = IRBlock(body=stmts)
        assert block.body == stmts

    def test_block_emit(self):
        """Test emitting statements to a block."""
        block = IRBlock(body=[])
        stmt = IRLetStmt(name="x", value=IRLiteralNumberExpr(42))
        block.emit(stmt)

        assert len(block.body) == 1
        assert block.body[0] == stmt

    def test_block_emit_multiple(self):
        """Test emitting multiple statements to a block."""
        block = IRBlock(body=[])
        stmt1 = IRLetStmt(name="x", value=IRLiteralNumberExpr(1))
        stmt2 = IRLetStmt(name="y", value=IRLiteralNumberExpr(2))

        block.emit(stmt1)
        block.emit(stmt2)

        assert len(block.body) == 2
        assert block.body[0] == stmt1
        assert block.body[1] == stmt2


class TestIRComplexStructures:
    """Test complex IR structures."""

    def test_nested_blocks(self):
        """Test nested block structures."""
        inner_block = IRBlock(body=[IRLetStmt(name="inner", value=IRLiteralNumberExpr(1))])
        outer_block = IRBlock(
            body=[
                IRLetStmt(name="outer", value=IRLiteralNumberExpr(2)),
                IRRangeStmt(var="i", start=IRLiteralNumberExpr(0), end=IRLiteralNumberExpr(5), body=inner_block),
            ]
        )

        assert len(outer_block.body) == 2
        assert isinstance(outer_block.body[1], IRRangeStmt)
        assert outer_block.body[1].body == inner_block  # type: ignore

    def test_function_with_complex_body(self):
        """Test function with complex body."""
        body = IRBlock(
            body=[
                IRLetStmt(name="result", value=IRLiteralNumberExpr(0)),
                IRRangeStmt(
                    var="i",
                    start=IRLiteralNumberExpr(1),
                    end=IRIdentifierExpr("n"),
                    body=IRBlock(
                        body=[
                            IRAssignStmt(
                                name="result",
                                value=IRBinaryOpExpr(
                                    operator=IRBinaryOperator.ADD,
                                    left=IRIdentifierExpr("result"),
                                    right=IRIdentifierExpr("i"),
                                ),
                            )
                        ]
                    ),
                ),
                IRReturnStmt(value=IRIdentifierExpr("result")),
            ]
        )

        func = IRFunctionStmt(name="sum_range", params=["n"], body=body)

        assert func.name == "sum_range"
        assert func.params == ["n"]
        assert len(func.body.body) == 3
        assert isinstance(func.body.body[1], IRRangeStmt)
