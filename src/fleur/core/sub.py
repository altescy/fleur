from typing import Generic

from typing_extensions import Self

from fleur.js.ast import ESTreeExpression

from .runtime import RUNTIME_NONE, RUNTIME_SUB, runtime_call
from .types import ModelT


class Sub(Generic[ModelT]):
    def __init__(self, kind: str = "none") -> None:
        self._kind = kind

    @classmethod
    def none(cls) -> Self:
        return cls("none")

    def __compile__(self) -> ESTreeExpression:
        if self._kind != "none":
            raise ValueError(f"Unsupported subscription kind: {self._kind}")
        return runtime_call((RUNTIME_SUB, RUNTIME_NONE))
