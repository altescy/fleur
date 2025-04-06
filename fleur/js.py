import ast
from typing import Any


class JSCodeGenerator(ast.NodeVisitor):
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.indent_level: int = 0

    def indent(self) -> str:
        return '  ' * self.indent_level

    def visit_Module(self, node: ast.Module) -> Any:
        for stmt in node.body:
            self.visit(stmt)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        args = [arg.arg for arg in node.args.args]
        self.lines.append(f"{self.indent()}function {node.name}({', '.join(args)}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.lines.append(f"{self.indent()}}}")

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.lines.append(f"{self.indent()}class {node.name} {{")
        self.indent_level += 1
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                self.visit_FunctionDef_in_class(stmt)
        self.indent_level -= 1
        self.lines.append(f"{self.indent()}}}")

    def visit_FunctionDef_in_class(self, node: ast.FunctionDef) -> Any:
        args = [arg.arg for arg in node.args.args]
        if args and args[0] == 'self':
            args = args[1:]
        method_name = node.name if node.name != '__init__' else 'constructor'
        self.lines.append(f"{self.indent()}{method_name}({', '.join(args)}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.lines.append(f"{self.indent()}}}")

    def visit_Return(self, node: ast.Return) -> Any:
        value = self.visit(node.value) if node.value else "undefined"
        self.lines.append(f"{self.indent()}return {value};")

    def visit_Assign(self, node: ast.Assign) -> Any:
        if len(node.targets) != 1:
            raise NotImplementedError("Multiple assignment not supported")
        target_node = node.targets[0]
        value = self.visit(node.value)

        if isinstance(target_node, ast.Attribute) and isinstance(target_node.value, ast.Name) and target_node.value.id == 'self':
            # self.x = y → this.x = y;
            attr = target_node.attr
            self.lines.append(f"{self.indent()}this.{attr} = {value};")
        else:
            target = self.visit(target_node)
            self.lines.append(f"{self.indent()}let {target} = {value};")

    def visit_Expr(self, node: ast.Expr) -> Any:
        value = self.visit(node.value)
        self.lines.append(f"{self.indent()}{value};")

    def visit_Call(self, node: ast.Call) -> str:
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        return f"{func}({', '.join(args)})"

    def visit_Name(self, node: ast.Name) -> str:
        return node.id

    def visit_Constant(self, node: ast.Constant) -> str:
        if isinstance(node.value, str):
            return f'"{node.value}"'
        elif isinstance(node.value, bool):
            return "true" if node.value else "false"
        return repr(node.value)

    def visit_BinOp(self, node: ast.BinOp) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self.visit(node.op)
        return f"({left} {op} {right})"

    def visit_Compare(self, node: ast.Compare) -> str:
        left = self.visit(node.left)
        comparisons = []
        for op, comparator in zip(node.ops, node.comparators):
            op_str = self.visit(op)
            comp = self.visit(comparator)
            comparisons.append(f"{left} {op_str} {comp}")
            left = comp
        return " && ".join(comparisons)

    def visit_Eq(self, node: ast.Eq) -> str:
        return "=="

    def visit_NotEq(self, node: ast.NotEq) -> str:
        return "!="

    def visit_Lt(self, node: ast.Lt) -> str:
        return "<"

    def visit_LtE(self, node: ast.LtE) -> str:
        return "<="

    def visit_Gt(self, node: ast.Gt) -> str:
        return ">"

    def visit_GtE(self, node: ast.GtE) -> str:
        return ">="

    def visit_If(self, node: ast.If) -> Any:
        test = self.visit(node.test)
        self.lines.append(f"{self.indent()}if ({test}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.lines.append(f"{self.indent()}}}")
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self.lines.append(f"{self.indent()}else ")
                self.visit(node.orelse[0])  # elif
            else:
                self.lines.append(f"{self.indent()}else {{")
                self.indent_level += 1
                for stmt in node.orelse:
                    self.visit(stmt)
                self.indent_level -= 1
                self.lines.append(f"{self.indent()}}}")

    def visit_While(self, node: ast.While) -> Any:
        test = self.visit(node.test)
        self.lines.append(f"{self.indent()}while ({test}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.lines.append(f"{self.indent()}}}")

    def visit_For(self, node: ast.For) -> Any:
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
            return self._handle_range_loop(node)
        target = self.visit(node.target)
        iter_expr = self.visit(node.iter)
        self.lines.append(f"{self.indent()}for (const {target} of {iter_expr}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.lines.append(f"{self.indent()}}}")

    def _handle_range_loop(self, node: ast.For) -> None:
        args = getattr(node.iter, 'args')
        target = self.visit(node.target)
        if len(args) == 1:
            start, end, step = "0", self.visit(args[0]), "1"
        elif len(args) == 2:
            start, end = self.visit(args[0]), self.visit(args[1])
            step = "1"
        elif len(args) == 3:
            start, end, step = map(self.visit, args)
        else:
            raise NotImplementedError("range() with more than 3 arguments is not supported")

        self.lines.append(f"{self.indent()}for (let {target} = {start}; {target} < {end}; {target} += {step}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.lines.append(f"{self.indent()}}}")

    def visit_Dict(self, node: ast.Dict) -> str:
        pairs = []
        for key, value in zip(node.keys, node.values):
            assert isinstance(key, ast.AST)
            js_key = self.visit(key)
            js_value = self.visit(value)
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                pairs.append(f'{js_key}: {js_value}')
            else:
                pairs.append(f'[{js_key}]: {js_value}')
        return f"{{{', '.join(pairs)}}}"

    def visit_Subscript(self, node: ast.Subscript) -> str:
        obj = self.visit(node.value)
        key = self.visit(node.slice)
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str) and node.slice.value.isidentifier():
            return f"{obj}.{node.slice.value}"
        return f"{obj}[{key}]"

    def visit_JoinedStr(self, node: ast.JoinedStr) -> str:
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                parts.append("${" + self.visit(value.value) + "}")
            elif isinstance(value, ast.Constant):
                parts.append(value.value.replace('`', '\\`'))
        return f"`{''.join(parts)}`"

    def generate(self, node: ast.AST) -> str:
        self.visit(node)
        return "\n".join(self.lines)


def python_to_js(python_code: str) -> str:
    tree: ast.AST = ast.parse(python_code)
    generator = JSCodeGenerator()
    return generator.generate(tree)
