import enum
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, Literal, Protocol, Union, runtime_checkable

from typing_extensions import TypeAlias, TypeVar

if TYPE_CHECKING:
    from .ast import GraineASTExpr


@runtime_checkable
class HasGraineASTExpr(Protocol):
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

GraineType: TypeAlias = Union[GrainePrimitiveType, "GraineObject"]

GraineTypeS = TypeVar("GraineTypeS", bound="GraineType")
GraineTypeT = TypeVar("GraineTypeT", bound="GraineType")
GraineTypeU = TypeVar("GraineTypeU", bound="GraineType")
GraineTypeS_co = TypeVar("GraineTypeS_co", bound="GraineType", covariant=True)
GraineTypeT_co = TypeVar("GraineTypeT_co", bound="GraineType", covariant=True)
GraineTypeU_co = TypeVar("GraineTypeU_co", bound="GraineType", covariant=True)

GraineASTExprT = TypeVar("GraineASTExprT", bound="GraineASTExpr")
GraineASTExprT_co = TypeVar("GraineASTExprT_co", bound="GraineASTExpr", covariant=True, default="GraineASTExpr")


class GraineObject(Generic[GraineASTExprT_co]):
    __graine_ast__: GraineASTExprT_co


GraineObjectS = TypeVar("GraineObjectS", bound=GraineObject)
GraineObjectT = TypeVar("GraineObjectT", bound=GraineObject)
GraineObjectT_co = TypeVar("GraineObjectT_co", bound=GraineObject, covariant=True)
GraineObjectT_contra = TypeVar("GraineObjectT_contra", bound=GraineObject, contravariant=True)


class GraineUndefined(GraineObject): ...


class GraineBoolean(GraineObject["GraineASTExpr[GraineBooleanType]"]): ...


class GraineNumber(GraineObject["GraineASTExpr[GraineNumberType]"]):
    def __eq__(self, other: Union[PyNumberCompat, "GraineNumber"]) -> GraineBoolean: ...  # pyright: ignore[reportIncompatibleMethodOverride]

    def __add__(self, other: "GraineNumber") -> "GraineNumber": ...


class GraineString(GraineObject["GraineASTExpr[GraineStringType]"]):
    def __eq__(self, other: Union[PyStringCompat, "GraineString"]) -> GraineBoolean: ...  # pyright: ignore[reportIncompatibleMethodOverride]

    def __add__(self, other: "GraineString") -> "GraineString": ...

    def __getitem__(self, index: Union[PyNumberCompat, GraineNumber]) -> "GraineString": ...

    def length(self) -> GraineNumber: ...


class GraineArray(GraineObject["GraineASTExpr[GraineArrayType]"], Generic[GraineObjectT_co]):
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
    def __getattr__(self, key: Union[PyStringCompat, GraineString]) -> GraineObjectT_co: ...

    def __getitem__(self, key: Union[PyStringCompat, GraineString]) -> GraineObjectT_co: ...

    def __setitem__(
        self: "GraineRecord[GraineObjectT]",
        key: GraineString,
        value: GraineObjectT,
    ) -> None: ...

    def items(self) -> GraineArray: ...


class GraineFunction(GraineObject["GraineASTExpr[GraineFunctionType]"]):
    def __call__(self, *args: GraineObject) -> GraineObject: ...


GraineBooleanLike: TypeAlias = Union[GraineUndefined, GraineBoolean, GraineNumber, GraineString]
