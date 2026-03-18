from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from typing_extensions import TypeVar

if TYPE_CHECKING:
    from fleur.js.ast import ESTreeExpression, ESTreeNode

JsonValue = str | int | float | bool | None | Sequence["JsonValue"] | Mapping[str, "JsonValue"]
JsonValueT = TypeVar("JsonValueT", bound=JsonValue, default=JsonValue)
JsonValueT_co = TypeVar("JsonValueT_co", bound=JsonValue, default=JsonValue, covariant=True)
JsonValueU = TypeVar("JsonValueU", bound=JsonValue, default=JsonValue)

ESTreeNodeT = TypeVar("ESTreeNodeT", bound="ESTreeNode", default="ESTreeNode")
ESTreeNodeT_co = TypeVar("ESTreeNodeT_co", covariant=True, bound="ESTreeNode", default="ESTreeNode")
ESTreeExpressionT = TypeVar("ESTreeExpressionT", bound="ESTreeExpression", default="ESTreeExpression")
ESTreeExpressionT_co = TypeVar(
    "ESTreeExpressionT_co", covariant=True, bound="ESTreeExpression", default="ESTreeExpression"
)


@runtime_checkable
class ICompilable(Protocol[ESTreeNodeT_co]):
    def __compile__(self) -> ESTreeNodeT_co: ...
