# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check typed error response bodies."""

from collections.abc import Sequence
from typing import assert_type

from fleur import Array, Cmd, Cond, Expr, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State
from fleur.types import JsonValue


class Todo(Model):
    title: State[str]


class Issue(Model):
    loc: State[list[str | int]]
    msg: State[str]


class ValidationError(Model):
    detail: State[list[Issue]]


class Actions(MsgGroup):
    CREATED: Msg[HttpResponse[Todo]] = Msg()
    REJECTED: Msg[HttpError[ValidationError]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def valid_examples() -> None:
    create = Http.post("/todos", body={"title": "x"}, expect=Http.expectJson(Todo, error=ValidationError))
    Cmd.task(create, Actions.CREATED, Actions.REJECTED)
    Cmd.task(Http.post("/todos", expect=Http.expectJson(Todo)), Actions.CREATED, Actions.FAILED)
    assert_type(Actions.REJECTED.event.body, ValidationError | None)
    assert_type(Actions.FAILED.event.body, JsonValue | None)
    messages = Cond.maybe(Actions.REJECTED.event.body, then=lambda error: Array.map(error.detail, lambda i: i.msg))
    assert_type(messages, Expr[Sequence[str] | None])


def invalid_examples() -> None:
    create = Http.post("/todos", expect=Http.expectJson(Todo, error=ValidationError))
    # The error handler must take the declared error body.
    Cmd.task(create, Actions.CREATED, Actions.FAILED)  # pyright: ignore[reportArgumentType]
    Cmd.task(Http.post("/todos", expect=Http.expectJson(Todo)), Actions.CREATED, Actions.REJECTED)  # pyright: ignore[reportArgumentType]
    Cond.maybe(Actions.REJECTED.event.body, then=lambda error: error.details)  # pyright: ignore[reportAttributeAccessIssue]
