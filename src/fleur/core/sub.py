from typing import TYPE_CHECKING, Any, Generic

from typing_extensions import Self

from fleur.js.ast import ESTreeExpression
from fleur.js.builder import literal

from .runtime import RUNTIME_INTERVAL, RUNTIME_MAP, RUNTIME_NONE, RUNTIME_SUB, runtime_call
from .types import ModelT

if TYPE_CHECKING:
    from .msg import GroupedMsg


class Sub(Generic[ModelT]):
    def __init__(self, expr: ESTreeExpression | None = None) -> None:
        self._expr = expr or runtime_call((RUNTIME_SUB, RUNTIME_NONE))

    @classmethod
    def none(cls) -> Self:
        return cls()

    @classmethod
    def map(cls, tagger: "GroupedMsg[Any, Any, Any]", sub: "Sub[ModelT]") -> "Sub[ModelT]":
        return cls(runtime_call((RUNTIME_SUB, RUNTIME_MAP), tagger.__compile__(), sub.__compile__()))

    @classmethod
    def interval(cls, key: str, ms: int, tagger: "GroupedMsg[Any, Any, Any]") -> "Sub[ModelT]":
        return cls(runtime_call((RUNTIME_SUB, RUNTIME_INTERVAL), literal(key), literal(ms), tagger.__compile__()))

    def __compile__(self) -> ESTreeExpression:
        return self._expr
