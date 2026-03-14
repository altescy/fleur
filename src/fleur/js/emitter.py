import json
from dataclasses import dataclass

from . import ast


@dataclass(frozen=True, slots=True)
class EmitterSettings:
    indent: str = ""
    newline: str = ""
    space_after_comma: bool = False
    space_around_operators: bool = False


def emit(node: ast.ESTreeNode, settings: EmitterSettings | None = None) -> str:
    return _emit(node, settings or EmitterSettings(), 0)


def _emit(node: ast.ESTreeNode, settings: EmitterSettings, level: int) -> str:
    comma = ", " if settings.space_after_comma else ","
    op_space = " " if settings.space_around_operators else ""
    nl = settings.newline
    current_indent = settings.indent * level
    next_indent = settings.indent * (level + 1)

    if isinstance(node, ast.ESTreeProgram):
        return nl.join(_emit(stmt, settings, level) for stmt in node.body)
    elif isinstance(node, ast.ESTreeVariableDeclaration):
        declarations = comma.join(_emit(d, settings, level) for d in node.declarations)
        return f"{node.kind} {declarations};"
    elif isinstance(node, ast.ESTreeVariableDeclarator):
        if node.init is None:
            return _emit(node.id, settings, level)
        return f"{_emit(node.id, settings, level)} = {_emit(node.init, settings, level)}"
    elif isinstance(node, ast.ESTreeObjectExpression):
        props = comma.join(_emit(p, settings, level) for p in node.properties)
        return "{" + props + "}"
    elif isinstance(node, ast.ESTreeObjectProperty):
        return f"{_emit(node.key, settings, level)}: {_emit(node.value, settings, level)}"
    elif isinstance(node, ast.ESTreeArrayExpression):
        return "[" + comma.join("null" if e is None else _emit(e, settings, level) for e in node.elements) + "]"
    elif isinstance(node, ast.ESTreeFunctionExpression):
        params = comma.join(_emit(p, settings, level) for p in node.params)
        return f"function({params}) {_emit(node.body, settings, level)}"
    elif isinstance(node, ast.ESTreeFunctionBody):
        return _emit(ast.ESTreeBlockStatement(body=node.body), settings, level)
    elif isinstance(node, ast.ESTreeBlockStatement):
        if not node.body:
            return "{}"
        inner = nl.join(next_indent + _emit(stmt, settings, level + 1) for stmt in node.body)
        return "{" + nl + inner + nl + current_indent + "}"
    elif isinstance(node, ast.ESTreeReturnStatement):
        if node.argument is None:
            return "return;"
        return f"return {_emit(node.argument, settings, level)};"
    elif isinstance(node, ast.ESTreeExpressionStatement):
        return f"{_emit(node.expression, settings, level)};"
    elif isinstance(node, ast.ESTreeSwitchStatement):
        cases = nl.join(next_indent + _emit(c, settings, level + 1) for c in node.cases)
        return f"switch ({_emit(node.discriminant, settings, level)}) {{{nl}{cases}{nl}{current_indent}}}"
    elif isinstance(node, ast.ESTreeSwitchCase):
        header = "default:" if node.test is None else f"case {_emit(node.test, settings, level)}:"
        if not node.consequent:
            return header
        body = nl.join(settings.indent + _emit(stmt, settings, level + 1) for stmt in node.consequent)
        return f"{header}{nl}{body}"
    elif isinstance(node, ast.ESTreeBreakStatement):
        return "break;" if node.label is None else f"break {_emit(node.label, settings, level)};"
    elif isinstance(node, ast.ESTreeCallExpression):
        args = comma.join(_emit(arg, settings, level) for arg in node.arguments)
        return f"{_emit(node.callee, settings, level)}({args})"
    elif isinstance(node, ast.ESTreeMemberExpression):
        obj = _emit(node.object, settings, level)
        prop = _emit(node.property, settings, level)
        if node.computed:
            return f"{obj}[{prop}]"
        return f"{obj}.{prop}"
    elif isinstance(node, ast.ESTreeBinaryExpression):
        return f"({_emit(node.left, settings, level)}{op_space}{node.operator}{op_space}{_emit(node.right, settings, level)})"
    elif isinstance(node, ast.ESTreeLiteral):
        return json.dumps(node.value)
    elif isinstance(node, ast.ESTreeIdentifier):
        return node.name
    else:
        raise NotImplementedError(f"Unsupported node type: {type(node).__name__}")
