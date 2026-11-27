from typing import TYPE_CHECKING, Any, Generic

from typing_extensions import TypeVar

from fleur.js.ast import ESTreeExpression
from fleur.js.builder import literal

from .runtime import RUNTIME_INTERVAL, RUNTIME_MAP, RUNTIME_NONE, RUNTIME_SUB, runtime_call
from .types import ModelT, MsgGroupT

if TYPE_CHECKING:
    from .model import Model
    from .msg import GroupedMsg, MsgGroup

# Method-scoped variables: class-level ones are not solved from the arguments of a classmethod.
_ModelT = TypeVar("_ModelT", bound="Model")
_MsgGroupT = TypeVar("_MsgGroupT", bound="MsgGroup")
_ChildMsgGroupT = TypeVar("_ChildMsgGroupT", bound="MsgGroup")


class Sub(Generic[ModelT, MsgGroupT]):
    """A subscription that dispatches messages of one group."""

    def __init__(self, expr: ESTreeExpression | None = None) -> None:
        self._expr = expr or runtime_call((RUNTIME_SUB, RUNTIME_NONE))

    @staticmethod
    def none() -> "Sub[Any, Any]":
        """A subscription that dispatches nothing, compatible with every component."""
        return Sub()

    @staticmethod
    def map(
        tagger: "GroupedMsg[_MsgGroupT, _ChildMsgGroupT, None]", sub: "Sub[_ModelT, _ChildMsgGroupT]"
    ) -> "Sub[_ModelT, _MsgGroupT]":
        """Wrap each message of a child subscription in the parent's tagger message."""
        return Sub(runtime_call((RUNTIME_SUB, RUNTIME_MAP), tagger.__compile__(), sub.__compile__()))

    @staticmethod
    def interval(key: str, ms: int, tagger: "GroupedMsg[_MsgGroupT, Any, None]") -> "Sub[Any, _MsgGroupT]":
        return Sub(runtime_call((RUNTIME_SUB, RUNTIME_INTERVAL), literal(key), literal(ms), tagger.__compile__()))

    def __compile__(self) -> ESTreeExpression:
        return self._expr
