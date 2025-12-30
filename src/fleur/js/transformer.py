"""
AST transformer to convert Python code to builder API calls.

This module provides functionality to transform Python AST nodes into
equivalent builder API calls, allowing more natural Python syntax.
"""

import ast
import dataclasses
import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Final, Optional, TypeVar

if TYPE_CHECKING:
    from .builder import StatementBuilder


_CallableT = TypeVar("_CallableT", bound=Callable)

# Marker attribute to identify already-transformed functions
_TRANSFORMED_MARKER: Final = "__fleur_transformed__"

# Function to get/set the current builder context
_GET_CURRENT_BUILDER: Final = "__fleur_get_current_builder__"
_SET_CURRENT_BUILDER: Final = "__fleur_set_current_builder__"


@dataclasses.dataclass
class _ScopeFrame:
    variables: set[str]

    def copy(self) -> "_ScopeFrame":
        return _ScopeFrame(variables=self.variables.copy())


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
        # Scope stack: each element is a set of variable names declared in that scope
        # The first scope contains function parameters
        self.scope_stack: list[_ScopeFrame] = [_ScopeFrame(variables=param_names.copy())]

    def _is_declared(self, var_name: str) -> bool:
        """Check if a variable is declared in any scope (including parent scopes)."""
        for scope in self.scope_stack:
            if var_name in scope.variables:
                return True
        return False

    def _declare_var(self, var_name: str) -> None:
        """Declare a variable in the current scope."""
        self.scope_stack[-1].variables.add(var_name)

    def _push_scope(self) -> None:
        """Push a new scope onto the stack."""
        self.scope_stack.append(_ScopeFrame(variables=set()))

    def _pop_scope(self) -> None:
        """Pop the current scope from the stack."""
        if len(self.scope_stack) > 1:  # Don't pop the root scope
            self.scope_stack.pop()

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

        if self._is_declared(var_name):
            # Reassignment: __fleur_builder__.assign(x, value)
            return ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Name(id=_GET_CURRENT_BUILDER, ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                        attr="assign",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Name(id=var_name, ctx=ast.Load()),
                        value,
                    ],
                    keywords=[],
                ),
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        else:
            # First assignment: x = __fleur_builder__.let("x", value)
            self._declare_var(var_name)
            return ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Name(id=_GET_CURRENT_BUILDER, ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                        attr="let",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Constant(value=var_name),
                        value,
                    ],
                    keywords=[],
                ),
                lineno=node.lineno,
                col_offset=node.col_offset,
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
                        value=ast.Call(
                            func=ast.Name(id=_GET_CURRENT_BUILDER, ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                        attr="ret",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        else:
            # return expr -> __fleur_builder__.ret(expr)
            value = self.visit(node.value)
            return ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Name(id=_GET_CURRENT_BUILDER, ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                        attr="ret",
                        ctx=ast.Load(),
                    ),
                    args=[value],
                    keywords=[],
                ),
                lineno=node.lineno,
                col_offset=node.col_offset,
            )

    def visit_If(self, node: ast.If) -> list[ast.stmt]:
        """
        Transform if statements to __fleur_builder__.if_then_else calls.

        if condition:
            stmt1
            stmt2
        else:
            stmt3

        ->

        with __fleur_builder__.new_context() as __fleur_temp_consequent__:
            transformed_stmt1
            transformed_stmt2

        with __fleur_builder__.new_context() as __fleur_temp_alternate__:
            __fleur_set_current_builder__(__fleur_builder__)
            transformed_stmt3

        __fleur_builder__.if_then_else(condition, __fleur_temp_consequent__.block, __fleur_temp_alternate__.block)
        """
        condition = self.visit(node.test)
        current_frame = self.scope_stack[-1].copy()

        # Generate unique function name
        consequent_name = "__fleur_temp_consequent__"

        # Transform consequent body (no new scope - Python if/else shares function scope)
        consequent_frame = current_frame.copy()
        self.scope_stack.append(consequent_frame)
        consequent_body: list[ast.stmt] = [self.visit(stmt) for stmt in node.body]
        consequent_context = ast.With(
            items=[
                ast.withitem(
                    context_expr=ast.Call(
                        func=ast.Attribute(
                            value=ast.Call(
                                func=ast.Name(id=_GET_CURRENT_BUILDER, ctx=ast.Load()),
                                args=[],
                                keywords=[],
                            ),
                            attr="new_context",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                    optional_vars=ast.Name(id=consequent_name, ctx=ast.Store()),
                )
            ],
            body=consequent_body,
        )
        consequent_block = ast.Attribute(
            value=ast.Name(id=consequent_name, ctx=ast.Load()),
            attr="block",
            ctx=ast.Load(),
        )
        consequent_fn = ast.Lambda(
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg("_")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=consequent_block,
        )
        self.scope_stack.pop()

        # Create alternate function if exists
        alternate_context: Optional[ast.With] = None
        alternate_fn: Optional[ast.expr] = None
        alternate_frame: Optional[_ScopeFrame] = None
        if node.orelse:
            alternate_name = "__fleur_temp_alternate__"
            alternate_frame = current_frame.copy()
            self.scope_stack.append(alternate_frame)

            # Transform alternate body (no new scope - Python if/else shares function scope)
            alternate_body: list[ast.stmt] = [self.visit(stmt) for stmt in node.orelse]
            alternate_context = ast.With(
                items=[
                    ast.withitem(
                        context_expr=ast.Call(
                            func=ast.Attribute(
                                value=ast.Call(
                                    func=ast.Name(id=_GET_CURRENT_BUILDER, ctx=ast.Load()),
                                    args=[],
                                    keywords=[],
                                ),
                                attr="new_context",
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        ),
                        optional_vars=ast.Name(id=alternate_name, ctx=ast.Store()),
                    )
                ],
                body=alternate_body,
            )
            alternate_block = ast.Attribute(
                value=ast.Name(id=alternate_name, ctx=ast.Load()),
                attr="block",
                ctx=ast.Load(),
            )
            alternate_fn = ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg("_")],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=alternate_block,
            )

            self.scope_stack.pop()

        # Create if_then_else call
        call_args: list[ast.expr] = [condition, consequent_fn]
        if alternate_fn:
            call_args.append(alternate_fn)

        if_then_else_call = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Call(
                        func=ast.Name(id=_GET_CURRENT_BUILDER, ctx=ast.Load()),
                        args=[],
                        keywords=[],
                    ),
                    attr="if_then_else",
                    ctx=ast.Load(),
                ),
                args=call_args,
                keywords=[],
            ),
        )

        statements: list[ast.stmt] = []
        statements.append(consequent_context)
        if alternate_context:
            statements.append(alternate_context)
        statements.append(if_then_else_call)

        # Copy location from original if node to all generated statements
        for stmt in statements:
            ast.copy_location(stmt, node)

        return statements


def transform_function_body(fn: Callable, param_names: set[str]) -> str:
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
    func_def = next(
        (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == fn.__name__),
        None,
    )
    if func_def is None:
        raise ValueError(f"Could not find function definition for {fn.__name__}")

    # Transform the function body
    transformer = PyASTTransformer(param_names)
    func_def.body = [transformer.visit(stmt) for stmt in func_def.body]

    # Fix missing locations
    ast.fix_missing_locations(func_def)

    # Convert back to source code
    return ast.unparse(func_def)


def create_transformed_function(fn: _CallableT, param_names: set[str], builder: "StatementBuilder") -> _CallableT:
    """
    Create a new function with transformed body that uses builder API calls.

    Args:
        fn: The original function to transform
        param_names: set of parameter names
        builder: The builder module to inject (will be available as __fleur_builder__)

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
    func_def = next(
        (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == fn.__name__),
        None,
    )
    if func_def is None:
        raise ValueError(f"Could not find function definition for {fn.__name__}")

    # Remove decorators to avoid infinite recursion
    func_def.decorator_list = []

    # Transform the function body
    transformer = PyASTTransformer(param_names)
    new_body: list[ast.stmt] = []
    for stmt in func_def.body:
        # Transform the statement
        result = transformer.visit(stmt)
        # visit_If returns list[ast.stmt], others return single ast.stmt
        if isinstance(result, list):
            new_body.extend(result)
        else:
            new_body.append(result)

    func_def.body = new_body

    # Fix missing locations
    ast.fix_missing_locations(tree)

    # Compile the transformed AST
    code = compile(tree, filename=f"<_fleur_transformed_{fn.__name__}>", mode="exec")

    # Create a new namespace with builder module under safe name
    # Import _CURRENT_BUILDER from builder module's globals
    from .builder import _CURRENT_BUILDER

    namespace = {
        _GET_CURRENT_BUILDER: _CURRENT_BUILDER.get,
        _SET_CURRENT_BUILDER: _CURRENT_BUILDER.set,
    }
    namespace.update(fn.__globals__)

    # Execute to define the function
    exec(code, namespace)

    # Get the transformed function and mark it
    transformed_fn = namespace[fn.__name__]
    setattr(transformed_fn, _TRANSFORMED_MARKER, True)

    # Return the transformed function
    return transformed_fn
