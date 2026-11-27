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
    return _emit(node, settings or EmitterSettings(), 0, {})


def _as_block(statement: ast.ESTreeStatement) -> ast.ESTreeBlockStatement:
    return statement if isinstance(statement, ast.ESTreeBlockStatement) else ast.ESTreeBlockStatement(body=[statement])


def _operand_space(operator: str, operand: str, space: str) -> str:
    """Keep `-` followed by `-1` (or `+` by `+`) from merging into `--` or `++`."""
    if not space and operator[-1:] in ("+", "-") and operand.startswith(operator[-1]):
        return " "
    return space


def _emit(node: ast.ESTreeNode, settings: EmitterSettings, level: int, names: dict[int, str]) -> str:
    comma = ", " if settings.space_after_comma else ","
    op_space = " " if settings.space_around_operators else ""
    nl = settings.newline
    current_indent = settings.indent * level
    next_indent = settings.indent * (level + 1)

    if isinstance(node, ast.ESTreeProgram):
        return nl.join(_emit(stmt, settings, level, names) for stmt in node.body)
    elif isinstance(node, ast.ESTreeVariableDeclaration):
        declarations = comma.join(_emit(d, settings, level, names) for d in node.declarations)
        return f"{node.kind} {declarations};"
    elif isinstance(node, ast.ESTreeVariableDeclarator):
        if node.init is None:
            return _emit(node.id, settings, level, names)
        return f"{_emit(node.id, settings, level, names)} = {_emit(node.init, settings, level, names)}"
    elif isinstance(node, ast.ESTreeObjectExpression):
        props = comma.join(_emit(p, settings, level, names) for p in node.properties)
        return "{" + props + "}"
    elif isinstance(node, ast.ESTreeObjectProperty):
        return f"{_emit(node.key, settings, level, names)}: {_emit(node.value, settings, level, names)}"
    elif isinstance(node, ast.ESTreeArrayExpression):
        return "[" + comma.join("null" if e is None else _emit(e, settings, level, names) for e in node.elements) + "]"
    elif isinstance(node, ast.ESTreeFunctionExpression):
        params = comma.join(_emit(p, settings, level, names) for p in node.params)
        return f"function({params}) {_emit(node.body, settings, level, names)}"
    elif isinstance(node, ast.ESTreeFunctionBody):
        return _emit(ast.ESTreeBlockStatement(body=node.body), settings, level, names)
    elif isinstance(node, ast.ESTreeBlockStatement):
        if not node.body:
            return "{}"
        inner = nl.join(next_indent + _emit(stmt, settings, level + 1, names) for stmt in node.body)
        return "{" + nl + inner + nl + current_indent + "}"
    elif isinstance(node, ast.ESTreeReturnStatement):
        if node.argument is None:
            return "return;"
        return f"return {_emit(node.argument, settings, level, names)};"
    elif isinstance(node, ast.ESTreeExpressionStatement):
        return f"{_emit(node.expression, settings, level, names)};"
    elif isinstance(node, ast.ESTreeIfStatement):
        test = _emit(node.test, settings, level, names)
        consequent = _emit(_as_block(node.consequent), settings, level, names)
        alternate = (
            "" if node.alternate is None else f" else {_emit(_as_block(node.alternate), settings, level, names)}"
        )
        return f"if ({test}) {consequent}{alternate}"
    elif isinstance(node, ast.ESTreeSwitchStatement):
        cases = nl.join(next_indent + _emit(c, settings, level + 1, names) for c in node.cases)
        return f"switch ({_emit(node.discriminant, settings, level, names)}) {{{nl}{cases}{nl}{current_indent}}}"
    elif isinstance(node, ast.ESTreeSwitchCase):
        header = "default:" if node.test is None else f"case {_emit(node.test, settings, level, names)}:"
        if not node.consequent:
            return header
        body = nl.join(settings.indent + _emit(stmt, settings, level + 1, names) for stmt in node.consequent)
        return f"{header}{nl}{body}"
    elif isinstance(node, ast.ESTreeBreakStatement):
        return "break;" if node.label is None else f"break {_emit(node.label, settings, level, names)};"
    elif isinstance(node, ast.ESTreeCallExpression):
        args = comma.join(_emit(arg, settings, level, names) for arg in node.arguments)
        return f"{_emit(node.callee, settings, level, names)}({args})"
    elif isinstance(node, ast.ESTreeNewExpression):
        args = comma.join(_emit(arg, settings, level, names) for arg in node.arguments)
        return f"(new {_emit(node.callee, settings, level, names)}({args}))"
    elif isinstance(node, ast.ESTreeMemberExpression):
        obj = _emit(node.object, settings, level, names)
        prop = _emit(node.property, settings, level, names)
        if node.computed:
            return f"{obj}[{prop}]"
        return f"{obj}.{prop}"
    elif isinstance(node, ast.ESTreeBinaryExpression):
        operator_space = " " if node.operator in ("in", "instanceof") else op_space
        left = _emit(node.left, settings, level, names)
        right = _emit(node.right, settings, level, names)
        return f"({left}{operator_space}{node.operator}{_operand_space(node.operator, right, operator_space)}{right})"
    elif isinstance(node, ast.ESTreeAssignmentExpression):
        return f"({_emit(node.left, settings, level, names)}{op_space}{node.operator}{op_space}{_emit(node.right, settings, level, names)})"
    elif isinstance(node, ast.ESTreeUnaryExpression):
        operator_space = " " if node.operator.isalpha() else op_space
        argument = _emit(node.argument, settings, level, names)
        return f"({node.operator}{_operand_space(node.operator, argument, operator_space)}{argument})"
    elif isinstance(node, ast.ESTreeLogicalExpression):
        return f"({_emit(node.left, settings, level, names)}{op_space}{node.operator}{op_space}{_emit(node.right, settings, level, names)})"
    elif isinstance(node, ast.ESTreeConditionalExpression):
        return (
            f"({_emit(node.test, settings, level, names)}{op_space}?{op_space}{_emit(node.consequent, settings, level, names)}"
            f"{op_space}:{op_space}{_emit(node.alternate, settings, level, names)})"
        )
    elif isinstance(node, ast.ESTreeLiteral):
        # Keep literal text from being interpreted as markup in an inline script.
        return json.dumps(node.value).replace("<", "\\u003c")
    elif isinstance(node, ast.ESTreeGeneratedIdentifier):
        return names.setdefault(id(node), f"$fleur{len(names)}")
    elif isinstance(node, ast.ESTreeIdentifier):
        return node.name
    else:
        raise NotImplementedError(f"Unsupported node type: {type(node).__name__}")
