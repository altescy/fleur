from typing import TYPE_CHECKING, Protocol

from typing_extensions import TypeVar

if TYPE_CHECKING:
    from fleur.js.ast import ESTreeNode

JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

ESTreeNodeT = TypeVar("ESTreeNodeT", bound="ESTreeNode", default="ESTreeNode")
ESTreeNodeT_co = TypeVar("ESTreeNodeT_co", covariant=True, bound="ESTreeNode", default="ESTreeNode")


class ICompilable(Protocol[ESTreeNodeT_co]):
    def __compile__(self) -> ESTreeNodeT_co: ...
