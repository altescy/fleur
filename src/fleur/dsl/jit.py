"""
Just-In-Time compilation and builder layer for Graine DSL.

This module provides the bridge between Python code execution and AST construction.
It uses the Proxy pattern to intercept Python operations and convert them into
Graine AST nodes.

Key components:
- _GraineBuilder: Proxy class that intercepts Python operations
- auto_let: Decorator for automatic let-binding creation
- use_block/require_block: Context management for statement emission
- ensure_graine: Conversion between Python and Graine values
- _function_from_python/_class_from_python: Introspection and conversion utilities
"""

import inspect
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any, Generic, Optional, Union, cast, overload

from typing_extensions import Concatenate, ParamSpec, TypeVar

from .ast import (
    GraineArrayNode,
    GraineAssignNode,
    GraineASTStmt,
    GraineBinaryOpNode,
    GraineBlockNode,
    GraineBooleanNode,
    GraineCallNode,
    GraineClassNode,
    GraineConstructionNode,
    GraineFunctionNode,
    GraineIdentifierNode,
    GraineIndexAccessNode,
    GraineLetNode,
    GraineMethodNode,
    GraineNumberNode,
    GrainePropertyAccessNode,
    GraineRecordNode,
    GraineReturnNode,
    GraineStringNode,
)
from .errors import GraineBlockError, GraineTypeError, format_type_error
from .types import (
    GraineArray,
    GraineASTExprT_co,
    GraineBoolean,
    GraineNumber,
    GraineObject,
    GraineObjectT,
    GraineRecord,
    GraineString,
    HasGraineASTExpr,
    PyBooleanCompat,
    PyCallableT,
    PyClassT,
    PyGraineCompat,
    PyNumberCompat,
    PyRecordCompat,
    PyStringCompat,
)

_T = TypeVar("_T")
_P = ParamSpec("_P")

_BLOCK = ContextVar[GraineBlockNode]("FLEUR_BLOCK", default=GraineBlockNode())
_IDENTIFIER_COUNTER = ContextVar[int]("FLEUR_ID_COUNTER", default=0)


@contextmanager
def use_block() -> Iterator[GraineBlockNode]:
    """
    Context manager for creating a new statement block.

    This creates a new GraineBlockNode and sets it as the current block
    for statement emission. When the context exits, the previous block
    is restored.

    Yields:
        A new GraineBlockNode for collecting statements

    Example:
        with use_block() as block:
            # Statements emitted here go into 'block'
            ...
        # block now contains all emitted statements
    """
    block = GraineBlockNode()
    token = _BLOCK.set(block)
    try:
        yield block
    finally:
        _BLOCK.reset(token)


def require_block() -> GraineBlockNode:
    """
    Get the current statement block.

    Returns:
        The current GraineBlockNode for statement emission

    Raises:
        GraineBlockError: If no block context is active
    """
    try:
        return _BLOCK.get()
    except LookupError as e:
        raise GraineBlockError(
            "No active block context. Make sure you're inside a 'with parterre()' or 'use_block()' context."
        ) from e


def emit_statement(block: GraineBlockNode, *statements: GraineASTStmt) -> None:
    """
    Emit statements to a block.

    This function adds one or more statements to the given block.

    Args:
        block: The block to emit statements to
        *statements: Statements to add to the block

    Example:
        block = GraineBlockNode()
        emit_statement(block, GraineLetNode(...))
    """
    block.statements.extend(statements)


def new_identifier(prefix: str = "_v_") -> GraineIdentifierNode:
    """
    Generate a unique identifier using a global counter.

    This ensures that all identifiers are unique across the entire code generation
    context, preventing variable name collisions even in nested scopes.

    Args:
        prefix: Prefix for the generated identifier name (default: "_v_")

    Returns:
        A new identifier node with a unique name

    Example:
        id1 = new_identifier()  # Creates "_v_0"
        id2 = new_identifier()  # Creates "_v_1"
    """
    counter = _IDENTIFIER_COUNTER.get()
    _IDENTIFIER_COUNTER.set(counter + 1)
    name = f"{prefix}{counter}"
    return GraineIdentifierNode(name=name)


@overload
def auto_let(fn: Callable[_P, GraineObjectT]) -> Callable[_P, GraineObjectT]: ...
@overload
def auto_let(fn: Callable[_P, "_GraineBuilder"]) -> Callable[_P, "_GraineBuilder"]: ...


def auto_let(
    fn: Callable[_P, Union[GraineObjectT, "_GraineBuilder"]],
) -> Callable[_P, Union[GraineObjectT, "_GraineBuilder"]]:
    """
    Decorator that automatically creates let-bindings for expression results.

    This ensures proper evaluation order by assigning the result of a complex
    expression to an intermediate variable before use. This prevents issues
    with side effects and ensures the generated JavaScript behaves correctly.

    Args:
        fn: Function that returns a Graine object or builder

    Returns:
        Wrapped function that emits a let statement and returns an identifier

    Example:
        @auto_let
        def add(a, b):
            return _GraineBuilder(GraineBinaryOpNode("+", a, b))

        # Generates:
        # let _v_0 = (a + b);
        # Returns: identifier referencing _v_0
    """

    @wraps(fn)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> "GraineObjectT":
        result = fn(*args, **kwargs)
        block = require_block()

        assert isinstance(result, HasGraineASTExpr)

        identifier_node = new_identifier()
        assignment_node = GraineLetNode(
            identifier=identifier_node,
            value=result.__graine_ast__,
        )
        emit_statement(block, assignment_node)

        return cast(GraineObjectT, _GraineBuilder(identifier_node))

    return wrapper


@overload
def as_interface(obj_or_name: str) -> Callable[[PyCallableT], PyCallableT]: ...
@overload
def as_interface(obj_or_name: PyCallableT) -> PyCallableT: ...


def as_interface(obj_or_name: Union[str, PyCallableT]) -> Union[PyCallableT, Callable[[PyCallableT], PyCallableT]]:
    """
    Decorator to mark a class as a JavaScript interface.

    This creates a Graine facade for existing JavaScript objects (like Math,
    Document, etc.) without generating class definitions. The class is replaced
    with a builder that references the JavaScript identifier.

    Args:
        obj_or_name: Either a class or a string name for the JavaScript object

    Returns:
        Decorated class or decorator function

    Example:
        @as_interface
        class Math:
            @staticmethod
            def sqrt(x): ...

        # Math references the JavaScript 'Math' object directly
    """

    def decorator(fn: PyCallableT) -> PyCallableT:
        assert isinstance(obj_or_name, str)
        identifier = GraineIdentifierNode(name=obj_or_name)
        return cast(PyCallableT, _GraineBuilder(identifier))

    if isinstance(obj_or_name, str):
        return decorator

    obj = obj_or_name
    obj_or_name = obj.__name__

    return decorator(obj)


def as_decorator(fn: Callable[Concatenate[PyCallableT, _P], _T]) -> Callable[_P, Callable[[PyCallableT], _T]]:
    return fn  # type: ignore


#
# Object System
#


@overload
def from_python(value: PyBooleanCompat) -> GraineBoolean: ...  # pyright: ignore[reportOverlappingOverload]
@overload
def from_python(value: PyNumberCompat) -> GraineNumber: ...
@overload
def from_python(value: PyStringCompat) -> GraineString: ...
@overload
def from_python(value: list[GraineObjectT]) -> GraineArray[GraineObjectT]: ...
@overload
def from_python(value: list[PyBooleanCompat]) -> GraineArray[GraineBoolean]: ...
@overload
def from_python(value: list[PyNumberCompat]) -> GraineArray[GraineNumber]: ...
@overload
def from_python(value: list[PyStringCompat]) -> GraineArray[GraineString]: ...
@overload
def from_python(value: list[Any]) -> GraineArray: ...
@overload
def from_python(value: dict[str, PyBooleanCompat]) -> GraineRecord[GraineBoolean]: ...
@overload
def from_python(value: dict[str, GraineObjectT]) -> GraineRecord[GraineObjectT]: ...
@overload
def from_python(value: dict[str, PyNumberCompat]) -> GraineRecord[GraineNumber]: ...
@overload
def from_python(value: dict[str, PyStringCompat]) -> GraineRecord[GraineString]: ...
@overload
def from_python(value: dict[str, Any]) -> GraineRecord: ...


def from_python(value: PyGraineCompat) -> GraineObject:
    if isinstance(value, bool):
        return boolean(value)
    elif isinstance(value, str):
        return string(value)
    elif isinstance(value, (int, float)):
        return number(float(value))
    elif isinstance(value, list):
        return array(*value)
    elif isinstance(value, dict):
        return record(**value)
    else:
        supported = "bool, int, float, str, list, dict"
        raise GraineTypeError(format_type_error(value, supported))


def boolean(value: PyBooleanCompat) -> GraineBoolean:
    return cast(GraineBoolean, _GraineBuilder(GraineBooleanNode(value=value)))


def number(value: PyNumberCompat) -> GraineNumber:
    return cast(GraineNumber, _GraineBuilder(GraineNumberNode(value=value)))


def string(value: PyStringCompat) -> GraineString:
    return cast(GraineString, _GraineBuilder(GraineStringNode(value=value)))


@overload
def array(*elements: PyBooleanCompat) -> GraineArray[GraineBoolean]: ...  # pyright: ignore[reportOverlappingOverload]
@overload
def array(*elements: PyNumberCompat) -> GraineArray[GraineNumber]: ...
@overload
def array(*elements: PyStringCompat) -> GraineArray[GraineString]: ...
@overload
def array(*elements: GraineNumber) -> GraineArray[GraineNumber]: ...
@overload
def array(*elements: GraineString) -> GraineArray[GraineString]: ...
@overload
def array(*elements: Any) -> GraineArray: ...


def array(*elements: Any) -> GraineArray:
    return cast(
        GraineArray,
        _GraineBuilder(ast=GraineArrayNode(elements=[ensure_graine(elem).__graine_ast__ for elem in elements])),
    )


@overload
def record(**fields: PyBooleanCompat) -> GraineRecord[GraineBoolean]: ...  # pyright: ignore[reportOverlappingOverload]
@overload
def record(**fields: PyNumberCompat) -> GraineRecord[GraineNumber]: ...
@overload
def record(**fields: PyStringCompat) -> GraineRecord[GraineString]: ...
@overload
def record(**fields: GraineObjectT) -> GraineRecord[GraineObjectT]: ...
@overload
def record(**fields: Any) -> GraineRecord: ...


def record(**fields: Any) -> GraineRecord:
    return cast(
        GraineRecord,
        _GraineBuilder(
            ast=GraineRecordNode(fields={key: ensure_graine(val).__graine_ast__ for key, val in fields.items()})
        ),
    )


@overload
def ensure_graine(value: PyNumberCompat) -> GraineNumber: ...
@overload
def ensure_graine(value: PyStringCompat) -> GraineString: ...
@overload
def ensure_graine(value: list[PyStringCompat]) -> GraineArray[GraineString]: ...
@overload
def ensure_graine(value: list[PyNumberCompat]) -> GraineArray[GraineNumber]: ...
@overload
def ensure_graine(value: list[Any]) -> GraineArray: ...
@overload
def ensure_graine(value: PyRecordCompat) -> GraineRecord: ...
@overload
def ensure_graine(value: GraineObjectT) -> GraineObjectT: ...


def ensure_graine(value: Any) -> GraineObject:
    """
    Convert a value to a Graine object if it isn't already.

    This is used to handle mixed Python/Graine values in operations,
    automatically converting Python primitives to Graine equivalents.

    Args:
        value: Either a Graine object or a Python primitive

    Returns:
        A Graine object (either the original or a converted version)

    Example:
        ensure_graine(42)  # Returns GraineNumber
        ensure_graine(graine.number(42))  # Returns as-is
    """
    if isinstance(value, (GraineObject, _GraineBuilder)):
        return cast(GraineObject, value)
    return from_python(cast(PyGraineCompat, value))


def _function_from_python(fn: Callable[..., Any]) -> GraineFunctionNode:
    """
    Convert a Python function to a Graine function AST node.

    This introspects the Python function signature and body, executing it
    with proxy arguments to build the AST. Special handling is provided
    for 'self' parameters in methods.

    Args:
        fn: Python function to convert

    Returns:
        GraineFunctionNode representing the function

    Example:
        def add(a, b):
            return a + b

        node = _function_from_python(add)
        # Generates function AST with return statement
    """
    sig = inspect.signature(fn)
    parameters = [GraineIdentifierNode(name=param.name) for param in sig.parameters.values()]

    has_self = parameters and parameters[0].name == "self"
    if has_self:
        parameters = parameters[1:]

    with use_block() as body:
        param_asts: list = [_GraineBuilder(param) for param in parameters]
        if has_self:
            param_asts.insert(0, _GraineBuilder(GraineIdentifierNode(name="this")))
        result = fn(*param_asts)

    if result is not None:
        emit_statement(body, GraineReturnNode(value=result.__graine_ast__))

    return GraineFunctionNode(
        name=fn.__name__,
        parameters=parameters,
        body=body,
    )


def _class_ast_from_python(cls: type) -> GraineClassNode:
    """
    Convert a Python class to a Graine class AST node.

    This introspects the class definition, converting __init__ to a constructor,
    methods to class methods, and properties to getters/setters.

    Args:
        cls: Python class to convert

    Returns:
        GraineClassNode representing the class

    Example:
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        node = _class_ast_from_python(Point)
        # Generates class with constructor
    """
    methods = []
    constructor_node: Optional[GraineFunctionNode] = None
    for attr_name in dir(cls):
        if attr_name == "__init__":
            init_method = getattr(cls, attr_name)
            if init_method is object.__init__:
                continue
            function_node = _function_from_python(init_method)
            constructor_node = GraineFunctionNode(
                name="constructor",
                parameters=function_node.parameters,
                body=function_node.body,
            )
            continue
        if attr_name.startswith("__"):
            # Skip python's special methods
            continue
        attr = getattr(cls, attr_name)
        if callable(attr):
            method_node = GraineMethodNode(
                name=attr_name,
                function=_function_from_python(attr),
            )
            methods.append(method_node)
        elif isinstance(attr, property):
            if callable(attr.fget):
                method_node = GraineMethodNode(
                    name=attr_name,
                    function=_function_from_python(attr.fget),
                    accessor="get",
                )
                methods.append(method_node)
            if callable(attr.fset):
                method_node = GraineMethodNode(
                    name=attr_name,
                    function=_function_from_python(attr.fset),
                    accessor="set",
                )
                methods.append(method_node)

    return GraineClassNode(
        name=cls.__name__,
        constructor=constructor_node,
        methods=methods,
    )


def _class_facade_from_python(cls: PyClassT, ast: GraineClassNode) -> PyClassT:
    original_class = cls

    class _GraineClassFacade(_GraineBuilder):
        __graine_ast__ = GraineIdentifierNode(name=ast.name)

        def __class_getitem__(cls, item: Any) -> Any:
            return original_class.__class_getitem__(item)

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            args = tuple(ensure_graine(arg) for arg in args)
            node = GraineConstructionNode(
                class_name=ast.name,
                arguments=[arg.__graine_ast__ for arg in args],
            )
            block = require_block()
            identifier = new_identifier()
            emit_statement(
                block,
                GraineLetNode(
                    identifier=identifier,
                    value=node,
                ),
            )
            self.__graine_ast__ = identifier

    return cast(PyClassT, _GraineClassFacade)


class _GraineBuilder(Generic[GraineASTExprT_co]):
    """
    Proxy class that intercepts Python operations and builds AST nodes.

    This is the core of the JIT system. It wraps an AST node and intercepts
    magic methods (__getattr__, __call__, __add__, etc.) to build complex
    AST expressions from natural Python syntax.

    The __graine_ast__ attribute holds the actual AST node being built.

    Example:
        builder = _GraineBuilder(GraineNumberNode(42))
        result = builder + 10  # Creates BinaryOpNode
        func = builder.method()  # Creates CallNode
    """

    def __init__(self, ast: GraineASTExprT_co) -> None:
        self.__graine_ast__ = ast

    def __getattr__(self, name: str) -> "_GraineBuilder":
        property_access_node = GrainePropertyAccessNode(
            property_name=name,
            receiver=self.__graine_ast__,
        )
        return _GraineBuilder(ast=property_access_node)

    def __setattr__(self, name: str, value: GraineObject) -> None:
        if name == "__graine_ast__":
            super().__setattr__(name, value)
            return
        block = require_block()
        assignment_node = GraineAssignNode(
            identifier=GrainePropertyAccessNode(
                property_name=name,
                receiver=self.__graine_ast__,
            ),
            value=value.__graine_ast__,
        )
        emit_statement(block, assignment_node)

    @auto_let
    def __call__(self, *args: Union[PyGraineCompat, GraineObject]) -> "_GraineBuilder":
        args = tuple(ensure_graine(arg) for arg in args)
        call_node = GraineCallNode(
            function=self.__graine_ast__,
            arguments=[arg.__graine_ast__ for arg in args],
        )
        return _GraineBuilder(call_node)

    @auto_let
    def __getitem__(self, key: Union[int, str, "GraineObject"]) -> "_GraineBuilder":
        graine_key = ensure_graine(key)
        index_access_node = GraineIndexAccessNode(
            index=graine_key.__graine_ast__,
            receiver=self.__graine_ast__,
        )
        return _GraineBuilder(index_access_node)

    def __setitem__(
        self,
        key: Union[int, str, "GraineObject"],
        value: Union[PyGraineCompat, "GraineObject"],
    ) -> None:
        key = ensure_graine(key)
        value = ensure_graine(value)
        assignment_node = GraineAssignNode(
            identifier=GraineIndexAccessNode(
                index=key.__graine_ast__,
                receiver=self.__graine_ast__,
            ),
            value=value.__graine_ast__,
        )
        emit_statement(require_block(), assignment_node)

    @auto_let
    def __eq__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Union[PyGraineCompat, "GraineObject"],
    ) -> "_GraineBuilder":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op="===",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return _GraineBuilder(binary_op_node)

    @auto_let
    def __ne__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Union[PyGraineCompat, "GraineObject"],
    ) -> "_GraineBuilder":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op="!==",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return _GraineBuilder(binary_op_node)

    @auto_let
    def __lt__(
        self,
        other: Union[PyGraineCompat, "GraineObject"],
    ) -> "_GraineBuilder":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op="<",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return _GraineBuilder(binary_op_node)

    @auto_let
    def __le__(
        self,
        other: Union[PyGraineCompat, "GraineObject"],
    ) -> "_GraineBuilder":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op="<=",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return _GraineBuilder(binary_op_node)

    @auto_let
    def __gt__(
        self,
        other: Union[PyGraineCompat, "GraineObject"],
    ) -> "_GraineBuilder":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op=">",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return _GraineBuilder(binary_op_node)

    @auto_let
    def __ge__(
        self,
        other: Union[PyGraineCompat, "GraineObject"],
    ) -> "_GraineBuilder":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op=">=",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return _GraineBuilder(binary_op_node)

    @auto_let
    def __add__(
        self,
        other: Union[PyGraineCompat, "GraineObject"],
    ) -> "_GraineBuilder":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op="+",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return _GraineBuilder(binary_op_node)

    def items(self) -> "_GraineBuilder":
        call_node = GraineCallNode(
            function=GraineIdentifierNode(name="Object.entries"),
            arguments=[self.__graine_ast__],
        )
        return _GraineBuilder(call_node)
