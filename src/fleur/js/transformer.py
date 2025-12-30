"""
AST transformer to convert Python code to builder API calls.

This module provides functionality to transform Python AST nodes into
equivalent builder API calls, allowing more natural Python syntax.
"""

import ast
import inspect
from typing import Any, Final

# Use a unique prefix to avoid name collisions with user code
_BUILDER_VAR: Final = "__fleur_builder__"

# Marker attribute to identify already-transformed functions
_TRANSFORMED_MARKER: Final = "__fleur_transformed__"

# Function to set the current builder context
_SET_CURRENT_BUILDER: Final = "__fleur_set_current_builder__"


class PyASTTransformer(ast.NodeTransformer):
    """
    Transform Python AST to use builder API calls.

    Transformations:
    - Variable assignments (x = value) -> builder.let("x", value)
    - Reassignments -> builder.assign(x, value)
    - Return statements -> builder.ret(expr)
    - If statements -> builder.if_then_else(...)
    """

    def __init__(self, param_names: set[str]) -> None:
        """
        Initialize transformer.

        Args:
            param_names: set of function parameter names (already declared)
        """
        self.param_names = param_names
        self.declared_vars = param_names.copy()
        self.temp_functions: list[ast.FunctionDef] = []
        self.temp_counter = 0

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        """
        Transform assignment statements.

        x = value -> __fleur_builder__.let("x", value) (first assignment)
        x = value -> __fleur_builder__.assign(x, value) (reassignment)
        """
        # For simplicity, only handle single target assignments
        if len(node.targets) != 1:
            return node

        target = node.targets[0]
        if not isinstance(target, ast.Name):
            # Complex assignments (e.g., a.b = c) not supported yet
            return node

        var_name = target.id
        value = self.visit(node.value)

        if var_name in self.declared_vars:
            # Reassignment: __fleur_builder__.assign(x, value)
            return ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=_BUILDER_VAR, ctx=ast.Load()),
                        attr="assign",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Name(id=var_name, ctx=ast.Load()),
                        value,
                    ],
                    keywords=[],
                )
            )
        else:
            # First assignment: x = __fleur_builder__.let("x", value)
            self.declared_vars.add(var_name)
            return ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=_BUILDER_VAR, ctx=ast.Load()),
                        attr="let",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Constant(value=var_name),
                        value,
                    ],
                    keywords=[],
                ),
            )

    def visit_Return(self, node: ast.Return) -> ast.AST:
        """
        Transform return statements.

        return expr -> __fleur_builder__.ret(expr)  (as expression statement, not return)
        return -> __fleur_builder__.ret()
        """
        if node.value is None:
            # return -> __fleur_builder__.ret()
            return ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=_BUILDER_VAR, ctx=ast.Load()),
                        attr="ret",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[],
                )
            )
        else:
            # return expr -> __fleur_builder__.ret(expr)
            value = self.visit(node.value)
            return ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=_BUILDER_VAR, ctx=ast.Load()),
                        attr="ret",
                        ctx=ast.Load(),
                    ),
                    args=[value],
                    keywords=[],
                )
            )

    def visit_If(self, node: ast.If) -> ast.AST:
        """
        Transform if statements to __fleur_builder__.if_then_else calls.

        if condition:
            stmt1
            stmt2
        else:
            stmt3

        ->

        def __fleur_temp_consequent_N__(b):
            __fleur_set_current_builder__(b)
            transformed_stmt1
            transformed_stmt2

        def __fleur_temp_alternate_N__(b):
            __fleur_set_current_builder__(b)
            transformed_stmt3

        __fleur_builder__.if_then_else(condition, __fleur_temp_consequent_N__, __fleur_temp_alternate_N__)
        """
        condition = self.visit(node.test)

        # Generate unique function name
        consequent_name = f"__fleur_temp_consequent_{self.temp_counter}__"
        self.temp_counter += 1

        # Transform consequent body
        consequent_body: list[ast.stmt] = [self.visit(stmt) for stmt in node.body]  # type: ignore

        # Create preamble for temp functions:
        # 1. __fleur_builder__ = b (rebind to correct builder)
        # 2. __fleur_set_current_builder__(b) (set current builder)
        rebind_builder: ast.stmt = ast.Assign(
            targets=[ast.Name(id=_BUILDER_VAR, ctx=ast.Store())],
            value=ast.Name(id="b", ctx=ast.Load()),
        )

        set_builder_call: ast.stmt = ast.Expr(
            value=ast.Call(
                func=ast.Name(id=_SET_CURRENT_BUILDER, ctx=ast.Load()),
                args=[ast.Name(id="b", ctx=ast.Load())],
                keywords=[],
            )
        )

        consequent_func = ast.FunctionDef(
            name=consequent_name,
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="b", annotation=None)],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[rebind_builder, set_builder_call] + consequent_body,
            decorator_list=[],
            returns=None,
        )
        self.temp_functions.append(consequent_func)

        # Create alternate function if exists
        alternate_name = None
        if node.orelse:
            alternate_name = f"__fleur_temp_alternate_{self.temp_counter}__"
            self.temp_counter += 1

            alternate_body: list[ast.stmt] = [self.visit(stmt) for stmt in node.orelse]  # type: ignore

            alternate_func = ast.FunctionDef(
                name=alternate_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg="b", annotation=None)],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=[rebind_builder, set_builder_call] + alternate_body,
                decorator_list=[],
                returns=None,
            )
            self.temp_functions.append(alternate_func)

        # Create if_then_else call
        call_args: list[ast.expr] = [condition, ast.Name(id=consequent_name, ctx=ast.Load())]
        if alternate_name:
            call_args.append(ast.Name(id=alternate_name, ctx=ast.Load()))

        return ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=_BUILDER_VAR, ctx=ast.Load()),
                    attr="if_then_else",
                    ctx=ast.Load(),
                ),
                args=call_args,
                keywords=[],
            )
        )


def transform_function_body(fn: Any, param_names: set[str]) -> str:
    """
    Transform a function's body to use builder API calls.

    Args:
        fn: The function to transform
        param_names: set of parameter names

    Returns:
        Transformed function source code
    """
    # Get function source code
    source = inspect.getsource(fn)

    # Parse to AST
    tree = ast.parse(source)

    # Find the function definition
    func_def = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn.__name__:
            func_def = node
            break

    if func_def is None:
        raise ValueError(f"Could not find function definition for {fn.__name__}")

    # Transform the function body
    transformer = PyASTTransformer(param_names)
    func_def.body = [transformer.visit(stmt) for stmt in func_def.body]

    # Fix missing locations
    ast.fix_missing_locations(func_def)

    # Convert back to source code
    return ast.unparse(func_def)


def create_transformed_function(fn: Any, param_names: set[str], builder_module: Any) -> Any:
    """
    Create a new function with transformed body that uses builder API calls.

    Args:
        fn: The original function to transform
        param_names: set of parameter names
        builder_module: The builder module to inject (will be available as __fleur_builder__)

    Returns:
        Transformed executable function
    """
    import textwrap

    # Check if already transformed
    if hasattr(fn, _TRANSFORMED_MARKER):
        return fn

    # Get function source code
    source = textwrap.dedent(inspect.getsource(fn))

    # Parse to AST
    tree = ast.parse(source)

    # Find the function definition
    func_def = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn.__name__:
            func_def = node
            break

    if func_def is None:
        raise ValueError(f"Could not find function definition for {fn.__name__}")

    # Remove decorators to avoid infinite recursion
    func_def.decorator_list = []

    # Transform the function body
    transformer = PyASTTransformer(param_names)
    new_body: list[ast.stmt] = []
    for stmt in func_def.body:
        # Remember the current temp_functions count
        before_count = len(transformer.temp_functions)

        # Transform the statement
        transformed_stmt = transformer.visit(stmt)

        # If new temp functions were added, insert them before this statement
        if len(transformer.temp_functions) > before_count:
            new_funcs = transformer.temp_functions[before_count:]
            new_body.extend(new_funcs)

        new_body.append(transformed_stmt)

    func_def.body = new_body

    # Fix missing locations
    ast.fix_missing_locations(tree)

    # Compile the transformed AST
    code = compile(tree, filename=f"<transformed_{fn.__name__}>", mode="exec")

    # Create a new namespace with builder module under safe name
    # Import _CURRENT_BUILDER from builder module's globals
    from . import builder as builder_module_import

    namespace = {
        _BUILDER_VAR: builder_module,
        _SET_CURRENT_BUILDER: builder_module_import._CURRENT_BUILDER.set,
    }
    namespace.update(fn.__globals__)

    # Execute to define the function
    exec(code, namespace)

    # Get the transformed function and mark it
    transformed_fn = namespace[fn.__name__]
    setattr(transformed_fn, _TRANSFORMED_MARKER, True)

    # Return the transformed function
    return transformed_fn
