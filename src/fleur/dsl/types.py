import enum
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, Literal, Union, overload

from typing_extensions import TypeAlias, TypeVar

if TYPE_CHECKING:
    from .ast import GraineArrayNode, GraineASTExpr, GraineBinaryOpNode, GraineRecordNode

PyBooleanCompat: TypeAlias = bool
PyNumberCompat: TypeAlias = Union[int, float]
PyStringCompat: TypeAlias = str
PyArrayCompat: TypeAlias = list[Any]
PyRecordCompat: TypeAlias = dict[str, Any]
PyGraineCompat: TypeAlias = Union[PyBooleanCompat, PyNumberCompat, PyStringCompat, PyArrayCompat, PyRecordCompat]

PyClassT = TypeVar("PyClassT", bound=type)
PyCallableT = TypeVar("PyCallableT", bound=Callable[..., Any])


class GraineType(enum.Enum):
    UNDEFINED = "undefined"
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    ARRAY = "array"
    RECORD = "record"
    FUNCTION = "function"
    CLASS = "class"


GraineUndefinedType: TypeAlias = Literal[GraineType.UNDEFINED]
GraineBooleanType: TypeAlias = Literal[GraineType.BOOLEAN]
GraineNumberType: TypeAlias = Literal[GraineType.NUMBER]
GraineStringType: TypeAlias = Literal[GraineType.STRING]
GraineArrayType: TypeAlias = Literal[GraineType.ARRAY]
GraineRecordType: TypeAlias = Literal[GraineType.RECORD]
GraineFunctionType: TypeAlias = Literal[GraineType.FUNCTION]
GraineClassType: TypeAlias = Literal[GraineType.CLASS]
GraineBooleanLikeType: TypeAlias = Union[GraineUndefinedType, GraineBooleanType, GraineNumberType, GraineStringType]

GraineTypeS = TypeVar("GraineTypeS", bound="GraineType")
GraineTypeT = TypeVar("GraineTypeT", bound="GraineType")
GraineTypeU = TypeVar("GraineTypeU", bound="GraineType")
GraineTypeS_co = TypeVar("GraineTypeS_co", bound="GraineType", covariant=True)
GraineTypeT_co = TypeVar("GraineTypeT_co", bound="GraineType", covariant=True)
GraineTypeU_co = TypeVar("GraineTypeU_co", bound="GraineType", covariant=True)

GraineASTExprT = TypeVar("GraineASTExprT", bound="GraineASTExpr")
GraineASTExprT_co = TypeVar("GraineASTExprT_co", bound="GraineASTExpr", covariant=True)


class GraineObject(Generic[GraineASTExprT_co]):
    __graine_ast__: GraineASTExprT_co

    def __getattr__(
        self: "GraineObject[GraineASTExpr[GraineRecordType]]",
        name: str,
    ) -> "GraineObject[GraineASTExpr]": ...

    def __eq__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Union[PyGraineCompat, "GraineObject[GraineASTExpr]"],
    ) -> "GraineObject[GraineBinaryOpNode[GraineBooleanType]]": ...

    @overload
    def __add__(
        self: "GraineObject[GraineASTExpr[GraineNumberType]]",
        other: Union[PyGraineCompat, "GraineObject[GraineASTExpr[GraineNumberType]]"],
    ) -> "GraineObject[GraineBinaryOpNode[GraineNumberType]]": ...
    @overload
    def __add__(
        self: "GraineObject[GraineASTExpr[GraineStringType]]",
        other: Union[PyGraineCompat, "GraineObject[GraineASTExpr[GraineStringType]]"],
    ) -> "GraineObject[GraineBinaryOpNode[GraineStringType]]": ...

    def __add__(
        self,
        other: Union[PyGraineCompat, "GraineObject[GraineASTExpr]"],
    ) -> "GraineObject[GraineBinaryOpNode]": ...

    @overload
    def __getitem__(
        self: "GraineObject[GraineASTExpr[GraineStringType]]",
        index: Union[PyNumberCompat, "GraineObject[GraineASTExpr[GraineNumberType]]"],
    ) -> "GraineObject[GraineASTExpr[GraineStringType]]": ...
    @overload
    def __getitem__(
        self: "GraineObject[GraineArrayNode[GraineTypeT]]",
        index: Union[PyNumberCompat, "GraineObject[GraineASTExpr[GraineNumberType]]"],
    ) -> "GraineObject[GraineASTExpr[GraineTypeT]]": ...
    @overload
    def __getitem__(
        self: "GraineObject[GraineASTExpr[GraineArrayType]]",
        index: Union[PyNumberCompat, "GraineObject[GraineASTExpr[GraineNumberType]]"],
    ) -> "GraineObject[GraineASTExpr[GraineType]]": ...
    @overload
    def __getitem__(
        self: "GraineObject[GraineRecordNode[GraineTypeT]]",
        index: Union[PyStringCompat, "GraineObject[GraineASTExpr[GraineStringType]]"],
    ) -> "GraineObject[GraineASTExpr[GraineTypeT]]": ...
    @overload
    def __getitem__(
        self: "GraineObject[GraineASTExpr[GraineRecordType]]",
        index: Union[PyStringCompat, "GraineObject[GraineASTExpr[GraineStringType]]"],
    ) -> "GraineObject[GraineASTExpr[GraineType]]": ...

    def __getitem__(
        self: "GraineObject[GraineASTExpr[Union[GraineArrayType, GraineRecordType, GraineStringType]]]",
        index: Union[
            PyNumberCompat,
            PyStringCompat,
            "GraineObject[GraineASTExpr[Union[GraineNumberType, GraineStringType]]]",
        ],
    ) -> "GraineObject[GraineASTExpr]": ...

    @property
    def length(
        self: "GraineObject[GraineASTExpr[Union[GraineStringType, GraineArrayType]]]",
    ) -> "GraineObject[GraineASTExpr[GraineNumberType]]": ...

    def push(
        self: "GraineObject[GraineArrayNode[GraineTypeT]]",
        value: "GraineObject[GraineASTExpr[GraineTypeT]]",
    ) -> None: ...


GraineBoolean: TypeAlias = GraineObject["GraineASTExpr[GraineBooleanType]"]
GraineNumber: TypeAlias = GraineObject["GraineASTExpr[GraineNumberType]"]
GraineString: TypeAlias = GraineObject["GraineASTExpr[GraineStringType]"]
GraineArray: TypeAlias = GraineObject["GraineASTExpr[GraineArrayType]"]
GraineRecord: TypeAlias = GraineObject["GraineASTExpr[GraineRecordType]"]

GraineObjectT = TypeVar("GraineObjectT", bound=GraineObject)
