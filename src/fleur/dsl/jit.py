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
def auto_let(fn: Callable[_P, GraineObjectT]) -> Callable[_P, GraineObjectT]: ...
@overload
def auto_let(fn: Callable[_P, "_GraineBuilder"]) -> Callable[_P, "_GraineBuilder"]: ...


def auto_let(
    fn: Callable[_P, Union[GraineObjectT, "_GraineBuilder"]],
) -> Callable[_P, Union[GraineObjectT, "_GraineBuilder"]]:
    @wraps(fn)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> "GraineObjectT":
        result = fn(*args, **kwargs)
        block = require_block()

        assert isinstance(result, HasGraineASTExpr)

        identifier_node = block.new_identifier()
        assignment_node = GraineLetNode(
            identifier=identifier_node,
            value=result.__graine_ast__,
        )
        block.emit(assignment_node)

        return cast(GraineObjectT, _GraineBuilder(identifier_node))

    return wrapper


@overload
def as_interface(obj_or_name: str) -> Callable[[PyCallableT], PyCallableT]: ...
@overload
def as_interface(obj_or_name: PyCallableT) -> PyCallableT: ...


def as_interface(obj_or_name: Union[str, PyCallableT]) -> Union[PyCallableT, Callable[[PyCallableT], PyCallableT]]:
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
    if isinstance(value, (GraineObject, _GraineBuilder)):
        return cast(GraineObject, value)
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


def _class_ast_from_python(cls: type) -> GraineClassNode:
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
            identifier = block.new_identifier()
            block.emit(
                GraineLetNode(
                    identifier=identifier,
                    value=node,
                )
            )
            self.__graine_ast__ = identifier

    return cast(PyClassT, _GraineClassFacade)


class _GraineBuilder(Generic[GraineASTExprT_co]):
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
        block.emit(assignment_node)

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
        require_block().emit(assignment_node)

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
