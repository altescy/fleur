from typing import Generic

from typing_extensions import Self

from fleur.js.ast import ESTreeExpression

from .runtime import RUNTIME_CMD, RUNTIME_NONE, runtime_call
from .types import ModelT, MsgGroupT


class Cmd(Generic[ModelT, MsgGroupT]):
    def __init__(self, kind: str = "none") -> None:
        self._kind = kind

    @classmethod
    def none(cls) -> Self:
        return cls("none")

    def __compile__(self) -> ESTreeExpression:
        if self._kind != "none":
            raise ValueError(f"Unsupported command kind: {self._kind}")
        return runtime_call((RUNTIME_CMD, RUNTIME_NONE))
