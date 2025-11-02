from typing import Any, Final, cast, overload

from . import ast, jit, types
from .stdlib import (
    JSON,
    Document,
    Element,
    Event,
    EventTarget,
    Math,
    Node,
    Proxy,
    case,
    foreach,
    instanceof,
    typeof,
    when,
)
from .types import (
    GraineArray as Array,
)
from .types import (
    GraineBoolean as Boolean,
)
from .types import (
    GraineFunction as Function,
)
from .types import (
    GraineNumber as Number,
)
from .types import (
    GraineObject as Class,
)
from .types import (
    GraineRecord as Record,
)
from .types import (
    GraineString as String,
)

__all__ = [
    # Types
    "Boolean",
    "Number",
    "String",
    "Array",
    "Record",
    "Function",
    "Class",
    # Type constructors
    "boolean",
    "number",
    "string",
    "array",
    "record",
    "func",
    "cls",
    "from_python",
    # Control flow
    "when",
    "case",
    "foreach",
    # Special operations
    "typeof",
    "instanceof",
    # Standard library
    "math",
    "json",
    # Global Types
    "Document",
    "Element",
    "Node",
    "EventTarget",
    "Event",
    "Proxy",
    # Global objects
    "document",
]

math: Final = Math
json: Final = JSON

document: Final = jit.as_interface("document")(Document)


@jit.auto_let
def boolean(value: types.PyBooleanCompat) -> Boolean:
    return jit.boolean(value)


@jit.auto_let
def number(value: types.PyNumberCompat) -> Number:
    return jit.number(value)


@jit.auto_let
def string(value: types.PyStringCompat) -> String:
    return jit.string(value)


@overload
def array() -> Array: ...
@overload
def array(*elements: types.PyNumberCompat) -> Array[Number]: ...
@overload
def array(*elements: types.PyStringCompat) -> Array[String]: ...
@overload
def array(*elements: Number) -> Array[Number]: ...
@overload
def array(*elements: String) -> Array[String]: ...
@overload
def array(*elements: Any) -> Array: ...


@jit.auto_let
def array(*elements: Any) -> Array:
    return jit.array(*elements)


@overload
def record() -> Record: ...
@overload
def record(**fields: types.PyNumberCompat) -> Record[Number]: ...
@overload
def record(**fields: types.PyStringCompat) -> Record[String]: ...
@overload
def record(**fields: types.GraineObjectT) -> Record[types.GraineObjectT]: ...
@overload
def record(**fields: Any) -> Record: ...


@jit.auto_let
def record(**fields: Any) -> Record:
    return jit.record(**fields)


@overload
def from_python(value: types.PyBooleanCompat) -> Boolean: ...  # pyright: ignore[reportOverlappingOverload]
@overload
def from_python(value: types.PyNumberCompat) -> Number: ...
@overload
def from_python(value: types.PyStringCompat) -> String: ...
@overload
def from_python(value: list[types.GraineObjectT]) -> Array[types.GraineObjectT]: ...
@overload
def from_python(value: list[types.PyBooleanCompat]) -> Array[Boolean]: ...
@overload
def from_python(value: list[types.PyNumberCompat]) -> Array[Number]: ...
@overload
def from_python(value: list[types.PyStringCompat]) -> Array[String]: ...
@overload
def from_python(value: list[Any]) -> Array: ...
@overload
def from_python(value: dict[str, types.PyBooleanCompat]) -> Record[Boolean]: ...
@overload
def from_python(value: dict[str, types.GraineObjectT]) -> Record[types.GraineObjectT]: ...
@overload
def from_python(value: dict[str, types.PyNumberCompat]) -> Record[Number]: ...
@overload
def from_python(value: dict[str, types.PyStringCompat]) -> Record[String]: ...
@overload
def from_python(value: dict[str, Any]) -> Record: ...


@jit.auto_let
def from_python(value: types.PyGraineCompat) -> Class:
    return jit.from_python(value)


def func(fn: types.PyCallableT) -> types.PyCallableT:
    func_ast = jit._function_from_python(fn)
    jit.emit_statement(jit.require_block(), func_ast)
    return cast(types.PyCallableT, jit._GraineBuilder(ast.GraineIdentifierNode(name=func_ast.name)))


def cls(cls_: types.PyClassT) -> types.PyClassT:
    class_ast = jit._class_ast_from_python(cls_)
    jit.emit_statement(jit.require_block(), class_ast)
    return jit._class_facade_from_python(cls_, class_ast)
