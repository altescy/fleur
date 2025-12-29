import pytest

from fleur.js import ast
from fleur.js.emitter import ES2022Emitter


class TestES2022Emitter:
    @pytest.mark.parametrize(
        "ast, expected",
        [
            pytest.param(
                ast.BreakStatement(),
                "break;",
                id="break statement",
            ),
            pytest.param(
                ast.ContinueStatement(),
                "continue;",
                id="continue statement",
            ),
            pytest.param(
                ast.VariableDeclarationStatement(
                    kind=ast.VariableDeclarationKind.LET,
                    identifier=ast.Identifier(name="x"),
                    initializer=ast.NumberLiteral(value=10),
                ),
                "let x=10;",
                id="variable declaration",
            ),
            pytest.param(
                ast.FunctionDeclarationStatement(
                    name="add",
                    parameters=(
                        ast.Identifier(name="a"),
                        ast.Identifier(name="b"),
                    ),
                    body=ast.BlockStatement(
                        statements=(
                            ast.ReturnStatement(
                                argument=ast.BinaryExpression(
                                    operator=ast.BinaryOperator.ADD,
                                    left=ast.Identifier(name="a"),
                                    right=ast.Identifier(name="b"),
                                )
                            ),
                        )
                    ),
                ),
                "function add(a,b){return a+b;}",
                id="function declaration",
            ),
            pytest.param(
                ast.IfStatement(
                    condition=ast.BinaryExpression(
                        operator=ast.BinaryOperator.GREATER_THAN,
                        left=ast.Identifier(name="x"),
                        right=ast.NumberLiteral(value=0),
                    ),
                    consequent=ast.BlockStatement(
                        statements=(
                            ast.ExpressionStatement(
                                expression=ast.CallExpression(
                                    callee=ast.PropertyAccessExpression(
                                        object=ast.Identifier(name="console"),
                                        property="log",
                                    ),
                                    arguments=(ast.StringLiteral(value="Positive"),),
                                )
                            ),
                        )
                    ),
                    alternate=ast.BlockStatement(
                        statements=(
                            ast.ExpressionStatement(
                                expression=ast.CallExpression(
                                    callee=ast.PropertyAccessExpression(
                                        object=ast.Identifier(name="console"),
                                        property="log",
                                    ),
                                    arguments=(ast.StringLiteral(value="Non-positive"),),
                                )
                            ),
                        )
                    ),
                ),
                'if(x>0){console.log("Positive");}else{console.log("Non-positive");}',
                id="if statement with else",
            ),
        ],
    )
    @staticmethod
    def test_emit_statements(ast: ast.Statement, expected: str):
        emitter = ES2022Emitter(config="minify")
        result = emitter(ast)
        assert result == expected
