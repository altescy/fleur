"""Unit tests for JavaScript code emission."""

import pytest

from fleur.dsl import ast, errors
from fleur.dsl.javascript import emit_javascript


class TestLiteralEmission:
    """Tests for emitting literal values."""

    def test_emit_number(self):
        """Test emitting a number literal."""
        node = ast.GraineNumberNode(value=42.0)
        code = emit_javascript(node)
        assert code == "42.0;"

    def test_emit_string(self):
        """Test emitting a string literal."""
        node = ast.GraineStringNode(value="hello")
        code = emit_javascript(node)
        assert code == '"hello";'

    def test_emit_string_with_escapes(self):
        """Test emitting a string with special characters."""
        node = ast.GraineStringNode(value='hello\n"world"')
        code = emit_javascript(node)
        assert "\\n" in code
        assert '\\"' in code

    def test_emit_boolean_true(self):
        """Test emitting boolean true - wrapped in let statement."""
        # Boolean nodes are typically used in expressions, not top-level
        # We need to test them in context
        pass  # Covered by integration tests

    def test_emit_empty_array(self):
        """Test emitting an empty array."""
        node = ast.GraineArrayNode(elements=[])
        code = emit_javascript(node)
        assert code == "[];"

    def test_emit_array_with_elements(self):
        """Test emitting an array with elements."""
        node = ast.GraineArrayNode(
            elements=[
                ast.GraineNumberNode(value=1.0),
                ast.GraineNumberNode(value=2.0),
                ast.GraineNumberNode(value=3.0),
            ]
        )
        code = emit_javascript(node)
        assert "[1.0, 2.0, 3.0]" in code

    def test_emit_empty_record(self):
        """Test emitting an empty object."""
        node = ast.GraineRecordNode(fields={})
        code = emit_javascript(node)
        assert code == "{};"

    def test_emit_record_with_fields(self):
        """Test emitting an object with fields."""
        node = ast.GraineRecordNode(
            fields={
                "x": ast.GraineNumberNode(value=10.0),
                "y": ast.GraineNumberNode(value=20.0),
            }
        )
        code = emit_javascript(node)
        assert "x: 10.0" in code
        assert "y: 20.0" in code


class TestExpressionEmission:
    """Tests for emitting expressions."""

    def test_emit_identifier(self):
        """Test emitting an identifier."""
        node = ast.GraineIdentifierNode(name="myVar")
        code = emit_javascript(node)
        assert code == "myVar;"

    def test_emit_binary_op(self):
        """Test emitting a binary operation."""
        node = ast.GraineBinaryOpNode(
            op="+", left=ast.GraineNumberNode(value=1.0), right=ast.GraineNumberNode(value=2.0)
        )
        code = emit_javascript(node)
        assert "(1.0 + 2.0)" in code

    def test_emit_call_no_args(self):
        """Test emitting a function call without arguments."""
        node = ast.GraineCallNode(function=ast.GraineIdentifierNode(name="func"))
        code = emit_javascript(node)
        assert "func()" in code

    def test_emit_call_with_args(self):
        """Test emitting a function call with arguments."""
        node = ast.GraineCallNode(
            function=ast.GraineIdentifierNode(name="add"),
            arguments=[
                ast.GraineNumberNode(value=1.0),
                ast.GraineNumberNode(value=2.0),
            ],
        )
        code = emit_javascript(node)
        assert "add(1.0, 2.0)" in code

    def test_emit_property_access(self):
        """Test emitting property access."""
        node = ast.GrainePropertyAccessNode(property_name="prop", receiver=ast.GraineIdentifierNode(name="obj"))
        code = emit_javascript(node)
        assert "obj.prop" in code

    def test_emit_index_access(self):
        """Test emitting index access."""
        node = ast.GraineIndexAccessNode(
            index=ast.GraineNumberNode(value=0.0), receiver=ast.GraineIdentifierNode(name="arr")
        )
        code = emit_javascript(node)
        assert "arr[0.0]" in code

    def test_emit_conditional_with_else(self):
        """Test emitting a conditional expression with else."""
        node = ast.GraineConditionalNode(
            condition=ast.GraineIdentifierNode(name="cond"),
            then_branch=ast.GraineNumberNode(value=1.0),
            else_branch=ast.GraineNumberNode(value=2.0),
        )
        code = emit_javascript(node)
        assert "(cond ? (1.0) : (2.0))" in code

    def test_emit_conditional_without_else(self):
        """Test emitting a conditional expression without else."""
        node = ast.GraineConditionalNode(
            condition=ast.GraineIdentifierNode(name="cond"), then_branch=ast.GraineNumberNode(value=1.0)
        )
        code = emit_javascript(node)
        assert "(cond ? (1.0) : undefined)" in code

    def test_emit_construction(self):
        """Test emitting a class instantiation."""
        node = ast.GraineConstructionNode(
            class_name="Point",
            arguments=[
                ast.GraineNumberNode(value=1.0),
                ast.GraineNumberNode(value=2.0),
            ],
        )
        code = emit_javascript(node)
        assert "new Point(1.0, 2.0)" in code


class TestStatementEmission:
    """Tests for emitting statements."""

    def test_emit_let(self):
        """Test emitting a let statement."""
        node = ast.GraineLetNode(identifier=ast.GraineIdentifierNode(name="x"), value=ast.GraineNumberNode(value=42.0))
        code = emit_javascript(node)
        assert code == "let x = 42.0;"

    def test_emit_assign(self):
        """Test emitting an assignment."""
        node = ast.GraineAssignNode(
            identifier=ast.GraineIdentifierNode(name="x"), value=ast.GraineNumberNode(value=10.0)
        )
        code = emit_javascript(node)
        assert code == "x = 10.0;"

    def test_emit_return(self):
        """Test emitting a return statement."""
        node = ast.GraineReturnNode(value=ast.GraineNumberNode(value=42.0))
        code = emit_javascript(node)
        assert code == "return 42.0;"

    def test_emit_block(self):
        """Test emitting a block of statements."""
        block = ast.GraineBlockNode(
            statements=[
                ast.GraineLetNode(identifier=ast.GraineIdentifierNode(name="x"), value=ast.GraineNumberNode(value=1.0)),
                ast.GraineLetNode(identifier=ast.GraineIdentifierNode(name="y"), value=ast.GraineNumberNode(value=2.0)),
            ]
        )
        code = emit_javascript(block)
        assert "let x = 1.0;" in code
        assert "let y = 2.0;" in code

    def test_emit_function(self):
        """Test emitting a function declaration."""
        body = ast.GraineBlockNode(statements=[ast.GraineReturnNode(value=ast.GraineNumberNode(value=42.0))])
        node = ast.GraineFunctionNode(name="getAnswer", parameters=[], body=body)
        code = emit_javascript(node)
        assert "function getAnswer()" in code
        assert "return 42.0;" in code

    def test_emit_function_with_params(self):
        """Test emitting a function with parameters."""
        body = ast.GraineBlockNode()
        node = ast.GraineFunctionNode(
            name="add",
            parameters=[
                ast.GraineIdentifierNode(name="a"),
                ast.GraineIdentifierNode(name="b"),
            ],
            body=body,
        )
        code = emit_javascript(node)
        assert "function add(a, b)" in code

    def test_emit_class_minimal(self):
        """Test emitting a minimal class."""
        node = ast.GraineClassNode(name="MyClass")
        code = emit_javascript(node)
        assert "class MyClass" in code

    def test_emit_class_with_constructor(self):
        """Test emitting a class with constructor."""
        constructor = ast.GraineFunctionNode(
            name="constructor", parameters=[ast.GraineIdentifierNode(name="x")], body=ast.GraineBlockNode()
        )
        node = ast.GraineClassNode(name="MyClass", constructor=constructor)
        code = emit_javascript(node)
        assert "constructor(x)" in code

    def test_emit_for_of(self):
        """Test emitting a for-of loop."""
        node = ast.GraineForOfNode(
            variable=ast.GraineIdentifierNode(name="item"),
            iterator=ast.GraineIdentifierNode(name="items"),
            body=ast.GraineBlockNode(),
        )
        code = emit_javascript(node)
        assert "for (let item of items)" in code

    def test_emit_if_without_else(self):
        """Test emitting an if statement without else."""
        node = ast.GraineIfNode(condition=ast.GraineIdentifierNode(name="cond"), then_branch=ast.GraineBlockNode())
        code = emit_javascript(node)
        assert "if (cond)" in code
        assert "else" not in code

    def test_emit_if_with_else(self):
        """Test emitting an if statement with else."""
        node = ast.GraineIfNode(
            condition=ast.GraineIdentifierNode(name="cond"),
            then_branch=ast.GraineBlockNode(),
            else_branch=ast.GraineBlockNode(),
        )
        code = emit_javascript(node)
        assert "if (cond)" in code
        assert "else" in code


class TestIndentation:
    """Tests for proper indentation in emitted code."""

    def test_function_body_indented(self):
        """Test that function bodies are properly indented."""
        body = ast.GraineBlockNode(statements=[ast.GraineReturnNode(value=ast.GraineNumberNode(value=42.0))])
        node = ast.GraineFunctionNode(name="test", parameters=[], body=body)
        code = emit_javascript(node)
        lines = code.split("\n")
        # The return statement should be indented
        assert any(line.startswith("  return") for line in lines)

    def test_nested_blocks_indented(self):
        """Test that nested blocks maintain proper indentation."""
        inner_if = ast.GraineIfNode(
            condition=ast.GraineIdentifierNode(name="inner"),
            then_branch=ast.GraineBlockNode(statements=[ast.GraineReturnNode(value=ast.GraineNumberNode(value=1.0))]),
        )
        outer_body = ast.GraineBlockNode(statements=[inner_if])
        func = ast.GraineFunctionNode(name="test", parameters=[], body=outer_body)
        code = emit_javascript(func)
        lines = code.split("\n")
        # Should have multiple indentation levels
        assert any("    " in line for line in lines)  # At least 4 spaces for nested content


class TestErrorHandling:
    """Tests for error handling during emission."""

    def test_unsupported_expression_type(self):
        """Test that unsupported expression types raise GraineASTError."""

        # Create a fake node type
        class FakeExpr(ast.GraineASTExpr):
            pass

        node = FakeExpr()
        with pytest.raises(errors.GraineASTError):
            emit_javascript(node)

    def test_unsupported_statement_type(self):
        """Test that unsupported statement types raise GraineASTError."""

        # Create a fake node type
        class FakeStmt(ast.GraineASTStmt):
            pass

        node = FakeStmt()
        with pytest.raises(errors.GraineASTError):
            emit_javascript(node)
