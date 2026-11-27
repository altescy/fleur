from typing import TYPE_CHECKING, Any, Generic

from typing_extensions import TypeVar

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeExpression,
    ESTreeFunctionBody,
    ESTreeFunctionExpression,
    ESTreeReturnStatement,
)

from .runtime import RUNTIME_BATCH, RUNTIME_CMD, RUNTIME_MAP, RUNTIME_NONE, RUNTIME_TASK, runtime_call
from .task import TaskLike
from .types import FleurValue, ModelT, MsgGroupT

if TYPE_CHECKING:
    from .msg import GroupedMsg, MsgGroup

# Method-scoped variable: class-level ones are not solved from the arguments of a classmethod.
_MsgGroupT = TypeVar("_MsgGroupT", bound="MsgGroup")
_ChildMsgGroupT = TypeVar("_ChildMsgGroupT", bound="MsgGroup")
# Without defaults, so that they may precede `_MsgGroupT` in `task`.
_ValueT = TypeVar("_ValueT", bound=FleurValue)
_ErrorT = TypeVar("_ErrorT", bound=FleurValue)


class Cmd(Generic[ModelT, MsgGroupT]):
    """A command whose results are dispatched as messages of one group.

    Commands do not depend on the model, so the constructors below return `Any` for it and the
    command fits whichever component runs it.
    """

    def __init__(self, expr: ESTreeExpression | None = None) -> None:
        self._expr = expr or runtime_call((RUNTIME_CMD, RUNTIME_NONE))

    @staticmethod
    def none() -> "Cmd[Any, Any]":
        """A command that dispatches nothing, compatible with every component."""
        return Cmd()

    @staticmethod
    def batch(*cmds: "Cmd[Any, _MsgGroupT]") -> "Cmd[Any, _MsgGroupT]":
        """Run several commands of the same message group together, like Elm's `Cmd.batch`."""
        return Cmd(
            runtime_call((RUNTIME_CMD, RUNTIME_BATCH), ESTreeArrayExpression([cmd.__compile__() for cmd in cmds]))
        )

    @staticmethod
    def map(
        tagger: "GroupedMsg[_MsgGroupT, _ChildMsgGroupT, None]", cmd: "Cmd[Any, _ChildMsgGroupT]"
    ) -> "Cmd[Any, _MsgGroupT]":
        """Wrap each message of a child command in the parent's tagger message."""
        return Cmd(runtime_call((RUNTIME_CMD, RUNTIME_MAP), tagger.__compile__(), cmd.__compile__()))

    @staticmethod
    def task(
        effect: TaskLike[_ValueT, _ErrorT],
        ok: "GroupedMsg[_MsgGroupT, _ValueT, None]",
        err: "GroupedMsg[_MsgGroupT, _ErrorT, None]",
    ) -> "Cmd[Any, _MsgGroupT]":
        """Run a task and dispatch its result or error to a message that accepts that payload."""
        effect_thunk = ESTreeFunctionExpression(
            id=None,
            params=[],
            body=ESTreeFunctionBody(body=[ESTreeReturnStatement(argument=effect.__compile__())]),
        )
        return Cmd(runtime_call((RUNTIME_CMD, RUNTIME_TASK), effect_thunk, ok.__compile__(), err.__compile__()))

    def __compile__(self) -> ESTreeExpression:
        return self._expr
