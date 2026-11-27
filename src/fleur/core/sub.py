from collections import Counter
from typing import TYPE_CHECKING, Any, Generic

from typing_extensions import TypeVar

from fleur.js.ast import ESTreeArrayExpression, ESTreeExpression
from fleur.js.builder import literal

from .runtime import RUNTIME_BATCH, RUNTIME_INTERVAL, RUNTIME_MAP, RUNTIME_NONE, RUNTIME_SUB, runtime_call
from .types import ModelT, MsgGroupT

if TYPE_CHECKING:
    from .model import Model
    from .msg import GroupedMsg, MsgGroup

# Method-scoped variables: class-level ones are not solved from the arguments of a classmethod.
_ModelT = TypeVar("_ModelT", bound="Model")
_MsgGroupT = TypeVar("_MsgGroupT", bound="MsgGroup")
_ChildMsgGroupT = TypeVar("_ChildMsgGroupT", bound="MsgGroup")


class Sub(Generic[ModelT, MsgGroupT]):
    """A subscription that dispatches messages of one group.

    The runtime identifies each active subscription by its key, so a subscription records the
    keys it starts and `Sub.batch` rejects duplicates that would otherwise replace each other.
    """

    def __init__(self, expr: ESTreeExpression | None = None, keys: tuple[str, ...] = ()) -> None:
        self._expr = expr or runtime_call((RUNTIME_SUB, RUNTIME_NONE))
        self._keys = keys

    @property
    def keys(self) -> tuple[str, ...]:
        """The keys of the subscriptions this starts."""
        return self._keys

    @staticmethod
    def none() -> "Sub[Any, Any]":
        """A subscription that dispatches nothing, compatible with every component."""
        return Sub()

    @staticmethod
    def batch(*subs: "Sub[_ModelT, _MsgGroupT]") -> "Sub[_ModelT, _MsgGroupT]":
        """Run several subscriptions of the same message group together, like Elm's `Sub.batch`."""
        keys = tuple(key for sub in subs for key in sub.keys)
        duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
        if duplicates:
            raise ValueError(f"Sub.batch() received subscriptions with the same key: {', '.join(duplicates)}")
        compiled = ESTreeArrayExpression([sub.__compile__() for sub in subs])
        return Sub(runtime_call((RUNTIME_SUB, RUNTIME_BATCH), compiled), keys)

    @staticmethod
    def map(
        tagger: "GroupedMsg[_MsgGroupT, _ChildMsgGroupT, None]", sub: "Sub[_ModelT, _ChildMsgGroupT]"
    ) -> "Sub[_ModelT, _MsgGroupT]":
        """Wrap each message of a child subscription in the parent's tagger message."""
        return Sub(runtime_call((RUNTIME_SUB, RUNTIME_MAP), tagger.__compile__(), sub.__compile__()), sub.keys)

    @staticmethod
    def interval(key: str, ms: int, tagger: "GroupedMsg[_MsgGroupT, Any, None]") -> "Sub[Any, _MsgGroupT]":
        call = runtime_call((RUNTIME_SUB, RUNTIME_INTERVAL), literal(key), literal(ms), tagger.__compile__())
        return Sub(call, (key,))

    def __compile__(self) -> ESTreeExpression:
        return self._expr
