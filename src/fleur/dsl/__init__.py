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

    # Type constructors
    @jit.auto_let
    @staticmethod
    def boolean(value: types.PyBooleanCompat) -> types.GraineObject[ast.GraineBooleanNode]:
        return cast(types.GraineObject[ast.GraineBooleanNode], jit._GraineBuilder(ast.GraineBooleanNode(value=value)))

    @jit.auto_let
    @staticmethod
    def number(value: types.PyNumberCompat) -> types.GraineObject[ast.GraineNumberNode]:
        return cast(types.GraineObject[ast.GraineNumberNode], jit._GraineBuilder(ast.GraineNumberNode(value=value)))

    @jit.auto_let
    @staticmethod
    def string(value: types.PyStringCompat) -> types.GraineObject[ast.GraineStringNode]:
        return cast(types.GraineObject[ast.GraineStringNode], jit._GraineBuilder(ast.GraineStringNode(value=value)))

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
        return cast(
            types.GraineObject[ast.GraineArrayNode[types.GraineType]],
            jit._GraineBuilder(
                ast=ast.GraineArrayNode(elements=[jit.ensure_graine(elem).__graine_ast__ for elem in elements])
            ),
        )

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

    @jit.auto_let
    @staticmethod
    def from_python(value: types.PyGraineCompat) -> types.GraineObject:
        if isinstance(value, str):
            return graine.string(value)
        elif isinstance(value, (int, float)):
            return graine.number(float(value))
        elif isinstance(value, list):
            return graine.array(value)
        else:
            raise TypeError(f"Unsupported type for from_python: {type(value)}")

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
    math: Final = stdlib.math


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
