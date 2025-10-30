import ast
import inspect
import textwrap
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import Any, Optional, TypeVar, cast

from ._utils import as_literal, extract_first_grainetype
from .ir import (
    IRBlock,
    IRClassStmt,
    IRExpr,
    IRFunctionStmt,
    IRIdentifierExpr,
    IRIfStmt,
    IRLetStmt,
    IRMethodStmt,
    IRNewExpr,
    IRRangeStmt,
    IRReturnStmt,
)
from .runtime import require_block, use_block
from .types import Boolean, Function, GraineType, Number, This

_ClassT = TypeVar("_ClassT", bound=type)
_GraineCallableT = TypeVar("_GraineCallableT", bound=Callable[..., Optional[GraineType]])


class Range:
    def __init__(self, var: str, start: IRExpr, end: IRExpr) -> None:
        self._var = var
        self._start = start
        self._end = end

    def __iter__(self) -> Iterator[Number]:
        block = require_block()
        with use_block() as inner:
            yield Number(IRIdentifierExpr(self._var))
        block.body.append(
            IRRangeStmt(
                var=self._var,
                start=self._start,
                end=self._end,
                body=inner,
            )
        )


class When:
    """Represents a when clause in a cases statement."""

    def __init__(self, cases: "Cases", condition: Optional[Boolean] = None) -> None:
        self._cases = cases
        self._condition = condition._expr if condition is not None else None
        self._block_ctx = None

    def __enter__(self) -> None:
        # Start a new block context
        self._block_ctx = use_block()
        self._block = self._block_ctx.__enter__()

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # Exit the block context
        if self._block_ctx is not None:
            self._block_ctx.__exit__(exc_type, exc_val, exc_tb)
            # Register this when clause with the cases
            self._cases._add_when(self._condition, self._block)


class Cases:
    """Cases statement for conditional branching with multiple conditions."""

    def __init__(self) -> None:
        self._whens: list[tuple[Optional[IRExpr], "IRBlock"]] = []

    def __call__(self, condition: Boolean) -> When:
        """Create a when clause with a condition."""
        return When(self, condition)

    def default(self) -> When:
        """Create a default when clause (always true)."""
        return When(self, None)

    def _add_when(self, condition: Optional[IRExpr], body: "IRBlock") -> None:
        """Add a when clause to the cases."""
        self._whens.append((condition, body))

    def __enter__(self) -> "Cases":
        return self

    def __exit__(self, *args: object) -> None:
        """Build the if-else chain from all when clauses."""
        if not self._whens:
            return

        # Build nested if-else statements from the when clauses
        # First when becomes the outermost if
        # Subsequent whens become else-if (else { if { ... } })
        # Default when (condition=None) becomes the final else

        def build_if_chain(whens: list[tuple[Optional[IRExpr], "IRBlock"]]) -> Optional[IRIfStmt]:
            if not whens:
                return None

            condition, then_body = whens[0]
            remaining = whens[1:]

            if condition is None:
                # This is a default when - should not generate an if statement
                # Return None and let the caller use then_body as else_body
                return None

            # Build the else body from remaining whens
            else_body = None
            if remaining:
                next_if = build_if_chain(remaining)
                if next_if is not None:
                    # Wrap in a block
                    from .ir import IRBlock

                    else_body = IRBlock(body=[next_if])
                else:
                    # The remaining when was a default, use its body
                    if remaining and remaining[0][0] is None:
                        else_body = remaining[0][1]

            return IRIfStmt(
                condition=condition,
                then_body=then_body,
                else_body=else_body,
            )

        first_if = build_if_chain(self._whens)
        if first_if is not None:
            require_block().emit(first_if)


def define_function(fn: _GraineCallableT) -> _GraineCallableT:
    """Compile a Python function to JavaScript.

    Args:
        fn: Python function to compile

    Returns:
        Function wrapper that can be called from DSL code
    """
    function = Function(name=fn.__name__, fn=fn)  # type: ignore[arg-type]

    with use_block() as block:
        # Create arguments for the function
        args = []
        for name, type_ in function.params:
            grainetype_class = extract_first_grainetype(type_)
            # Check if this is a graine-defined class (not a primitive type)
            if hasattr(grainetype_class, "_graine_class"):
                # For class types, create a simple GraineType without instantiation
                # This represents the parameter, not a new instance
                args.append(GraineType(expr=IRIdentifierExpr(name)))
            else:
                # For primitive types, instantiate normally
                args.append(grainetype_class(IRIdentifierExpr(name)))

        ret = fn(*args)
        if ret and hasattr(ret, "_expr"):
            block.emit(IRReturnStmt(value=ret._expr))

    require_block().emit(
        IRFunctionStmt(
            name=function.name,
            params=[name for name, _ in function.params],
            body=block,
        )
    )

    return cast(_GraineCallableT, function)


def define_class(class_: _ClassT) -> _ClassT:
    """Compile a Python class to JavaScript.

    Args:
        class_: Python class to compile

    Returns:
        Class wrapper that can be instantiated from DSL code
    """
    class_name = class_.__name__

    # Extract __init__ for constructor
    init_method = class_.__init__
    init_signature = inspect.signature(init_method)
    # Get parameter names (skip 'self')
    init_params = list(init_signature.parameters.keys())
    if init_params and init_params[0] == "self":
        init_params = init_params[1:]

    # Build constructor body by executing __init__ with This instance
    with use_block() as constructor_block:
        this_instance = This()
        # Create parameter instances for constructor
        param_args = [
            extract_first_grainetype(param.annotation)(IRIdentifierExpr(param.name))
            for param in list(init_signature.parameters.values())[1:]
        ]
        # Execute __init__ to capture property assignments
        init_method(this_instance, *param_args)

    # Create a temporary class wrapper for use in static methods
    # This allows static methods to reference the class being defined
    class TempClassRef:
        """Temporary class reference for use in static methods during class definition."""

        def __call__(self, *args: Any) -> GraineType:
            # When called, create a new instance expression
            arg_exprs: list[IRExpr] = []
            for arg in args:
                if isinstance(arg, GraineType):
                    arg_exprs.append(arg._expr)
                else:
                    arg_exprs.append(as_literal(arg)._expr)
            # Return a GraineType wrapping the new expression
            return GraineType(expr=IRNewExpr(class_name=class_name, args=arg_exprs))

    temp_class_ref = TempClassRef()

    # Collect methods (both functions and properties)
    methods: list[IRMethodStmt] = []
    for method_name, member in inspect.getmembers(class_):
        # Skip __init__ and private methods
        if method_name.startswith("__"):
            continue

        # Check if this is a property (getter)
        if isinstance(member, property):
            # This is a @graine.getter decorated method
            is_static = False
            is_getter = True
            # Get the original method from the property
            method = getattr(member, "_graine_original_method", member.fget)
            if method is None:
                continue
        elif inspect.isfunction(member):
            # Regular method
            method = member
            is_static = getattr(method, "_graine_static", False)
            is_getter = False
        else:
            # Skip non-function, non-property members
            continue

        # Get method signature
        method_signature = inspect.signature(method)
        method_params = list(method_signature.parameters.keys())

        # Check if first parameter is 'self' (for instance methods)
        has_self = method_params and method_params[0] == "self"

        # For static methods, use all params; for instance methods, skip 'self'
        if is_static:
            param_names = method_params
        elif has_self:
            param_names = method_params[1:]
        else:
            param_names = method_params

        # Build method body
        with use_block() as method_block:
            # Check if method source code contains explicit return statement
            method_source = inspect.getsource(method)
            try:
                # Dedent the source to remove class-level indentation
                dedented_source = textwrap.dedent(method_source)
                method_ast = ast.parse(dedented_source)
                has_explicit_return = any(
                    isinstance(node, ast.Return) and node.value is not None for node in ast.walk(method_ast)
                )
            except Exception:
                # If we can't parse, assume no explicit return
                has_explicit_return = False

            if is_static:
                # Static methods don't have 'this', but can reference the class
                param_args = [
                    extract_first_grainetype(param.annotation)(IRIdentifierExpr(param.name))
                    for param in list(method_signature.parameters.values())
                ]
                # Inject the class reference into method's globals so it can be used
                original_globals = method.__globals__.copy()
                method.__globals__[class_name] = temp_class_ref
                try:
                    ret = method(*param_args)
                finally:
                    # Restore original globals
                    method.__globals__.clear()
                    method.__globals__.update(original_globals)
            elif has_self:
                # Instance methods: pass This() as first argument
                this_instance = This()
                param_args = [
                    extract_first_grainetype(param.annotation)(IRIdentifierExpr(param.name))
                    for param in list(method_signature.parameters.values())[1:]
                ]
                ret = method(this_instance, *param_args)
            else:
                # No self parameter (shouldn't happen, but handle gracefully)
                param_args = [
                    extract_first_grainetype(param.annotation)(IRIdentifierExpr(param.name))
                    for param in list(method_signature.parameters.values())
                ]
                ret = method(*param_args)

            # Add return statement only if:
            # 1. Method has explicit return in source code, OR
            # 2. Method is a getter (getters should return their last expression)
            # Note: We check if has_explicit_return to avoid emitting spurious returns from
            # statements like `self.x += 1` which return a Number but shouldn't produce a return
            if ret and (isinstance(ret, GraineType) or hasattr(ret, "_expr")):
                if is_getter:
                    # Getters always return their last expression
                    method_block.emit(IRReturnStmt(value=ret._expr))
                elif has_explicit_return:
                    # Only emit return if source code has explicit return
                    method_block.emit(IRReturnStmt(value=ret._expr))

        methods.append(
            IRMethodStmt(
                name=method_name,
                params=param_names,
                body=method_block,
                is_static=is_static,
                is_getter=is_getter,
            )
        )

    # Emit class statement
    require_block().emit(
        IRClassStmt(
            name=class_name,
            constructor_params=init_params,
            constructor_body=constructor_block,
            methods=methods,
        )
    )

    # Create a wrapper class that can be instantiated
    class ClassWrapper(GraineType[IRIdentifierExpr]):
        def __init__(self, *args: Any) -> None:
            # When instantiated, create a GraineType with IRNewExpr
            arg_exprs: list[IRExpr] = []
            for arg in args:
                if isinstance(arg, GraineType):
                    arg_exprs.append(arg._expr)
                else:
                    arg_exprs.append(as_literal(arg)._expr)

            # Store as a variable
            var_name = f"_{class_name.lower()}_{len(require_block().body)}"
            require_block().emit(IRLetStmt(name=var_name, value=IRNewExpr(class_name=class_name, args=arg_exprs)))

            # Initialize GraineType with the identifier
            super().__init__(expr=IRIdentifierExpr(var_name))
            self._class_name = class_name

    # Copy class name and metadata to wrapper
    ClassWrapper.__name__ = class_name
    ClassWrapper.__qualname__ = class_.__qualname__
    # Store original class for type checking
    ClassWrapper._graine_class = class_  # type: ignore[attr-defined]

    return cast(_ClassT, ClassWrapper)
