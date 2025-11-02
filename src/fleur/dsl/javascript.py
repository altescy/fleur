"""
JavaScript code emitter for Graine AST.

This module traverses Graine AST nodes and generates clean, readable JavaScript code.
It handles proper indentation, escaping, and formatting to produce idiomatic JavaScript
that is functionally equivalent to the original Graine code.
"""

from .ast import (
    GraineArrayNode,
    GraineAssignNode,
    GraineASTExpr,
    GraineASTNode,
    GraineASTStmt,
    GraineBinaryOpNode,
    GraineBlockNode,
    GraineBooleanNode,
    GraineCallNode,
    GraineClassNode,
    GraineConditionalNode,
    GraineConstructionNode,
    GraineForOfNode,
    GraineFunctionNode,
    GraineIdentifierNode,
    GraineIfNode,
    GraineIndexAccessNode,
    GraineLetNode,
    GraineNumberNode,
    GrainePropertyAccessNode,
    GraineRecordNode,
    GraineReturnNode,
    GraineStringNode,
)
from .errors import GraineASTError, format_unsupported_ast_error


def emit_javascript(*asts: GraineASTNode) -> str:
    """
    Generate JavaScript code from Graine AST nodes.

    This function traverses the AST and emits formatted JavaScript code.
    It handles both expression and statement nodes, maintaining proper
    indentation and syntax.

    Args:
        *asts: One or more AST nodes to emit as JavaScript

    Returns:
        A string containing the generated JavaScript code

    Raises:
        NotImplementedError: If an unsupported AST node type is encountered

    Example:
        node = GraineNumberNode(value=42)
        code = emit_javascript(node)
        # Returns: "42;"
    """

    def e(expr: GraineASTExpr) -> str:
        """Emit an expression node as JavaScript."""
        if isinstance(expr, GraineBooleanNode):
            return "true" if expr.value else "false"
        elif isinstance(expr, GraineNumberNode):
            return str(expr.value)
        elif isinstance(expr, GraineStringNode):
            # Escape backslashes, double quotes, and newlines
            escaped = (
                expr.value.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
            )
            return f'"{escaped}"'
        elif isinstance(expr, GraineArrayNode):
            elements = ", ".join(e(elem) for elem in expr.elements)
            return f"[{elements}]"
        elif isinstance(expr, GraineRecordNode):
            fields = ", ".join(f"{key}: {e(value)}" for key, value in expr.fields.items())
            return f"{{{fields}}}"
        elif isinstance(expr, GraineBinaryOpNode):
            left = e(expr.left)
            right = e(expr.right)
            return f"({left} {expr.op} {right})"
        elif isinstance(expr, GraineCallNode):
            function = e(expr.function)
            arguments = ", ".join(e(arg) for arg in expr.arguments)
            return f"{function}({arguments})"
        elif isinstance(expr, GrainePropertyAccessNode):
            receiver = e(expr.receiver)
            return f"{receiver}.{expr.property_name}"
        elif isinstance(expr, GraineIndexAccessNode):
            receiver = e(expr.receiver)
            index = e(expr.index)
            return f"{receiver}[{index}]"
        elif isinstance(expr, GraineIdentifierNode):
            return expr.name
        elif isinstance(expr, GraineConditionalNode):
            condition = e(expr.condition)
            then_branch = e(expr.then_branch)
            if expr.else_branch:
                else_branch = e(expr.else_branch)
                return f"({condition} ? ({then_branch}) : ({else_branch}))"
            else:
                return f"({condition} ? ({then_branch}) : undefined)"
        elif isinstance(expr, GraineConstructionNode):
            arguments = ", ".join(e(arg) for arg in expr.arguments)
            return f"new {expr.class_name}({arguments})"
        else:
            raise GraineASTError(format_unsupported_ast_error(type(expr)))

    def s(stmt: GraineASTStmt, indent: str = "") -> str:
        """Emit a statement node as JavaScript with proper indentation."""
        if isinstance(stmt, GraineLetNode):
            identifier = e(stmt.identifier)
            value = e(stmt.value)
            return f"{indent}let {identifier} = {value};"
        elif isinstance(stmt, GraineAssignNode):
            identifier = e(stmt.identifier)
            value = e(stmt.value)
            return f"{indent}{identifier} = {value};"
        elif isinstance(stmt, GraineReturnNode):
            value = e(stmt.value)
            return f"{indent}return {value};"
        elif isinstance(stmt, GraineBlockNode):
            return "\n".join(s(subb, indent) for subb in stmt.statements)
        elif isinstance(stmt, GraineFunctionNode):
            params = ", ".join(param.name for param in stmt.parameters)
            body = s(stmt.body, indent + "  ")
            return f"{indent}function {stmt.name}({params}) {{\n{body}\n{indent}}}"
        elif isinstance(stmt, GraineClassNode):
            methods = []
            if stmt.constructor:
                constructor = stmt.constructor
                params = ", ".join(param.name for param in constructor.parameters)
                body = s(constructor.body, indent + "    ")
                methods.append(f"{indent}  constructor({params}) {{\n{body}\n  {indent}}}")
            for method in stmt.methods:
                func = method.function
                params = ", ".join(param.name for param in func.parameters)
                body = s(func.body, indent + "    ")
                accessor_str = f"{method.accessor} " if method.accessor else ""
                methods.append(f"{indent}  {accessor_str}{method.name}({params}) {{\n{body}\n  {indent}}}")
            methods_str = "\n".join(methods)
            return f"{indent}class {stmt.name} {{\n{methods_str}\n{indent}}}"
        elif isinstance(stmt, GraineForOfNode):
            variable = e(stmt.variable)
            iterator = e(stmt.iterator)
            body = s(stmt.body, indent + "  ")
            return f"{indent}for (let {variable} of {iterator}) {{\n{body}\n{indent}}}"
        elif isinstance(stmt, GraineIfNode):
            condition = e(stmt.condition)
            then_branch = s(stmt.then_branch, indent + "  ")
            result = f"{indent}if ({condition}) {{\n{then_branch}\n{indent}}}"
            if stmt.else_branch:
                if isinstance(stmt.else_branch, GraineIfNode):
                    else_branch = s(stmt.else_branch, indent)
                    result += f" else {else_branch[len(indent) :]}"
                else:
                    else_branch = s(stmt.else_branch, indent + "  ")
                    result += f" else {{\n{else_branch}\n{indent}}}"
            return result
        else:
            raise GraineASTError(format_unsupported_ast_error(type(stmt)))

    lines = []
    for ast in asts:
        if isinstance(ast, GraineASTExpr):
            lines.append(e(ast) + ";")
        elif isinstance(ast, GraineASTStmt):
            lines.append(s(ast))
        else:
            raise NotImplementedError(f"Unsupported AST node type: {type(ast)}")
    return "\n".join(lines)
