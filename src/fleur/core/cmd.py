from typing import TYPE_CHECKING, Any, Generic

from typing_extensions import Self

from fleur.js.ast import ESTreeExpression, ESTreeFunctionBody, ESTreeFunctionExpression, ESTreeReturnStatement

from .runtime import RUNTIME_CMD, RUNTIME_MAP, RUNTIME_NONE, RUNTIME_TASK, runtime_call
from .task import TaskErrorT, TaskLike, TaskValueT
from .types import ModelT, MsgGroupT

if TYPE_CHECKING:
    from .msg import GroupedMsg


class Cmd(Generic[ModelT, MsgGroupT]):
    def __init__(self, expr: ESTreeExpression | None = None) -> None:
        self._expr = expr or runtime_call((RUNTIME_CMD, RUNTIME_NONE))

    @classmethod
    def none(cls) -> Self:
        return cls()

    @classmethod
    def map(cls, tagger: "GroupedMsg[MsgGroupT, Any, Any]", cmd: "Cmd[ModelT, Any]") -> "Cmd[ModelT, MsgGroupT]":
        return cls(runtime_call((RUNTIME_CMD, RUNTIME_MAP), tagger.__compile__(), cmd.__compile__()))

    @classmethod
    def task(
        cls,
        effect: TaskLike[TaskValueT, TaskErrorT],
        ok: "GroupedMsg[MsgGroupT, TaskValueT, Any]",
        err: "GroupedMsg[MsgGroupT, TaskErrorT, Any]",
    ) -> "Cmd[ModelT, MsgGroupT]":
        effect_thunk = ESTreeFunctionExpression(
            id=None,
            params=[],
            body=ESTreeFunctionBody(body=[ESTreeReturnStatement(argument=effect.__compile__())]),
        )
        return cls(runtime_call((RUNTIME_CMD, RUNTIME_TASK), effect_thunk, ok.__compile__(), err.__compile__()))

    def __compile__(self) -> ESTreeExpression:
        return self._expr
