from typing import Union

from .ir import (
    IRAssignStmt,
    IRBinaryOpExpr,
    IRBlock,
    IRCallExpr,
    IRExpr,
    IRExprStmt,
    IRFunctionStmt,
    IRIdentifierExpr,
    IRLetStmt,
    IRLiteralBooleanExpr,
    IRLiteralNumberExpr,
    IRLiteralStringExpr,
    IRRangeStmt,
    IRReturnStmt,
    IRStmt,
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
            return f"{x.function}({args_str})"
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
        if isinstance(st, IRFunctionStmt):
            params_str = ", ".join(st.params)
            body = s(st.body, indent + "  ")
            return f"{indent}function {st.name}({params_str}) {{\n{body}{indent}}}\n"
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
