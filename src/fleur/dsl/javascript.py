from typing import Union

from .ir import (
    IRAssignStmt,
    IRBinaryOpExpr,
    IRBlock,
    IRCallExpr,
    IRClassStmt,
    IRExpr,
    IRExprStmt,
    IRFunctionStmt,
    IRIdentifierExpr,
    IRIfStmt,
    IRIndexAccessExpr,
    IRLetStmt,
    IRLiteralArrayExpr,
    IRLiteralBooleanExpr,
    IRLiteralNumberExpr,
    IRLiteralRecordExpr,
    IRLiteralStringExpr,
    IRMethodCallExpr,
    IRNewExpr,
    IRPropertyAccessExpr,
    IRPropertyAssignStmt,
    IRRangeStmt,
    IRReturnStmt,
    IRStmt,
    IRThisExpr,
)


def emit_javascript(*args: Union[IRExpr, IRStmt]) -> str:
    def e(x: IRExpr) -> str:
        if isinstance(x, IRLiteralNumberExpr):
            return str(x.value)
        if isinstance(x, IRLiteralBooleanExpr):
            return "true" if x.value else "false"
        if isinstance(x, IRLiteralStringExpr):
            return f'"{x.value}"'
        if isinstance(x, IRIdentifierExpr):
            return x.name
        if isinstance(x, IRBinaryOpExpr):
            left = e(x.left)
            right = e(x.right)
            op = x.operator.value
            return f"({left} {op} {right})"
        if isinstance(x, IRCallExpr):
            args_str = ", ".join(e(arg) for arg in x.args)
            func_str = e(x.function) if isinstance(x.function, IRExpr) else x.function
            return f"{func_str}({args_str})"
        if isinstance(x, IRLiteralArrayExpr):
            elements_str = ", ".join(e(elem) for elem in x.elements)
            return f"[{elements_str}]"
        if isinstance(x, IRLiteralRecordExpr):
            fields_str = ", ".join(f'"{key}": {e(value)}' for key, value in x.fields.items())
            return f"{{{fields_str}}}"
        if isinstance(x, IRIndexAccessExpr):
            target_str = e(x.target)
            index_str = e(x.index)
            return f"{target_str}[{index_str}]"
        if isinstance(x, IRPropertyAccessExpr):
            target_str = e(x.target)
            return f"{target_str}.{x.property}"
        if isinstance(x, IRMethodCallExpr):
            target_str = e(x.target)
            args_str = ", ".join(e(arg) for arg in x.args)
            return f"{target_str}.{x.method}({args_str})"
        if isinstance(x, IRThisExpr):
            return "this"
        if isinstance(x, IRNewExpr):
            args_str = ", ".join(e(arg) for arg in x.args)
            return f"new {x.class_name}({args_str})"
        raise ValueError(f"Unsupported IRExpr: {x}")

    def s(st: IRStmt, indent: str) -> str:
        if isinstance(st, IRLetStmt):
            return f"{indent}let {st.name} = {e(st.value)};\n"
        if isinstance(st, IRAssignStmt):
            return f"{indent}{st.name} = {e(st.value)};\n"
        if isinstance(st, IRExprStmt):
            return f"{indent}{e(st.expr)};\n"
        if isinstance(st, IRReturnStmt):
            return f"{indent}return {e(st.value)};\n"
        if isinstance(st, IRRangeStmt):
            head = f"for (let {st.var} = {e(st.start)}; {st.var} < {e(st.end)}; {st.var}++)"
            body = s(st.body, indent + "  ")
            return f"{indent}{head} {{\n{body}{indent}}}\n"
        if isinstance(st, IRIfStmt):
            condition_str = e(st.condition)
            then_body = s(st.then_body, indent + "  ")
            result = f"{indent}if ({condition_str}) {{\n{then_body}{indent}}}"
            if st.else_body is not None:
                else_body = s(st.else_body, indent + "  ")
                result += f" else {{\n{else_body}{indent}}}"
            return result + "\n"
        if isinstance(st, IRFunctionStmt):
            params_str = ", ".join(st.params)
            body = s(st.body, indent + "  ")
            return f"{indent}function {st.name}({params_str}) {{\n{body}{indent}}}\n"
        if isinstance(st, IRPropertyAssignStmt):
            return f"{indent}{e(st.target)} = {e(st.value)};\n"
        if isinstance(st, IRClassStmt):
            # Generate constructor
            constructor_params = ", ".join(st.constructor_params)
            constructor_body = s(st.constructor_body, indent + "    ")

            # Generate methods
            methods_lines = []
            for method in st.methods:
                prefix = "static " if method.is_static else ""
                prefix = "get " if method.is_getter else prefix
                params = ", ".join(method.params)
                method_body = s(method.body, indent + "    ")
                methods_lines.append(f"{indent}  {prefix}{method.name}({params}) {{\n{method_body}{indent}  }}")

            methods_str = "\n".join(methods_lines)

            result = f"{indent}class {st.name} {{\n"
            result += f"{indent}  constructor({constructor_params}) {{\n{constructor_body}{indent}  }}\n"
            if methods_str:
                result += methods_str + "\n"
            result += f"{indent}}}\n"
            return result
        if isinstance(st, IRBlock):
            body_lines = [s(bst, indent) for bst in st.body]
            return "".join(body_lines)
        raise ValueError(f"Unsupported IRStmt: {st}")

    lines = []
    for item in args:
        if isinstance(item, IRExpr):
            lines.append(e(item) + ";")
        elif isinstance(item, IRStmt):
            lines.append(s(item, ""))
        else:
            raise ValueError(f"Unsupported item: {item}")
    return "\n".join(lines)
