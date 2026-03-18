from __future__ import annotations

from typing import Any, Protocol

from typing_extensions import TypeVar

from fleur.js.ast import ESTreeExpression
from fleur.types import ICompilable

from .types import FleurValue

TaskValueT = TypeVar("TaskValueT", bound=FleurValue, default=Any)
TaskValueT_co = TypeVar("TaskValueT_co", bound=FleurValue, default=Any, covariant=True)
TaskErrorT = TypeVar("TaskErrorT", bound=FleurValue, default=Any)
TaskErrorT_co = TypeVar("TaskErrorT_co", bound=FleurValue, default=Any, covariant=True)


class TaskLike(ICompilable[ESTreeExpression], Protocol[TaskValueT_co, TaskErrorT_co]):
    """Marker protocol for task effects used by Cmd.task."""
