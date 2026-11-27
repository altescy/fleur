# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check typed JSON responses and reading fields of model values."""

from collections.abc import Sequence
from typing import assert_type

from fleur import Array, Cmd, Cond, Expr, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State
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


def valid_examples() -> None:
    Cmd.task(Http.get("/todos/1", expect=Http.expectJson(Todo)), Actions.LOADED, Actions.FAILED)
    Cmd.task(Http.get("/todos", expect=Http.expectJson(list[Todo])), Actions.LISTED, Actions.FAILED)
    Cmd.task(Http.get("/raw", expect=Http.expectJson()), Actions.RAW, Actions.FAILED)
    assert_type(Actions.LOADED.event.body.title, Expr[str])
    assert_type(Array.map(Screen.todos, lambda todo: todo.title), Expr[Sequence[str]])


def invalid_examples() -> None:
    Cmd.task(Http.get("/todos", expect=Http.expectJson(Todo)), Actions.LISTED, Actions.FAILED)  # pyright: ignore[reportArgumentType]
    Cmd.task(Http.get("/todos/1", expect=Http.expectJson(list[Todo])), Actions.LOADED, Actions.FAILED)  # pyright: ignore[reportArgumentType]
    Array.map(Screen.todos, lambda todo: todo.name)  # pyright: ignore[reportAttributeAccessIssue]


class Picker(Model):
    current: State[Todo | None]
    flag: State[bool]
    count: State[int | None]


def optional_models() -> None:
    """Model values from conditions and optional lookups read fields as attributes."""
    assert_type(Cond.when(Picker.flag, Screen.todos[0], Screen.todos[1]), Todo)
    assert_type(Cond.when(Picker.flag, Screen.todos[0], Screen.todos[1]).title, Expr[str])
    assert_type(Cond.maybe(Picker.current, lambda todo: todo.title, otherwise="none"), Expr[str])
    assert_type(Cond.maybe(Array.get(Screen.todos, 0), lambda todo: todo.id), Expr[int | None])
    assert_type(Cond.maybe(Picker.count, lambda count: count + 1, otherwise=0), Expr[int])
    Cond.maybe(Picker.current, lambda todo: todo.titel)  # pyright: ignore[reportAttributeAccessIssue]
