from __future__ import annotations

from abc import abstractmethod
from typing import Generic

from typing_extensions import TypeVar

from fleur.js.ast import ESTreeExpression
from fleur.types import ICompilable

from .types import FleurValue

TaskValueT = TypeVar("TaskValueT", bound=FleurValue)
TaskValueT_co = TypeVar("TaskValueT_co", bound=FleurValue, covariant=True)
TaskErrorT = TypeVar("TaskErrorT", bound=FleurValue)
TaskErrorT_co = TypeVar("TaskErrorT_co", bound=FleurValue, covariant=True)


class TaskLike(Generic[TaskValueT_co, TaskErrorT_co], ICompilable[ESTreeExpression]):
    """Subclass with the success and error payload types and implement __compile__.

    This is nominal rather than a Protocol on purpose: the payload types appear in no member,
    so any object with `__compile__` would structurally match `TaskLike[T, E]` for every `T`
    and `E`, and `Cmd.task` could no longer check its messages against the task.
    """

    @abstractmethod
    def __compile__(self) -> ESTreeExpression: ...
