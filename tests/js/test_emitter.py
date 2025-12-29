import pytest

from fleur.js import ast
from fleur.js.emitter import ES2022Emitter


class TestES2022Emitter:
    @pytest.mark.parametrize(
        "ast, expected",
        [
            pytest.param(
                ast.ExpressionStatement(
                    expression=ast.NumberLiteral(value=42),
                ),
                "42;",
                id="expression statement",
            ),
            pytest.param(
                ast.ExpressionStatement(
                    expression=ast.ArrayLiteral(
                        elements=(
                            ast.NumberLiteral(value=1),
                            ast.NumberLiteral(value=2),
                            ast.NumberLiteral(value=3),
                        ),
                    ),
                ),
                "[1,2,3];",
                id="array literal expression statement",
            ),
            pytest.param(
                ast.ExpressionStatement(
                    ast.ObjectLiteral(
                        properties={
                            "name": ast.StringLiteral(value="Alice"),
                            "age": ast.NumberLiteral(value=30),
                        },
                    ),
                ),
                '{"name":"Alice","age":30};',
                id="object literal statement",
            ),
            pytest.param(
                ast.ExpressionStatement(
                    expression=ast.UnaryExpression(
                        operator=ast.UnaryOperator.NEGATE,
                        operand=ast.NumberLiteral(value=5),
                    ),
                ),
                "-5;",
                id="unary expression statement",
            ),
            pytest.param(
                ast.ExpressionStatement(
                    expression=ast.BinaryExpression(
                        operator=ast.BinaryOperator.MULTIPLY,
                        left=ast.NumberLiteral(value=6),
                        right=ast.NumberLiteral(value=7),
                    ),
                ),
                "6*7;",
                id="binary expression statement",
            ),
            pytest.param(
                ast.ExpressionStatement(
                    expression=ast.CallExpression(
                        callee=ast.Identifier(name="greet"),
                        arguments=(ast.StringLiteral(value="World"),),
                    )
                ),
                'greet("World");',
                id="call expression statement",
            ),
            pytest.param(
                ast.ExpressionStatement(
                    expression=ast.PropertyAccessExpression(
                        object=ast.Identifier(name="console"),
                        property="log",
                    ),
                ),
                "console.log;",
                id="property access expression statement",
            ),
            pytest.param(
                ast.ExpressionStatement(
                    expression=ast.FunctionExpression(
                        parameters=(),
                        body=ast.BlockStatement(statements=()),
                    ),
                ),
                "function(){};",
                id="function expression statement",
            ),
            pytest.param(
                ast.ExpressionStatement(
                    expression=ast.FunctionExpression(
                        parameters=(
                            ast.Identifier(name="x"),
                            ast.Identifier(name="y"),
                        ),
                        body=ast.BlockStatement(
                            statements=(
                                ast.ReturnStatement(
                                    argument=ast.BinaryExpression(
                                        operator=ast.BinaryOperator.ADD,
                                        left=ast.Identifier(name="x"),
                                        right=ast.Identifier(name="y"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                "function(x,y){return x+y;};",
                id="function expression statement",
            ),
            pytest.param(
                ast.ReturnStatement(
                    argument=ast.StringLiteral(value="Hello, World!"),
                ),
                'return "Hello, World!";',
                id="return statement with argument",
            ),
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
