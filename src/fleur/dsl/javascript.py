from .ast import (
    GraineArrayNode,
    GraineAssignNode,
    GraineASTExpr,
    GraineASTNode,
    GraineASTStmt,
    GraineBinaryOpNode,
    GraineBlockNode,
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


def emit_javascript(*asts: GraineASTNode) -> str:
    def e(expr: GraineASTExpr) -> str:
        if isinstance(expr, GraineNumberNode):
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
            raise NotImplementedError(f"Unsupported expression type: {type(expr)}")

    def s(stmt: GraineASTStmt, indent: str = "") -> str:
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
            return f"{indent}function {stmt.name} ({params}) {{\n{body}\n{indent}}}"
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
                else_branch = s(stmt.else_branch, indent + "  ")
                result += f" else {{\n{else_branch}\n{indent}}}"
            return result
        else:
            raise NotImplementedError(f"Unsupported statement type: {type(stmt)}")

    lines = []
    for ast in asts:
        if isinstance(ast, GraineASTExpr):
            lines.append(e(ast) + ";")
        elif isinstance(ast, GraineASTStmt):
            lines.append(s(ast))
        else:
            raise NotImplementedError(f"Unsupported AST node type: {type(ast)}")
    return "\n".join(lines)
