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
    GraineNumberType,
    GraineObject,
    GraineObjectT,
    GraineStringType,
    GraineType,
    GraineTypeT,
    PyCallableT,
    PyGraineCompat,
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


@overload
def ensure_graine(value: Union[int, float]) -> "GraineObject[GraineNumberNode]": ...
@overload
def ensure_graine(value: str) -> "GraineObject[GraineStringNode]": ...
@overload
def ensure_graine(value: list[str]) -> "GraineObject[GraineArrayNode[GraineStringType]]": ...
@overload
def ensure_graine(value: list[Union[int, float]]) -> "GraineObject[GraineArrayNode[GraineNumberType]]": ...
@overload
def ensure_graine(value: list[Any]) -> "GraineObject[GraineArrayNode[GraineType]]": ...
@overload
def ensure_graine(value: dict[str, Any]) -> "GraineObject[GraineRecordNode]": ...
@overload
def ensure_graine(value: GraineObjectT) -> GraineObjectT: ...


def ensure_graine(value: Union[PyGraineCompat, GraineObjectT]) -> Union["GraineObject", GraineObjectT]:
    from .. import graine

    if isinstance(value, _GraineBuilder):
        return cast(GraineObjectT, value)
    return graine.from_python(cast(PyGraineCompat, value))


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


def as_identifier(obj: PyCallableT) -> PyCallableT:
    identifier = GraineIdentifierNode(name=obj.__name__)
    return cast(PyCallableT, _GraineBuilder(identifier))


def as_decorator(fn: Callable[Concatenate[PyCallableT, _P], _T]) -> Callable[_P, Callable[[PyCallableT], _T]]:
    return fn  # type: ignore


#
# Object System
#


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
    def __init__(self, ast: GraineClassNode) -> None:
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
