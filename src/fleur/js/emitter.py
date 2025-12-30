import dataclasses
from collections.abc import Mapping
from typing import Literal, Union

from . import ast


@dataclasses.dataclass
class ES2022EmitterConfig:
    indent: str
    space: str
    newline: str


class ES2022Emitter:
    _PRESETS: Mapping[str, ES2022EmitterConfig] = {
        "minify": ES2022EmitterConfig(
            indent="",
            space="",
            newline="",
        ),
        "default": ES2022EmitterConfig(
            indent="  ",
            space=" ",
            newline="\n",
        ),
    }

    def __init__(
        self,
        config: Union[Literal["minify", "default"], ES2022EmitterConfig] = "default",
    ) -> None:
        self._config = ES2022Emitter._PRESETS[config] if isinstance(config, str) else config

    @property
    def _indent(self) -> str:
        return self._config.indent

    @property
    def _space(self) -> str:
        return self._config.space

    @property
    def _newline(self) -> str:
        return self._config.newline

    # Emit Expressions

    def _emit_literal_expression(self, node: ast.LiteralNode) -> str:
        if isinstance(node, ast.NumberLiteral):
            return str(node.value)
        if isinstance(node, ast.StringLiteral):
            return f'"{node.value}"'
        if isinstance(node, ast.BooleanLiteral):
            return "true" if node.value else "false"
        if isinstance(node, ast.NullLiteral):
            return "null"
        if isinstance(node, ast.UndefinedLiteral):
            return "undefined"
        if isinstance(node, ast.ArrayLiteral):
            elements = [self._emit_expression(elem) for elem in node.elements]
            elements_str = f",{self._space}".join(elements)
            return f"[{elements_str}]"
        if isinstance(node, ast.ObjectLiteral):
            props = []
            for key, value in node.properties.items():
                prop_str = f'"{key}":{self._space}{self._emit_expression(value)}'
                props.append(prop_str)
            props_str = f",{self._space}".join(props)
            return f"{{{props_str}}}"
        raise NotImplementedError(f"Unsupported literal node: {type(node)!r}")

    def _emit_identifier_expression(self, node: ast.Identifier) -> str:
        return node.name

    def _emit_unary_expression(self, node: ast.UnaryExpression[ast._JSTypeT]) -> str:
        operator = node.operator.value
        operand = self._emit_expression(node.operand)
        return f"{operator}{operand}"

    def _emit_binary_expression(self, node: ast.BinaryExpression[ast._JSTypeT]) -> str:
        left = self._emit_expression(node.left)
        operator = node.operator.value
        right = self._emit_expression(node.right)
        return f"{left}{self._space}{operator}{self._space}{right}"

    def _emit_call_expression(self, node: ast.CallExpression[ast._JSTypeT]) -> str:
        callee = self._emit_expression(node.callee)
        args = ", ".join(self._emit_expression(arg) for arg in node.arguments)
        return f"{callee}({args})"

    def _emit_property_access_expression(self, node: ast.PropertyAccessExpression[ast._JSTypeT]) -> str:
        obj = self._emit_expression(node.object)
        prop = node.property
        return f"{obj}.{prop}"

    def _emit_key_access_expression(self, node: ast.KeyAccessExpression[ast._JSTypeT]) -> str:
        obj = self._emit_expression(node.object)
        key = self._emit_expression(node.key)
        return f"{obj}[{key}]"

    def _emit_function_expression(self, node: ast.FunctionExpression) -> str:
        params = f",{self._space}".join(self._emit_identifier_expression(param) for param in node.parameters)
        body = self(node.body)
        return f"function({params}){self._space}{body}"

    def _emit_parenthesized_expression(self, node: ast.ParenthesizedExpression[ast._JSTypeT]) -> str:
        expr = self._emit_expression(node.expression)
        return f"({expr})"

    def _emit_assignment_expression(self, node: ast.AssignmentExpression[ast._JSTypeT]) -> str:
        target = self._emit_expression(node.target)
        value = self._emit_expression(node.value)
        return f"{target}{self._space}={self._space}{value}"

    def _emit_conditional_expression(self, node: ast.ConditionalExpression[ast._JSTypeT]) -> str:
        condition = self._emit_expression(node.condition)
        consequent = self._emit_expression(node.consequent)
        alternate = self._emit_expression(node.alternate)
        return f"{condition}{self._space}?{self._space}{consequent}{self._space}:{self._space}{alternate}"

    def _emit_expression(self, node: ast.Expression[ast.JSType]) -> str:
        if isinstance(node, ast.LiteralNode):
            return self._emit_literal_expression(node)
        if isinstance(node, ast.Identifier):
            return self._emit_identifier_expression(node)
        if isinstance(node, ast.UnaryExpression):
            return self._emit_unary_expression(node)
        if isinstance(node, ast.BinaryExpression):
            return self._emit_binary_expression(node)
        if isinstance(node, ast.CallExpression):
            return self._emit_call_expression(node)
        if isinstance(node, ast.PropertyAccessExpression):
            return self._emit_property_access_expression(node)
        if isinstance(node, ast.KeyAccessExpression):
            return self._emit_key_access_expression(node)
        if isinstance(node, ast.FunctionExpression):
            return self._emit_function_expression(node)
        if isinstance(node, ast.ParenthesizedExpression):
            return self._emit_parenthesized_expression(node)
        if isinstance(node, ast.AssignmentExpression):
            return self._emit_assignment_expression(node)
        if isinstance(node, ast.ConditionalExpression):
            return self._emit_conditional_expression(node)
        raise NotImplementedError(f"Unsupported expression node: {type(node)!r}")

    # Emit Statements

    def _emit_expression_statement(self, node: ast.ExpressionStatement) -> list[str]:
        expr = self._emit_expression(node.expression)
        return [f"{expr};"]

    def _emit_return_statement(self, node: ast.ReturnStatement) -> list[str]:
        if node.argument is None:
            return ["return;"]
        expr = self._emit_expression(node.argument)
        return [f"return {expr};"]

    def _emit_variable_declaration(self, node: ast.VariableDeclarationStatement) -> list[str]:
        identifier = self._emit_identifier_expression(node.identifier)
        initializer = self._emit_expression(node.initializer)
        return [f"{node.kind.value} {identifier}{self._space}={self._space}{initializer};"]

    def _emit_function_declaration(self, node: ast.FunctionDeclarationStatement) -> list[str]:
        name = node.name
        params = f",{self._space}".join(self._emit_identifier_expression(param) for param in node.parameters)
        body = self(node.body)
        return [f"function {name}({params}){self._space}{body}"]

    def _emit_if_statement(self, node: ast.IfStatement) -> list[str]:
        condition = self._emit_expression(node.condition)
        consequent = self(node.consequent)
        statement = f"if{self._space}({condition}){self._space}{consequent}"
        if node.alternate:
            statement = f"{statement}{self._space}else{self._space}{self(node.alternate)}"
        return [statement]

    def _emit_for_statement(self, node: ast.ForStatement) -> list[str]:
        init = self(node.initializer).rstrip(";") if node.initializer else ""
        condition = self._emit_expression(node.condition) if node.condition else ""
        increment = self._emit_expression(node.increment) if node.increment else ""
        body = self(node.body)
        return [f"for{self._space}({init};{self._space}{condition};{self._space}{increment}){self._space}{body}"]

    def _emit_forof_statement(self, node: ast.ForOfStatement) -> list[str]:
        iterator = self._emit_identifier_expression(node.iterator)
        iterable = self._emit_expression(node.iterable)
        body = self(node.body)
        return [f"for{self._space}(let {iterator} of {iterable}){self._space}{body}"]

    def _emit_forin_statement(self, node: ast.ForInStatement) -> list[str]:
        iterator = self._emit_identifier_expression(node.iterator)
        object_expr = self._emit_expression(node.object)
        body = self(node.body)
        return [f"for{self._space}(let {iterator} in {object_expr}){self._space}{body}"]

    def _emit_break_statement(self, node: ast.BreakStatement) -> list[str]:
        return ["break;"]

    def _emit_continue_statement(self, node: ast.ContinueStatement) -> list[str]:
        return ["continue;"]

    def _emit_block_statement(self, node: ast.BlockStatement, level: int) -> list[str]:
        indent = self._indent * level
        lines = [indent + "{"]
        for statement in node.statements:
            stmt_lines = self._emit_statement(statement, level + 1)
            for line in stmt_lines:
                lines.append(f"{indent}{self._indent}{line}")
        lines.append(indent + "}")
        return lines

    def _emit_statement(self, node: ast.Statement, level: int) -> list[str]:
        if isinstance(node, ast.ExpressionStatement):
            return self._emit_expression_statement(node)
        if isinstance(node, ast.ReturnStatement):
            return self._emit_return_statement(node)
        if isinstance(node, ast.VariableDeclarationStatement):
            return self._emit_variable_declaration(node)
        if isinstance(node, ast.FunctionDeclarationStatement):
            return self._emit_function_declaration(node)
        if isinstance(node, ast.IfStatement):
            return self._emit_if_statement(node)
        if isinstance(node, ast.ForStatement):
            return self._emit_for_statement(node)
        if isinstance(node, ast.ForOfStatement):
            return self._emit_forof_statement(node)
        if isinstance(node, ast.ForInStatement):
            return self._emit_forin_statement(node)
        if isinstance(node, ast.BreakStatement):
            return self._emit_break_statement(node)
        if isinstance(node, ast.ContinueStatement):
            return self._emit_continue_statement(node)
        if isinstance(node, ast.BlockStatement):
            return self._emit_block_statement(node, level)
        raise NotImplementedError(f"Unsupported statement node: {type(node)!r}")

    def __call__(self, *nodes: ast.Statement) -> str:
        lines = []
        for node in nodes:
            stmt_lines = self._emit_statement(node, level=0)
            lines.extend(stmt_lines)
        return self._newline.join(lines)
