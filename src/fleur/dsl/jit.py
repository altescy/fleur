import inspect
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any, Optional, Union, cast, overload

from typing_extensions import Concatenate, ParamSpec, TypeVar

from .ast import (
    GraineArrayNode,
    GraineAssignNode,
    GraineASTExpr,
    GraineBinaryOpNode,
    GraineBlockNode,
    GraineBooleanNode,
    GraineBooleanType,
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
from .types import (
    GraineNumber,
    GraineNumberType,
    GraineObject,
    GraineObjectT,
    GraineString,
    GraineStringType,
    GraineType,
    GraineTypeT,
    PyBooleanCompat,
    PyCallableT,
    PyGraineCompat,
    PyNumberCompat,
    PyRecordCompat,
    PyStringCompat,
)

_T = TypeVar("_T")
_P = ParamSpec("_P")

_BLOCK = ContextVar[GraineBlockNode]("FLEUR_BLOCK", default=GraineBlockNode())


@contextmanager
def use_block() -> Iterator[GraineBlockNode]:
    block = GraineBlockNode()
    token = _BLOCK.set(block)
    try:
        yield block
    finally:
        _BLOCK.reset(token)


def require_block() -> GraineBlockNode:
    return _BLOCK.get()


def auto_let(
    fn: Callable[_P, "GraineObject[GraineASTExpr[GraineTypeT]]"],
) -> Callable[_P, "GraineObject[GraineIdentifierNode[GraineTypeT]]"]:
    @wraps(fn)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> "GraineObject[GraineIdentifierNode[GraineTypeT]]":
        result = fn(*args, **kwargs)
        block = require_block()

        identifier_node = block.new_identifier()
        assignment_node = GraineLetNode(
            identifier=identifier_node,
            value=result.__graine_ast__,
        )
        block.emit(assignment_node)

        return cast(GraineObject[GraineIdentifierNode[GraineTypeT]], _GraineBuilder(identifier_node))

    return wrapper


@overload
def as_interface(obj_or_name: str) -> Callable[[PyCallableT], PyCallableT]: ...
@overload
def as_interface(obj_or_name: PyCallableT) -> PyCallableT: ...


def as_interface(obj_or_name: Union[str, PyCallableT]) -> Union[PyCallableT, Callable[[PyCallableT], PyCallableT]]:
    def decorator(fn: PyCallableT) -> PyCallableT:
        assert isinstance(obj_or_name, str)
        identifier = GraineIdentifierNode(name=obj_or_name)
        if isinstance(obj_or_name, type):
            return cast(PyCallableT, _GraineClassFacade(identifier))
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
def from_python(value: PyBooleanCompat) -> GraineObject[GraineBooleanNode]: ...  # pyright: ignore[reportOverlappingOverload]
@overload
def from_python(value: PyStringCompat) -> GraineObject[GraineStringNode]: ...
@overload
def from_python(value: PyNumberCompat) -> GraineObject[GraineNumberNode]: ...
@overload
def from_python(
    value: list[PyStringCompat],
) -> GraineObject[GraineArrayNode[GraineStringType]]: ...
@overload
def from_python(
    value: list[PyNumberCompat],
) -> GraineObject[GraineArrayNode[GraineNumberType]]: ...
@overload
def from_python(value: list[Any]) -> GraineObject[GraineArrayNode[GraineType]]: ...
@overload
def from_python(value: dict[str, Any]) -> GraineObject[GraineRecordNode]: ...


def boolean(value: PyBooleanCompat) -> GraineObject[GraineBooleanNode]:
    return cast(GraineObject[GraineBooleanNode], _GraineBuilder(GraineBooleanNode(value=value)))


def number(value: PyNumberCompat) -> GraineObject[GraineNumberNode]:
    return cast(GraineObject[GraineNumberNode], _GraineBuilder(GraineNumberNode(value=value)))


def string(value: PyStringCompat) -> GraineObject[GraineStringNode]:
    return cast(GraineObject[GraineStringNode], _GraineBuilder(GraineStringNode(value=value)))


@overload
def array(*elements: PyBooleanCompat) -> GraineObject[GraineArrayNode[GraineBooleanType]]: ...  # pyright: ignore[reportOverlappingOverload]
@overload
def array(*elements: PyNumberCompat) -> GraineObject[GraineArrayNode[GraineNumberType]]: ...
@overload
def array(*elements: PyStringCompat) -> GraineObject[GraineArrayNode[GraineStringType]]: ...
@overload
def array(*elements: GraineNumber) -> GraineObject[GraineArrayNode[GraineNumberType]]: ...
@overload
def array(*elements: GraineString) -> GraineObject[GraineArrayNode[GraineStringType]]: ...
@overload
def array(*elements: Any) -> GraineObject[GraineArrayNode[GraineType]]: ...


def array(*elements: Any) -> GraineObject[GraineArrayNode[GraineType]]:
    return cast(
        GraineObject[GraineArrayNode[GraineType]],
        _GraineBuilder(ast=GraineArrayNode(elements=[ensure_graine(elem).__graine_ast__ for elem in elements])),
    )


def record(**fields: Any) -> GraineObject[GraineRecordNode]:
    return cast(
        GraineObject[GraineRecordNode],
        _GraineBuilder(
            ast=GraineRecordNode(fields={key: ensure_graine(val).__graine_ast__ for key, val in fields.items()})
        ),
    )


@auto_let
@staticmethod
def from_python(value: PyGraineCompat) -> GraineObject:
    if isinstance(value, str):
        return string(value)
    elif isinstance(value, (int, float)):
        return number(float(value))
    elif isinstance(value, list):
        return array(value)
    elif isinstance(value, dict):
        return record(**value)
    else:
        raise TypeError(f"Unsupported type for from_python: {type(value)}")


@overload
def ensure_graine(value: PyNumberCompat) -> "GraineObject[GraineNumberNode]": ...
@overload
def ensure_graine(value: PyStringCompat) -> "GraineObject[GraineStringNode]": ...
@overload
def ensure_graine(value: list[PyStringCompat]) -> "GraineObject[GraineArrayNode[GraineStringType]]": ...
@overload
def ensure_graine(value: list[PyNumberCompat]) -> "GraineObject[GraineArrayNode[GraineNumberType]]": ...
@overload
def ensure_graine(value: list[Any]) -> "GraineObject[GraineArrayNode[GraineType]]": ...
@overload
def ensure_graine(value: PyRecordCompat) -> "GraineObject[GraineRecordNode]": ...
@overload
def ensure_graine(value: GraineObjectT) -> GraineObjectT: ...


def ensure_graine(value: Union[PyGraineCompat, GraineObjectT]) -> Union["GraineObject", GraineObjectT]:
    if isinstance(value, _GraineBuilder):
        return cast(GraineObjectT, value)
    return from_python(cast(PyGraineCompat, value))


def _function_from_python(fn: Callable[..., Any]) -> GraineFunctionNode:
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
        body.emit(GraineReturnNode(value=result.__graine_ast__))

    return GraineFunctionNode(
        name=fn.__name__,
        parameters=parameters,
        body=body,
    )


def _class_from_python(cls: type) -> GraineClassNode:
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


class _GraineBuilder:
    def __init__(self, ast: GraineASTExpr) -> None:
        self.__graine_ast__ = ast

    def __getattr__(self, name: str) -> "GraineObject[GrainePropertyAccessNode]":
        property_access_node = GrainePropertyAccessNode(
            property_name=name,
            receiver=self.__graine_ast__,
        )
        return cast(GraineObject[GrainePropertyAccessNode], _GraineBuilder(ast=property_access_node))

    def __setattr__(self, name: str, value: "GraineObject[GraineASTExpr]") -> None:
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
        block.emit(assignment_node)

    @auto_let
    def __call__(self, *args: Union[PyGraineCompat, "GraineObject"]) -> "GraineObject[GraineCallNode]":
        args = tuple(ensure_graine(arg) for arg in args)
        call_node = GraineCallNode(
            function=self.__graine_ast__,
            arguments=[arg.__graine_ast__ for arg in args],
        )
        return cast(GraineObject[GraineCallNode], _GraineBuilder(call_node))

    @auto_let
    def __getitem__(self, key: Union[int, str, "GraineObject"]) -> "GraineObject[GraineASTExpr]":
        key = ensure_graine(key)
        index_access_node = GraineIndexAccessNode(
            index=key.__graine_ast__,
            receiver=self.__graine_ast__,
        )
        return cast(GraineObject[GraineASTExpr], _GraineBuilder(index_access_node))

    def __setitem__(
        self,
        key: Union[int, str, "GraineObject"],
        value: "GraineObject[GraineASTExpr]",
    ) -> None:
        key = ensure_graine(key)
        assignment_node = GraineAssignNode(
            identifier=GraineIndexAccessNode(
                index=key.__graine_ast__,
                receiver=self.__graine_ast__,
            ),
            value=value.__graine_ast__,
        )
        require_block().emit(assignment_node)

    @auto_let
    def __eq__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Union[PyGraineCompat, "GraineObject[GraineASTExpr]"],
    ) -> "GraineObject[GraineBinaryOpNode]":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op="===",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return cast(GraineObject[GraineBinaryOpNode], _GraineBuilder(binary_op_node))

    @auto_let
    def __add__(
        self,
        other: Union[PyGraineCompat, "GraineObject[GraineASTExpr]"],
    ) -> "GraineObject[GraineBinaryOpNode]":
        other = ensure_graine(other)
        binary_op_node = GraineBinaryOpNode(
            op="+",
            left=self.__graine_ast__,
            right=other.__graine_ast__,
        )
        return cast(GraineObject[GraineBinaryOpNode], _GraineBuilder(binary_op_node))


class _GraineClassFacade(_GraineBuilder):
    def __init__(self, ast: Union[GraineIdentifierNode, GraineClassNode]) -> None:
        self.__graine_ast__ = GraineIdentifierNode(name=ast.name)

    @auto_let
    def __call__(self, *args: Union[PyGraineCompat, "GraineObject"]) -> "GraineObject[GraineConstructionNode]":
        args = tuple(ensure_graine(arg) for arg in args)
        construction_node = GraineConstructionNode(
            class_name=self.__graine_ast__.name,
            arguments=[arg.__graine_ast__ for arg in args],
        )
        return cast(GraineObject[GraineConstructionNode], _GraineBuilder(construction_node))

    def __getitem__(self, key: Any):  # pyright: ignore[reportIncompatibleMethodOverride]
        return Any
