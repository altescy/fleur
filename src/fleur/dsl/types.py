"""
Type system for Graine DSL.

This module defines the type-level representations used for static type checking
in Graine. It uses phantom types and protocols to provide compile-time type safety
without runtime overhead.

Key concepts:
- GrainePrimitiveType: Enum of primitive JavaScript types
- GraineObject: Protocol for typed Graine objects with magic methods
- PyXxxCompat: Type aliases for Python types compatible with Graine types
- Phantom types: Generic type parameters that exist only for type checking
"""

import enum
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, Literal, Protocol, Union, runtime_checkable

from typing_extensions import TypeAlias, TypeVar

if TYPE_CHECKING:
    from .ast import GraineASTExpr


@runtime_checkable
class HasGraineASTExpr(Protocol):
    """Protocol for objects that carry a Graine AST node."""

    __graine_ast__: "GraineASTExpr"


PyBooleanCompat: TypeAlias = bool
PyNumberCompat: TypeAlias = Union[int, float]
PyStringCompat: TypeAlias = str
PyArrayCompat: TypeAlias = list[Any]
PyRecordCompat: TypeAlias = dict[str, Any]
PyGraineCompat: TypeAlias = Union[PyBooleanCompat, PyNumberCompat, PyStringCompat, PyArrayCompat, PyRecordCompat]

PyClassT = TypeVar("PyClassT", bound=type)
PyCallableT = TypeVar("PyCallableT", bound=Callable[..., Any])


class GrainePrimitiveType(enum.Enum):
    """
    Enumeration of primitive Graine types.

    These correspond to JavaScript primitive types and object categories.
    Used for type checking and introspection.
    """

    UNDEFINED = "undefined"
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    ARRAY = "array"
    RECORD = "record"
    FUNCTION = "function"
    CLASS = "class"


GraineUndefinedType: TypeAlias = Literal[GrainePrimitiveType.UNDEFINED]
GraineBooleanType: TypeAlias = Literal[GrainePrimitiveType.BOOLEAN]
GraineNumberType: TypeAlias = Literal[GrainePrimitiveType.NUMBER]
GraineStringType: TypeAlias = Literal[GrainePrimitiveType.STRING]
GraineArrayType: TypeAlias = Literal[GrainePrimitiveType.ARRAY]
GraineRecordType: TypeAlias = Literal[GrainePrimitiveType.RECORD]
GraineFunctionType: TypeAlias = Literal[GrainePrimitiveType.FUNCTION]
GraineClassType: TypeAlias = Literal[GrainePrimitiveType.CLASS]
GraineBooleanLikeType: TypeAlias = Union[GraineUndefinedType, GraineBooleanType, GraineNumberType, GraineStringType]

GraineType: TypeAlias = Union[GrainePrimitiveType, "GraineObject[Any]"]

GraineTypeS = TypeVar("GraineTypeS", bound="GraineType")
GraineTypeT = TypeVar("GraineTypeT", bound="GraineType")
GraineTypeU = TypeVar("GraineTypeU", bound="GraineType")
GraineTypeS_co = TypeVar("GraineTypeS_co", bound="GraineType", covariant=True)
GraineTypeT_co = TypeVar("GraineTypeT_co", bound="GraineType", covariant=True)
GraineTypeU_co = TypeVar("GraineTypeU_co", bound="GraineType", covariant=True)

GraineASTExprT = TypeVar("GraineASTExprT", bound="GraineASTExpr")
GraineASTExprT_co = TypeVar("GraineASTExprT_co", bound="GraineASTExpr", covariant=True, default="GraineASTExpr")


class GraineObject(Generic[GraineASTExprT_co]):
    """
    Base protocol for all Graine typed objects.

    This is a phantom type that exists only for type checking. Concrete instances
    are actually _GraineBuilder objects, but this protocol provides the type-level
    interface with proper method signatures for operations.

    The generic parameter carries the AST expression type for type safety.
    """

    __graine_ast__: GraineASTExprT_co


GraineObjectS = TypeVar("GraineObjectS", bound=GraineObject)
GraineObjectT = TypeVar("GraineObjectT", bound=GraineObject)
GraineObjectT_co = TypeVar("GraineObjectT_co", bound=GraineObject, covariant=True)
GraineObjectT_contra = TypeVar("GraineObjectT_contra", bound=GraineObject, contravariant=True)


class GraineUndefined(GraineObject["GraineASTExpr[GraineUndefinedType]"]):
    """Phantom type for JavaScript undefined value."""

    ...


class GraineBoolean(GraineObject["GraineASTExpr[GraineBooleanType]"]):
    """Phantom type for JavaScript boolean values."""

    ...


class GraineNumber(GraineObject["GraineASTExpr[GraineNumberType]"]):
    """
    Phantom type for JavaScript number values.

    Supports arithmetic operations and comparisons with type safety.
    """

    def __eq__(self, other: Union[PyNumberCompat, "GraineNumber"]) -> GraineBoolean: ...  # pyright: ignore[reportIncompatibleMethodOverride]

    def __add__(self, other: "GraineNumber") -> "GraineNumber": ...


class GraineString(GraineObject["GraineASTExpr[GraineStringType]"]):
    """
    Phantom type for JavaScript string values.

    Supports string operations like concatenation, indexing, and methods.
    """

    def __eq__(self, other: Union[PyStringCompat, "GraineString"]) -> GraineBoolean: ...  # pyright: ignore[reportIncompatibleMethodOverride]

    def __add__(self, other: "GraineString") -> "GraineString": ...

    def __getitem__(self, index: Union[PyNumberCompat, GraineNumber]) -> "GraineString": ...

    def length(self) -> GraineNumber: ...

    def startswith(self, prefix: Union[PyStringCompat, "GraineString"]) -> GraineBoolean: ...


class GraineArray(GraineObject["GraineASTExpr[GraineArrayType]"], Generic[GraineObjectT_co]):
    """
    Phantom type for JavaScript array values.

    Generic over element type to provide type-safe array operations.
    Supports indexing, mutation, and array methods like push/pop.
    """

    def __getitem__(self, index: GraineNumber) -> GraineObjectT_co: ...

    def __setitem__(
        self: "GraineArray[GraineObjectT]",
        index: GraineNumber,
        value: GraineObjectT,
    ) -> None: ...

    def pop(self) -> GraineObjectT_co: ...

    def push(self: "GraineArray[GraineObjectT]", value: GraineObjectT) -> None: ...

    @property
    def length(self) -> GraineNumber: ...


class GraineRecord(GraineObject["GraineASTExpr[GraineRecordType]"], Generic[GraineObjectT_co]):
    """
    Phantom type for JavaScript object/record values.

    Generic over value type to provide type-safe property access.
    Supports both dot notation (via __getattr__) and bracket notation (via __getitem__).
    """

    def __getattr__(self, key: Union[PyStringCompat, GraineString]) -> GraineObjectT_co: ...

    def __getitem__(self, key: Union[PyStringCompat, GraineString]) -> GraineObjectT_co: ...

    def __setitem__(
        self: "GraineRecord[GraineObjectT]",
        key: GraineString,
        value: GraineObjectT,
    ) -> None: ...

    def items(self) -> GraineArray: ...


class GraineFunction(GraineObject["GraineASTExpr[GraineFunctionType]"]):
    """
    Phantom type for JavaScript function values.

    Supports function call operations.
    """

    def __call__(self, *args: GraineObject) -> GraineObject: ...


GraineBooleanLike: TypeAlias = Union[GraineUndefined, GraineBoolean, GraineNumber, GraineString]
