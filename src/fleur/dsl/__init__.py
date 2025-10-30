from collections.abc import Callable
from contextlib import ExitStack
from typing import Any, Optional, TypeVar, Union, cast, overload

from typing_extensions import Self

from ._utils import as_literal, extract_first_grainetype
from .ir import (
    IRBlock,
    IRClassStmt,
    IRExpr,
    IRFunctionStmt,
    IRIdentifierExpr,
    IRLetStmt,
    IRLiteralArrayExpr,
    IRLiteralBooleanExpr,
    IRLiteralNumberExpr,
    IRLiteralRecordExpr,
    IRLiteralStringExpr,
    IRMethodStmt,
    IRNewExpr,
    IRReturnStmt,
)
from .javascript import emit_javascript
from .runtime import require_block, use_block
from .stdlib import Cases, Range
from .types import (
    Array,
    ArrayElementT,
    ArrayExprT,
    ArrayLike,
    Boolean,
    BooleanLike,
    Function,
    GraineType,
    Number,
    NumberLike,
    PyBooleanCompat,
    PyNumberCompat,
    PyStringCompat,
    Record,
    RecordExprT,
    RecordLike,
    RecordValueT,
    String,
    StringLike,
    This,
)

__all__ = ["graine", "parterre"]


def _make_array_from_elements(elements: list[Any]) -> Array[GraineType, IRLiteralArrayExpr]:
    """Helper to create Array from elements with proper type inference."""
    element_exprs = [as_literal(elem)._expr for elem in elements]
    return Array(IRLiteralArrayExpr(element_exprs))


def _make_record_from_fields(fields: dict[str, Any]) -> Record[GraineType, IRLiteralRecordExpr]:
    """Helper to create Record from fields with proper type inference."""
    field_exprs = {key: as_literal(val)._expr for key, val in fields.items()}
    return Record(IRLiteralRecordExpr(field_exprs))


_ClassT = TypeVar("_ClassT", bound=type)
_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])
_GraineCallableT = TypeVar("_GraineCallableT", bound=Callable[..., Optional[GraineType]])
_ElementT = TypeVar("_ElementT")  # For Array element types


class _GraineProperty(property):
    """Custom property class that can hold graine-specific metadata."""

    def __init__(self, fget: Callable[..., Any]) -> None:
        super().__init__(fget)
        self._graine_getter = True
        self._graine_original_method = fget


class graine:
    Number = Number
    Boolean = Boolean
    String = String
    Array = Array
    Record = Record

    BooleanLike = BooleanLike
    NumberLike = NumberLike
    StringLike = StringLike
    ArrayLike = ArrayLike
    RecordLike = RecordLike

    # Array types
    @overload
    @staticmethod
    def literal(value: list[PyNumberCompat]) -> Array[Number[IRLiteralNumberExpr], IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: list[PyStringCompat]) -> Array[String[IRLiteralStringExpr], IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: list[PyBooleanCompat]) -> Array[Boolean[IRLiteralBooleanExpr], IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Record types
    @overload
    @staticmethod
    def literal(value: dict[str, PyNumberCompat]) -> Record[Number[IRLiteralNumberExpr], IRLiteralRecordExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: dict[str, PyStringCompat]) -> Record[String[IRLiteralStringExpr], IRLiteralRecordExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: dict[str, PyBooleanCompat]) -> Record[Boolean[IRLiteralBooleanExpr], IRLiteralRecordExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Generic list/dict fallback
    @overload
    @staticmethod
    def literal(value: list) -> Array[GraineType, IRLiteralArrayExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: dict) -> Record[GraineType, IRLiteralRecordExpr]: ...

    # Scalar types - must come after list/dict to avoid overlap
    @overload
    @staticmethod
    def literal(value: PyStringCompat) -> String[IRLiteralStringExpr]: ...

    @overload
    @staticmethod
    def literal(value: PyBooleanCompat) -> Boolean[IRLiteralBooleanExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def literal(value: PyNumberCompat) -> Number[IRLiteralNumberExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @staticmethod
    def literal(value: Any) -> GraineType:
        return as_literal(value)

    # Primitive types
    @overload
    @staticmethod
    def let(init: NumberLike, name: str = "v") -> Number[IRIdentifierExpr]: ...

    @overload
    @staticmethod
    def let(init: BooleanLike, name: str = "v") -> Boolean[IRIdentifierExpr]: ...

    @overload
    @staticmethod
    def let(init: StringLike, name: str = "v") -> String[IRIdentifierExpr]: ...

    @overload
    @staticmethod
    def let(init: list[NumberLike], name: str = "v") -> Array[Number, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def let(init: list[StringLike], name: str = "v") -> Array[String, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def let(init: list[BooleanLike], name: str = "v") -> Array[Boolean, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Array with Graine types
    @overload
    @staticmethod
    def let(init: Array[ArrayElementT, ArrayExprT], name: str = "v") -> Array[ArrayElementT, IRIdentifierExpr]: ...

    # Generic array fallback
    @overload
    @staticmethod
    def let(init: list, name: str = "v") -> Array[GraineType, IRIdentifierExpr]: ...

    # Record types - specific value types
    @overload
    @staticmethod
    def let(init: dict[str, NumberLike], name: str = "v") -> Record[Number, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def let(init: dict[str, StringLike], name: str = "v") -> Record[String, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def let(init: dict[str, BooleanLike], name: str = "v") -> Record[Boolean, IRIdentifierExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Record with Graine types
    @overload
    @staticmethod
    def let(init: Record[RecordValueT, RecordExprT], name: str = "v") -> Record[RecordValueT, IRIdentifierExpr]: ...

    # Generic record fallback
    @overload
    @staticmethod
    def let(init: dict, name: str = "v") -> Record[GraineType, IRIdentifierExpr]: ...

    @staticmethod
    def let(init: Any, name: str = "v") -> Any:
        block = require_block()
        idx = len(block.body)
        gtype = init if isinstance(init, GraineType) else graine.literal(init)

        # Special case: If init is a ClassWrapper instance (has _graine_class),
        # and it already has an IRIdentifierExpr, just return it
        # This avoids double-wrapping class instances
        if (
            hasattr(type(gtype), "_graine_class")
            and isinstance(gtype._expr, IRIdentifierExpr)
            and gtype._expr.name.startswith("_")
        ):
            return gtype

        var_name = f"{name}_{idx}"
        block.emit(IRLetStmt(name=var_name, value=gtype._expr))
        return type(gtype)(IRIdentifierExpr(var_name))

    @staticmethod
    def range(start: Union[int, float, Number], end: Union[int, float, Number]) -> Range:
        var_name = f"i_{len(require_block().body)}"
        start_expr = start._expr if isinstance(start, Number) else IRLiteralNumberExpr(start)
        end_expr = end._expr if isinstance(end, Number) else IRLiteralNumberExpr(end)
        return Range(var=var_name, start=start_expr, end=end_expr)

    @staticmethod
    def cases() -> Cases:
        return Cases()

    # Array creation with type tracking
    @overload
    @staticmethod
    def array(elements: list[NumberLike]) -> Array[Number, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def array(elements: list[StringLike]) -> Array[String, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def array(elements: list[BooleanLike]) -> Array[Boolean, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Generic fallback
    @overload
    @staticmethod
    def array(elements: list) -> Array[GraineType, IRLiteralArrayExpr]: ...

    @staticmethod
    def array(elements: list) -> Any:  # pyright: ignore[reportInconsistentOverload]
        return _make_array_from_elements(elements)

    # Record creation with type tracking
    @overload
    @staticmethod
    def record(fields: dict[str, NumberLike]) -> Record[Number, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def record(fields: dict[str, StringLike]) -> Record[String, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    @overload
    @staticmethod
    def record(fields: dict[str, BooleanLike]) -> Record[Boolean, IRExpr]: ...  # pyright: ignore[reportOverlappingOverload]

    # Generic fallback
    @overload
    @staticmethod
    def record(fields: dict) -> Record[GraineType, IRLiteralRecordExpr]: ...

    @staticmethod
    def record(fields: dict) -> Any:  # pyright: ignore[reportInconsistentOverload]
        return _make_record_from_fields(fields)

    @overload
    @staticmethod
    def define(fn_or_class: _ClassT) -> _ClassT: ...

    @overload
    @staticmethod
    def define(fn_or_class: _GraineCallableT) -> _GraineCallableT: ...

    @staticmethod
    def define(fn_or_class: Union[type, Callable]) -> Union[type, Callable]:
        """Decorator to define a Graine function or class that transpiles to JavaScript."""
        if isinstance(fn_or_class, type):
            return graine._define_class(fn_or_class)
        else:
            return graine._define_function(fn_or_class)

    @staticmethod
    def _define_function(fn: _GraineCallableT) -> _GraineCallableT:
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

    @staticmethod
    def static(fn: _CallableT) -> _CallableT:
        """Decorator to mark a method as static."""
        fn._graine_static = True  # type: ignore[attr-defined]
        return fn

    @staticmethod
    def getter(fn: Callable[..., Any]) -> _GraineProperty:
        """Decorator to mark a method as a getter.

        Returns a property object so that type checkers recognize it as a property,
        but stores the original method for code generation.
        """
        return _GraineProperty(fn)

    @staticmethod
    def _define_class(class_: _ClassT) -> _ClassT:
        """Decorator to define a Graine class that transpiles to JavaScript."""
        import inspect

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
                import ast
                import textwrap

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


class parterre:
    def __init__(self) -> None:
        self._stack = ExitStack()
        self._block: Optional[IRBlock] = None

    def __enter__(self) -> Self:
        self._stack.__enter__()
        self._stack.enter_context(use_block())
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> Optional[bool]:
        self._block = require_block()
        return self._stack.__exit__(exc_type, exc_value, traceback)

    def germinate(self) -> str:
        return emit_javascript(self._block or require_block())
