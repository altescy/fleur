from __future__ import annotations

import ast
import json
from typing import Any

# ========================
# JavaScript AST ノード定義
# ========================


class JsNode:
    def to_code(self) -> str:
        raise NotImplementedError()


class JsExpr(JsNode):
    pass


class JsStmt(JsNode):
    pass


class JsUndefined(JsExpr):
    def to_code(self) -> str:
        return "undefined"


class JsLiteral(JsExpr):
    def __init__(self, value: Any) -> None:
        self.value = value

    def to_code(self) -> str:
        return json.dumps(self.value, ensure_ascii=False)


class JsIdentifier(JsExpr):
    def __init__(self, name: str) -> None:
        self.name = name

    def to_code(self) -> str:
        if self.name == "self":
            return "this"
        return self.name


class JsBinaryOp(JsExpr):
    def __init__(self, left: JsExpr, op: str, right: JsExpr) -> None:
        self.left = left
        self.op = op
        self.right = right

    def to_code(self) -> str:
        return f"({self.left.to_code()} {self.op} {self.right.to_code()})"


class JsCall(JsExpr):
    def __init__(self, func: JsExpr, args: list[JsExpr]) -> None:
        self.func = func
        self.args = args

    def to_code(self) -> str:
        return f"{self.func.to_code()}({', '.join(arg.to_code() for arg in self.args)})"


class JsMember(JsExpr):
    def __init__(self, obj: JsExpr, prop: str):
        self.obj = obj
        self.prop = prop

    def to_code(self) -> str:
        return f"{self.obj.to_code()}.{self.prop}"


class JsObject(JsExpr):
    def __init__(self, props: list[tuple[str, JsExpr]]) -> None:
        self.props = props

    def to_code(self) -> str:
        return "{" + ", ".join(f"{k}: {v.to_code()}" for k, v in self.props) + "}"


class JsArray(JsExpr):
    def __init__(self, elements: list[JsExpr]) -> None:
        self.elements = elements

    def to_code(self) -> str:
        return "[" + ", ".join(e.to_code() for e in self.elements) + "]"


class JsAccess(JsExpr):
    def __init__(self, obj: JsExpr, prop: str) -> None:
        self.obj = obj
        self.prop = prop

    def to_code(self) -> str:
        return f"{self.obj.to_code()}[{self.prop}]"


# === Statements ===


class JsVarDecl(JsStmt):
    def __init__(self, name: str, value: JsExpr) -> None:
        self.name = name
        self.value = value

    def to_code(self) -> str:
        return f"let {self.name} = {self.value.to_code()};"


class JsAssign(JsStmt):
    def __init__(self, left: JsExpr, right: JsExpr) -> None:
        self.left = left
        self.right = right

    def to_code(self) -> str:
        return f"{self.left.to_code()} = {self.right.to_code()}"


class JsReturn(JsStmt):
    def __init__(self, value: JsExpr) -> None:
        self.value = value

    def to_code(self) -> str:
        return f"return {self.value.to_code()};"


class JsExprStmt(JsStmt):
    def __init__(self, expr: JsExpr) -> None:
        self.expr = expr

    def to_code(self) -> str:
        return f"{self.expr.to_code()};"


class JsFunction(JsStmt):
    def __init__(self, name: str, params: list[str], body: list[JsStmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def to_code(self) -> str:
        body_code = "\n".join("  " + stmt.to_code() for stmt in self.body)
        return f"function {self.name}({', '.join(self.params)}) {{\n{body_code}\n}}"


class JsIf(JsStmt):
    def __init__(
        self,
        test: JsExpr,
        body: list[JsStmt],
        orelse: list[JsStmt | JsIf],
    ) -> None:
        self.test = test
        self.body = body
        self.orelse = orelse

    def to_code(self) -> str:
        code = (
            f"if ({self.test.to_code()}) {{\n"
            + "\n".join("  " + s.to_code() for s in self.body)
            + "\n}"
        )
        if self.orelse:
            if len(self.orelse) == 1 and isinstance(self.orelse[0], JsIf):
                code += f" else {self.orelse[0].to_code()}"
            else:
                code += (
                    " else {{\n"
                    + "\n".join("  " + s.to_code() for s in self.orelse)
                    + "\n}}"
                )
        return code


class JsForOf(JsStmt):
    def __init__(self, var: str, iterable: JsExpr, body: list[JsStmt]) -> None:
        self.var = var
        self.iterable = iterable
        self.body = body

    def to_code(self) -> str:
        body_code = "\n".join("  " + stmt.to_code() for stmt in self.body)
        return f"for (let {self.var} of {self.iterable.to_code()}) {{\n{body_code}\n}}"


class JsWhile(JsStmt):
    def __init__(self, test: JsExpr, body: list[JsStmt]) -> None:
        self.test = test
        self.body = body

    def to_code(self) -> str:
        body_code = "\n".join("  " + stmt.to_code() for stmt in self.body)
        return f"while ({self.test.to_code()}) {{\n{body_code}\n}}"


class JsBreak(JsStmt):
    def to_code(self) -> str:
        return "break;"


class JsContinue(JsStmt):
    def to_code(self) -> str:
        return "continue;"


class JsMethod(JsStmt):
    def __init__(
        self, name: str, params: list[str], body: list[JsStmt], kind: str = "method"
    ) -> None:
        self.name = name
        self.params = params
        self.body = body
        self.kind = kind  # "method", "static", "get", "set"

    def to_code(self) -> str:
        prefix = {
            "method": "",
            "static": "static ",
            "get": "get ",
            "set": "set ",
        }[self.kind]
        body_code = "\n".join("    " + stmt.to_code() for stmt in self.body)
        return f"{prefix}{self.name}({', '.join(self.params)}) {{\n{body_code}\n  }}"


class JsClass(JsStmt):
    def __init__(self, name: str, methods: list[JsMethod]) -> None:
        self.name = name
        self.methods = methods

    def to_code(self) -> str:
        body_code = "\n".join("  " + m.to_code() for m in self.methods)
        return f"class {self.name} {{\n{body_code}\n}}"


# ========================
# Builtin Call Map
# ========================

BUILTIN_CALL_MAP = {
    "len": lambda args: JsMember(convert_expr(args[0]), "length"),
    "range": lambda args: JsCall(
        JsIdentifier("range"), [convert_expr(arg) for arg in args]
    ),
    "enumerate": lambda args: JsCall(
        JsIdentifier("enumerate"), [convert_expr(arg) for arg in args]
    ),
    "print": lambda args: JsCall(
        JsIdentifier("console.log"), [convert_expr(arg) for arg in args]
    ),
}

# ========================
# Python AST → JavaScript AST
# ========================


def convert_operator(op: ast.operator | ast.cmpop) -> str:
    return {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        ast.Pow: "**",
        ast.Mod: "%",
        ast.BitAnd: "&",
        ast.BitOr: "|",
        ast.And: "&&",
        ast.Or: "||",
        ast.Eq: "===",
        ast.NotEq: "!==",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
    }.get(type(op), "?")


# ========================
# Statement Transformers
# ========================


class ExpressionTransformer[T: ast.expr]:
    def matches(self, node: T) -> bool: ...
    def transform(self, node: T) -> JsExpr: ...


class ConstantTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Constant)

    def transform(self, node: ast.Constant) -> JsExpr:
        return JsLiteral(node.value)


class NameTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Name)

    def transform(self, node: ast.Name) -> JsExpr:
        return JsIdentifier(node.id)


class AttributeTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Attribute)

    def transform(self, node: ast.Attribute) -> JsExpr:
        return JsMember(convert_expr(node.value), node.attr)


class BinOpTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.BinOp)

    def transform(self, node: ast.BinOp) -> JsExpr:
        return JsBinaryOp(
            convert_expr(node.left), convert_operator(node.op), convert_expr(node.right)
        )


class ComparisonTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Compare)

    def transform(self, node: ast.Compare) -> JsExpr:
        if len(node.ops) == 1 and len(node.comparators) == 1:
            return JsBinaryOp(
                convert_expr(node.left),
                convert_operator(node.ops[0]),
                convert_expr(node.comparators[0]),
            )
        raise NotImplementedError(f"Unsupported comparison: {type(node)}")


class CallTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Call)

    def transform(self, node: ast.Call) -> JsExpr:
        if isinstance(node.func, ast.Name) and node.func.id in BUILTIN_CALL_MAP:
            return BUILTIN_CALL_MAP[node.func.id](node.args)
        return JsCall(convert_expr(node.func), [convert_expr(arg) for arg in node.args])


class DictTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Dict)

    def transform(self, node: ast.Dict) -> JsExpr:
        keys = [k.value if isinstance(k, ast.Constant) else str(k) for k in node.keys]
        values = [convert_expr(v) for v in node.values]
        return JsObject(list(zip(keys, values)))


class ListTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.List)

    def transform(self, node: ast.List) -> JsExpr:
        return JsArray([convert_expr(e) for e in node.elts])


class SubscriptTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Subscript)

    def transform(self, node: ast.Subscript) -> JsExpr:
        obj = convert_expr(node.value)
        index = convert_expr(node.slice)
        return JsAccess(obj, index.to_code())  # type: ignore


EXPRESSION_TRANSFORMERS = [
    ConstantTransformer(),
    NameTransformer(),
    AttributeTransformer(),
    BinOpTransformer(),
    ComparisonTransformer(),
    CallTransformer(),
    DictTransformer(),
    ListTransformer(),
    SubscriptTransformer(),
]


def convert_expr(node: ast.expr | None) -> JsExpr:
    if node is None:
        return JsUndefined()
    for t in EXPRESSION_TRANSFORMERS:
        if t.matches(node):
            return t.transform(node)
    raise NotImplementedError(f"Unsupported expr: {type(node)}")


# ========================
# Statement Transformers
# ========================


class StatementTransformer[T: ast.stmt]:
    def matches(self, node: T) -> bool: ...
    def transform(self, node: T) -> JsStmt: ...


class ReturnTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.Return)

    def transform(self, node: ast.Return) -> JsStmt:
        return JsReturn(convert_expr(node.value))


class ExprTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.Expr)

    def transform(self, node: ast.Expr) -> JsStmt:
        return JsExprStmt(convert_expr(node.value))


class AssignTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.Assign)

    def transform(self, node: ast.Assign) -> JsStmt:
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            return JsVarDecl(node.targets[0].id, convert_expr(node.value))
        elif len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute):
            obj = convert_expr(node.targets[0].value)
            prop = node.targets[0].attr
            value = convert_expr(node.value)
            return JsAssign(JsMember(obj, prop), value)
        else:
            raise NotImplementedError(f"Unsupported assignment: {type(node)}")


class FunctionTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.FunctionDef)

    def transform(self, node: ast.FunctionDef) -> JsStmt:
        params = [a.arg for a in node.args.args]
        if node.args.vararg:
            params.append(f"...{node.args.vararg.arg}")
        if node.args.kwarg:
            params.append(f"...{node.args.kwarg.arg}")
        body = [convert_stmt(s) for s in node.body]
        return JsFunction(node.name, params, body)


class IfTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.If)

    def transform(self, node: ast.If) -> JsStmt:
        def chain(n: ast.If) -> JsIf:
            test = convert_expr(n.test)
            body = [convert_stmt(s) for s in n.body]
            orelse: list[JsStmt | JsIf]
            if len(n.orelse) == 1 and isinstance(n.orelse[0], ast.If):
                orelse = [chain(n.orelse[0])]
            else:
                orelse = [convert_stmt(s) for s in n.orelse]
            return JsIf(test, body, orelse)

        return chain(node)


class ForTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.For)

    def transform(self, node: ast.For) -> JsStmt:
        var = node.target.id if isinstance(node.target, ast.Name) else None
        iter_expr = convert_expr(node.iter)
        body = [convert_stmt(s) for s in node.body]
        return JsForOf(var or "", iter_expr, body)


class WhileTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.While)

    def transform(self, node: ast.While) -> JsStmt:
        return JsWhile(convert_expr(node.test), [convert_stmt(s) for s in node.body])


class BreakTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.Break)

    def transform(self, node: ast.Break) -> JsStmt:
        return JsBreak()


class ContinueTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.Continue)

    def transform(self, node: ast.Continue) -> JsStmt:
        return JsContinue()


class ClassTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.ClassDef)

    def transform(self, node: ast.ClassDef) -> JsStmt:
        methods = []
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                name = self.map_special_name(stmt.name)
                kind = "method"
                params = [a.arg for a in stmt.args.args[1:]]  # skip self
                for dec in stmt.decorator_list:
                    if isinstance(dec, ast.Name):
                        if dec.id == "staticmethod":
                            kind = "static"
                            params = [a.arg for a in stmt.args.args]
                        elif dec.id == "classmethod":
                            kind = "static"
                            params = [a.arg for a in stmt.args.args[1:]]  # skip cls
                        elif dec.id == "property":
                            kind = "get"
                    elif isinstance(dec, ast.Attribute) and dec.attr == "setter":
                        kind = "set"
                body = [convert_stmt(s) for s in stmt.body]
                methods.append(JsMethod(name, params, body, kind))
        return JsClass(node.name, methods)

    def map_special_name(self, py_name: str) -> str:
        special_map = {
            "__init__": "constructor",
            "__str__": "toString",
            "__repr__": "toString",
            "__iter__": "[Symbol.iterator]",
            "__next__": "next",
            "__len__": "length",
        }
        return special_map.get(py_name, py_name)


STATEMENT_TRANSFORMERS = [
    ReturnTransformer(),
    ExprTransformer(),
    AssignTransformer(),
    FunctionTransformer(),
    IfTransformer(),
    ForTransformer(),
    WhileTransformer(),
    BreakTransformer(),
    ContinueTransformer(),
    ClassTransformer(),
]


def convert_stmt(node: ast.stmt) -> JsStmt:
    for t in STATEMENT_TRANSFORMERS:
        if t.matches(node):
            return t.transform(node)
    raise NotImplementedError(f"Unsupported stmt: {type(node)}")


# ========================
# 実行例
# ========================
if __name__ == "__main__":
    source = """
class Counter:
    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    @staticmethod
    def static_hello():
        print("hello")

    @classmethod
    def from_value(cls, v):
        c = Counter()
        c._value = v
        for i in range(5):
            print(i)

x = {"key": 42, "value": [1, 2, 3]}
print(x["key"][1])
"""

    tree = ast.parse(source)
    for s in tree.body:
        print(convert_stmt(s).to_code())
