# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check typed JSON responses and reading fields of model values."""

from collections.abc import Sequence
from typing import Any, assert_type

from fleur import (
    Array,
    Cmd,
    Cond,
    Expr,
    Http,
    HttpError,
    HttpResponse,
    Model,
    ModelUpdate,
    Msg,
    MsgGroup,
    State,
)
from fleur.types import JsonValue


class Todo(Model):
    id: State[int]
    title: State[str]


class Screen(Model):
    todos: State[list[Todo]]
    name: State[str]


class Actions(MsgGroup):
    LOADED: Msg[HttpResponse[Todo]] = Msg()
    LISTED: Msg[HttpResponse[list[Todo]]] = Msg()
    RAW: Msg[HttpResponse[JsonValue]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def loaded(event: HttpResponse[Todo]) -> ModelUpdate[Any]:
    assert_type(event.body.title, Expr[str])
    return State.unchanged()


def loaded_typo(event: HttpResponse[Todo]) -> ModelUpdate[Any]:
    _ = event.body.titel  # pyright: ignore[reportAttributeAccessIssue]
    return State.unchanged()


def valid_examples(screen: Screen) -> None:
    Cmd.task(Http.get("/todos/1", expect=Http.expectJson(Todo)), Actions.LOADED, Actions.FAILED)
    Cmd.task(Http.get("/todos", expect=Http.expectJson(list[Todo])), Actions.LISTED, Actions.FAILED)
    Cmd.task(Http.get("/raw", expect=Http.expectJson()), Actions.RAW, Actions.FAILED)
    Actions.LOADED.then(lambda event: loaded(event))
    assert_type(Array.map(screen.todos, lambda todo: todo.title), Expr[Sequence[str]])


def invalid_examples(screen: Screen) -> None:
    Cmd.task(Http.get("/todos", expect=Http.expectJson(Todo)), Actions.LISTED, Actions.FAILED)  # pyright: ignore[reportArgumentType]
    Cmd.task(Http.get("/todos/1", expect=Http.expectJson(list[Todo])), Actions.LOADED, Actions.FAILED)  # pyright: ignore[reportArgumentType]
    Array.map(screen.todos, lambda todo: todo.name)  # pyright: ignore[reportAttributeAccessIssue]


class Picker(Model):
    current: State[Todo | None]
    flag: State[bool]
    count: State[int | None]


def optional_models(screen: Screen, picker: Picker) -> None:
    """Model values from conditions and optional lookups read fields as attributes."""
    assert_type(Cond.when(picker.flag, screen.todos[0], screen.todos[1]), Todo)
    assert_type(Cond.when(picker.flag, screen.todos[0], screen.todos[1]).title, Expr[str])
    assert_type(Cond.maybe(picker.current, lambda todo: todo.title, otherwise="none"), Expr[str])
    assert_type(Cond.maybe(Array.get(screen.todos, 0), lambda todo: todo.id), Expr[int | None])
    Cond.maybe(picker.current, lambda todo: todo.titel)  # pyright: ignore[reportAttributeAccessIssue]
