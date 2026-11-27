from __future__ import annotations

from abc import abstractmethod
from typing import Any, Generic

from typing_extensions import TypeVar

from fleur.js.ast import ESTreeExpression
from fleur.types import ICompilable

from .types import FleurValue

TaskValueT = TypeVar("TaskValueT", bound=FleurValue, default=Any)
TaskValueT_co = TypeVar("TaskValueT_co", bound=FleurValue, default=Any, covariant=True)
TaskErrorT = TypeVar("TaskErrorT", bound=FleurValue, default=Any)
TaskErrorT_co = TypeVar("TaskErrorT_co", bound=FleurValue, default=Any, covariant=True)


class TaskLike(Generic[TaskValueT_co, TaskErrorT_co], ICompilable[ESTreeExpression]):
    """Subclass with the success and error payload types and implement __compile__."""

    @abstractmethod
    def __compile__(self) -> ESTreeExpression: ...
