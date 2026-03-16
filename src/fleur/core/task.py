from __future__ import annotations

from typing import Protocol

from typing_extensions import TypeVar

from fleur.js.ast import ESTreeExpression
from fleur.types import ICompilable

TaskValueT = TypeVar("TaskValueT", default=object, covariant=True)
TaskErrorT = TypeVar("TaskErrorT", default=object, covariant=True)
TaskNextT = TypeVar("TaskNextT", default=object, covariant=True)
TaskRefT = TypeVar("TaskRefT", bound="TaskExpr[object]", default="TaskExpr[object]")


class TaskExpr(ICompilable[ESTreeExpression], Protocol[TaskValueT]):
    """Compilable expression that represents a task value in the DSL."""


class TaskLike(ICompilable[ESTreeExpression], Protocol[TaskValueT, TaskErrorT]):
    """Marker protocol for task effects used by Cmd.task."""
