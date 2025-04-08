from __future__ import annotations

import ast
import inspect
import json
from collections.abc import Callable, Mapping
from textwrap import dedent
from typing import Any, ParamSpec, overload

__all__ = [
    "document",
    "javascript",
    "typeof",
    "JSON",
    "Node",
    "Object",
    "Proxy",
]

P = ParamSpec("P")

# ========================
# JavaScript AST Nodes
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
    MEMBER_MAP = {
        "startswith": "startsWith",
        "endswith": "endsWith",
        "append": "push",
        "lower": "toLowerCase",
        "upper": "toUpperCase",
    }

    def __init__(self, obj: JsExpr, prop: str):
        self.obj = obj
        self.prop = prop

    def to_code(self) -> str:
        prop = self.MEMBER_MAP.get(self.prop, self.prop)
        return f"{self.obj.to_code()}.{prop}"


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


class JsFunction(JsExpr):
    def __init__(self, name: str, params: list[str], body: list[JsStmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def to_code(self) -> str:
        body_code = "\n".join("  " + stmt.to_code() for stmt in self.body)
        return f"function {self.name}({', '.join(self.params)}) {{\n{body_code}\n}}"


class JsNew(JsExpr):
    def __init__(self, cls: JsExpr, args: list[JsExpr]) -> None:
        self.cls = cls
        self.args = args

    def to_code(self) -> str:
        return f"new {self.cls.to_code()}({', '.join(arg.to_code() for arg in self.args)})"


class JsLambda(JsExpr):
    def __init__(self, params: list[str], body: JsExpr) -> None:
        self.params = params
        self.body = body

    def to_code(self) -> str:
        return f"({', '.join(self.params)}) => {self.body.to_code()}"


class JsClass(JsExpr):
    def __init__(
        self,
        name: str,
        methods: list[JsMethod],
        bases: list[JsExpr] | None = None,
    ) -> None:
        self.name = name
        self.methods = methods
        self.bases = bases or []

    def to_code(self) -> str:
        body_code = "\n".join("  " + m.to_code() for m in self.methods)
        base_code = f"extends {', '.join(base.to_code() for base in self.bases)}" if self.bases else ""
        return f"class {self.name} {base_code} {{\n{body_code}\n}}"


class JsInstanceOf(JsExpr):
    def __init__(self, obj: JsExpr, cls: JsExpr) -> None:
        self.obj = obj
        self.cls = cls

    def to_code(self) -> str:
        return f"{self.obj.to_code()} instanceof {self.cls.to_code()}"


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
        code = f"if ({self.test.to_code()}) {{\n" + "\n".join("  " + s.to_code() for s in self.body) + "\n}"
        if self.orelse:
            if len(self.orelse) == 1 and isinstance(self.orelse[0], JsIf):
                code += f" else {self.orelse[0].to_code()}"
            else:
                code += " else {{\n" + "\n".join("  " + s.to_code() for s in self.orelse) + "\n}}"
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
        self,
        name: str,
        params: list[str],
        body: list[JsStmt],
        kind: str = "method",
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


# ========================
# Builtin Call Map
# ========================

BUILTIN_CALL_MAP = {
    "len": lambda args: JsMember(convert_expr(args[0]), "length"),
    "range": lambda args: JsCall(JsIdentifier("range"), [convert_expr(arg) for arg in args]),
    "enumerate": lambda args: JsCall(JsIdentifier("enumerate"), [convert_expr(arg) for arg in args]),
    "print": lambda args: JsCall(JsIdentifier("console.log"), [convert_expr(arg) for arg in args]),
    "isinstance": lambda args: JsInstanceOf(convert_expr(args[0]), convert_expr(args[1])),
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
    def transform(self, node: T) -> JsExpr | JsStmt: ...


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
        return JsBinaryOp(convert_expr(node.left), convert_operator(node.op), convert_expr(node.right))


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
        if isinstance(node.slice, ast.Slice):
            return JsCall(
                JsMember(obj, "slice"),
                [
                    convert_expr(node.slice.lower) if node.slice.lower else JsLiteral(0),
                    convert_expr(node.slice.upper),
                ],
            )
        index = convert_expr(node.slice)
        return JsAccess(obj, index.to_code())


class FunctionTransformer(ExpressionTransformer):
    IGNORED_DECORATORS = {
        "asdecorator",
        "component",
        "javascript",
        "fleur.asdecorator",
        "fleur.component",
        "fleur.javascript",
    }

    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.FunctionDef)

    def transform(self, node: ast.FunctionDef) -> JsExpr | JsStmt:
        params = [a.arg for a in node.args.args]
        if node.args.vararg:
            params.append(f"...{node.args.vararg.arg}")
        if node.args.kwarg:
            params.append(f"{{...{node.args.kwarg.arg}}}")
        body = [convert_stmt(s) for s in node.body]
        func = JsFunction(node.name, params, body)

        for decorator_node in node.decorator_list:
            decorator: JsExpr
            decorator_args: list[JsExpr] = []
            if isinstance(decorator_node, ast.Name):
                decorator = JsIdentifier(decorator_node.id)
            elif isinstance(decorator_node, ast.Attribute):
                decorator = JsMember(convert_expr(decorator_node.value), decorator_node.attr)
            elif isinstance(decorator_node, ast.Call):
                decorator = convert_expr(decorator_node.func)
                decorator_args = [convert_expr(arg) for arg in decorator_node.args]
            else:
                raise NotImplementedError(f"Unsupported decorator: {type(decorator_node)}")
            if decorator.to_code() in self.IGNORED_DECORATORS:
                continue
            func = JsCall(decorator, [func, *decorator_args])

        return (
            JsVarDecl(
                node.name,
                func,
            )
            if isinstance(func, JsCall)
            else func
        )


class StarredTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Starred)

    def transform(self, node: ast.Starred) -> JsExpr:
        return JsIdentifier(f"...({convert_expr(node.value).to_code()})")


class LambdaTransformer(ExpressionTransformer):
    def matches(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Lambda)

    def transform(self, node: ast.Lambda) -> JsExpr:
        params = [a.arg for a in node.args.args]
        body = convert_expr(node.body)
        return JsLambda(params, body)


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
    FunctionTransformer(),
    StarredTransformer(),
    LambdaTransformer(),
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
    def transform(self, node: T) -> JsStmt | JsExpr: ...


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


class AugAssignTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.AugAssign)

    def transform(self, node: ast.AugAssign) -> JsExpr:
        if isinstance(node.target, ast.Name):
            left = JsIdentifier(node.target.id)
        elif isinstance(node.target, ast.Attribute):
            left = JsMember(convert_expr(node.target.value), node.target.attr)
        else:
            raise NotImplementedError(f"Unsupported assignment: {type(node)}")
        return JsBinaryOp(
            left,
            f"{convert_operator(node.op)}=",
            convert_expr(node.value),
        )


class ClassTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.ClassDef)

    def _is_protocol(self, node: ast.ClassDef) -> bool:
        return any(
            base.id == "Protocol"
            if isinstance(base, ast.Name)
            else isinstance(base.value, ast.Name) and base.value.id == "Protocol"
            for base in node.bases
            if isinstance(base, (ast.Name, ast.Subscript))
        )

    def transform(self, node: ast.ClassDef) -> JsStmt:
        methods = []
        proxy_methods = []
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
                if stmt.name == "__getattr__":
                    proxy_methods.append(JsMethod("get", ["_"] + params, body, "get"))
                else:
                    methods.append(JsMethod(name, params, body, kind))
        if self._is_protocol(node):
            return JsVarDecl(
                node.name,
                JsObject([(m.name, JsFunction(m.name, m.params, m.body)) for m in methods]),
            )
        bases = [convert_expr(base.value if isinstance(base, ast.Subscript) else base) for base in node.bases]
        return JsVarDecl(
            node.name,
            JsNew(
                JsIdentifier("Proxy"),
                [
                    JsClass("", methods, bases),
                    JsObject(
                        [
                            (
                                "apply",
                                JsFunction(
                                    "",
                                    ["cls", "_", "args"],
                                    [
                                        JsReturn(
                                            JsNew(
                                                JsIdentifier("Proxy"),
                                                [
                                                    JsNew(
                                                        JsIdentifier("cls"),
                                                        [JsIdentifier("...args")],
                                                    ),
                                                    JsObject(
                                                        [
                                                            (
                                                                m.name,
                                                                JsFunction(
                                                                    m.name,
                                                                    m.params,
                                                                    m.body,
                                                                ),
                                                            )
                                                            for m in proxy_methods
                                                        ]
                                                    ),
                                                ],
                                            )
                                        )
                                    ],
                                ),
                            )
                        ]
                    ),
                ],
            ),
        )

    def map_special_name(self, py_name: str) -> str:
        special_map = {
            "__init__": "constructor",
            "__str__": "toString",
            "__repr__": "toString",
            "__iter__": "[Symbol.iterator]",
            "__next__": "next",
            "__len__": "length",
            "__call__": "call",
            "__getattr__": "get",
        }
        return special_map.get(py_name, py_name)


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
        var: JsExpr
        if isinstance(node.target, ast.Name):
            var = JsIdentifier(node.target.id)
        elif isinstance(node.target, ast.Attribute):
            var = JsMember(convert_expr(node.target.value), node.target.attr)
        elif isinstance(node.target, ast.Tuple):
            var = JsArray([JsIdentifier(e.id) for e in node.target.elts if isinstance(e, ast.Name)])
        else:
            raise NotImplementedError(f"Unsupported for target: {type(node.target)}")
        iter_expr = convert_expr(node.iter)
        body = [convert_stmt(s) for s in node.body]
        return JsForOf(var.to_code(), iter_expr, body)


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


class PassTransformer(StatementTransformer):
    def matches(self, node: ast.stmt) -> bool:
        return isinstance(node, ast.Pass)

    def transform(self, node: ast.Pass) -> JsStmt:
        del node
        return JsExprStmt(JsUndefined())


STATEMENT_TRANSFORMERS = [
    ReturnTransformer(),
    ExprTransformer(),
    AssignTransformer(),
    AugAssignTransformer(),
    IfTransformer(),
    ForTransformer(),
    WhileTransformer(),
    BreakTransformer(),
    ContinueTransformer(),
    ClassTransformer(),
    FunctionTransformer(),
    PassTransformer(),
]


def convert_stmt(node: ast.stmt) -> JsStmt:
    for t in STATEMENT_TRANSFORMERS:
        if t.matches(node):
            return t.transform(node)
    raise NotImplementedError(f"Unsupported stmt: {type(node)}")


def to_javascript(fn: Any) -> str:
    source = dedent(inspect.getsource(fn))
    tree = ast.parse(source)
    return "\n".join(convert_stmt(n).to_code() for n in tree.body)


# ========================
# JavaScript Environment
# ========================


@overload
def javascript[T](value: None = None) -> Callable[[T], T]: ...


@overload
def javascript[T](value: T) -> T: ...


def javascript[T](value: T | None = None) -> T | Callable[[T], T]:
    def decorator(value: T) -> T:
        return value

    if value is None:
        return decorator
    return decorator(value)


def asdecorator[*P, R, F: Callable](fn: Callable[[F, *P], R]) -> Callable[[*P], Callable[[F], R]]:
    return fn  # type: ignore


@javascript
class Node:
    def replaceWith(self, node: Node, /) -> None: ...


@javascript
def typeof(_: Any) -> str: ...


@javascript
class document:
    body: Dom

    @staticmethod
    def createTextNode(s: str, /) -> Node: ...

    @staticmethod
    def createElement(tag: str, /) -> Dom: ...


@javascript
class JSON:
    @staticmethod
    def stringify(_: Any) -> str: ...


@javascript
class Object:
    @staticmethod
    def getPrototypeOf(_: Any) -> Any: ...

    @staticmethod
    def entries[K, V](_: Mapping[K, V]) -> list[tuple[K, V]]: ...


@javascript
def Proxy[T](target: T, *args: Any) -> T: ...


Dom = Any
