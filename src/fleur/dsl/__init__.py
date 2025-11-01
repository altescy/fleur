from contextlib import ExitStack
from typing import Any, Final, Optional, cast, overload

from typing_extensions import Self, TypeAlias

from . import ast, jit, stdlib, types
from .javascript import emit_javascript

__all__ = ["graine", "parterre"]


class graine:
    # Types
    Number: TypeAlias = types.GraineNumber
    String: TypeAlias = types.GraineString
    Array: TypeAlias = types.GraineArray
    Record: TypeAlias = types.GraineRecord

    # Type constructors
    @jit.auto_let
    @staticmethod
    def boolean(value: types.PyBooleanCompat) -> types.GraineObject[ast.GraineBooleanNode]:
        return jit.boolean(value)

    @jit.auto_let
    @staticmethod
    def number(value: types.PyNumberCompat) -> types.GraineObject[ast.GraineNumberNode]:
        return jit.number(value)

    @jit.auto_let
    @staticmethod
    def string(value: types.PyStringCompat) -> types.GraineObject[ast.GraineStringNode]:
        return jit.string(value)

    @overload
    def array(*elements: types.PyBooleanCompat) -> types.GraineObject[ast.GraineArrayNode[types.GraineBooleanType]]: ...  # pyright: ignore[reportOverlappingOverload]
    @overload
    def array(*elements: types.PyNumberCompat) -> types.GraineObject[ast.GraineArrayNode[types.GraineNumberType]]: ...
    @overload
    def array(*elements: types.PyStringCompat) -> types.GraineObject[ast.GraineArrayNode[types.GraineStringType]]: ...
    @overload
    def array(*elements: types.GraineNumber) -> types.GraineObject[ast.GraineArrayNode[types.GraineNumberType]]: ...
    @overload
    def array(*elements: types.GraineString) -> types.GraineObject[ast.GraineArrayNode[types.GraineStringType]]: ...
    @overload
    def array(*elements: Any) -> types.GraineObject[ast.GraineArrayNode[types.GraineType]]: ...

    @jit.auto_let
    @staticmethod
    def array(*elements: Any) -> types.GraineObject[ast.GraineArrayNode[types.GraineType]]:
        return jit.array(*elements)

    @jit.auto_let
    @staticmethod
    def record(**fields: Any) -> types.GraineObject[ast.GraineASTExpr[types.GraineRecordType]]:
        return jit.record(**fields)

    @overload
    @staticmethod
    def from_python(value: types.PyBooleanCompat) -> types.GraineObject[ast.GraineBooleanNode]: ...  # pyright: ignore[reportOverlappingOverload]
    @overload
    @staticmethod
    def from_python(value: types.PyStringCompat) -> types.GraineObject[ast.GraineStringNode]: ...
    @overload
    @staticmethod
    def from_python(value: types.PyNumberCompat) -> types.GraineObject[ast.GraineNumberNode]: ...
    @overload
    @staticmethod
    def from_python(
        value: list[types.PyStringCompat],
    ) -> types.GraineObject[ast.GraineArrayNode[types.GraineStringType]]: ...
    @overload
    @staticmethod
    def from_python(
        value: list[types.PyNumberCompat],
    ) -> types.GraineObject[ast.GraineArrayNode[types.GraineNumberType]]: ...
    @overload
    @staticmethod
    def from_python(value: list[Any]) -> types.GraineObject[ast.GraineArrayNode[types.GraineType]]: ...
    @overload
    @staticmethod
    def from_python(value: dict[str, Any]) -> types.GraineObject[ast.GraineRecordNode]: ...

    @staticmethod
    def from_python(value: types.PyGraineCompat) -> types.GraineObject:
        return jit.from_python(value)

    @staticmethod
    def func(fn: types.PyCallableT) -> types.PyCallableT:
        func_ast = jit._function_from_python(fn)
        jit.require_block().emit(func_ast)
        return cast(types.PyCallableT, jit._GraineBuilder(ast.GraineIdentifierNode(name=func_ast.name)))

    @staticmethod
    def cls(cls_: types.PyClassT) -> types.PyClassT:
        class_ast = jit._class_from_python(cls_)
        jit.require_block().emit(class_ast)
        return cast(types.PyClassT, jit._GraineClassFacade(class_ast))

    # Control flow
    when: Final = staticmethod(stdlib.when)
    case: Final = staticmethod(stdlib.case)
    foreach: Final = staticmethod(stdlib.foreach)

    # Special operations
    typeof: Final = staticmethod(stdlib.typeof)
    instanceof: Final = staticmethod(stdlib.instanceof)

    # Standard library
    math: Final = stdlib.Math
    json: Final = stdlib.JSON

    # Global Types
    Document: TypeAlias = stdlib.Document
    Element: TypeAlias = stdlib.Element
    Event: TypeAlias = stdlib.Event
    EventTarget: TypeAlias = stdlib.EventTarget
    Node: TypeAlias = stdlib.Node
    Object: TypeAlias = stdlib.Object

    # Global Objects
    document: Final = jit.as_interface("document")(Document)


class parterre:
    def __init__(self) -> None:
        self._stack = ExitStack()
        self._block: Optional[ast.GraineBlockNode] = None

    def __enter__(self) -> Self:
        self._stack.__enter__()
        self._stack.enter_context(jit.use_block())
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> Optional[bool]:
        self._block = jit.require_block()
        return self._stack.__exit__(exc_type, exc_value, traceback)

    def germinate(self) -> str:
        return emit_javascript(self._block or jit.require_block())
