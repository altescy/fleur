# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check typed error response bodies."""

from collections.abc import Sequence
from typing import Any, assert_type

from fleur import Array, Cmd, Cond, Expr, Http, HttpError, HttpResponse, Model, ModelUpdate, Msg, MsgGroup, State
from fleur.types import JsonValue


class Todo(Model):
    title: State[str]


class Issue(Model):
    loc: State[list[str | int]]
    msg: State[str]


class ValidationError(Model):
    detail: State[list[Issue]]


class Reply(Model):
    messages: State[Sequence[str] | None]


class Actions(MsgGroup):
    CREATED: Msg[HttpResponse[Todo]] = Msg()
    REJECTED: Msg[HttpError[ValidationError]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def rejected(event: HttpError[ValidationError]) -> ModelUpdate[Reply]:
    assert_type(event.body, ValidationError | None)
    messages = Cond.maybe(event.body, then=lambda error: Array.map(error.detail, lambda issue: issue.msg))
    assert_type(messages, Expr[Sequence[str] | None])
    return State.set(Reply.messages, messages)


def failed(event: HttpError) -> ModelUpdate[Any]:
    assert_type(event.body, JsonValue | None)
    return State.unchanged()


def valid_examples() -> None:
    create = Http.post("/todos", body={"title": "x"}, expect=Http.expectJson(Todo, error=ValidationError))
    Cmd.task(create, Actions.CREATED, Actions.REJECTED)
    Cmd.task(Http.post("/todos", expect=Http.expectJson(Todo)), Actions.CREATED, Actions.FAILED)
    Actions.REJECTED.then(lambda event: rejected(event))
    Actions.FAILED.then(lambda event: failed(event))


def misread(event: HttpError[ValidationError]) -> ModelUpdate[Reply]:
    # The body has the declared type, so a misspelled field is an error.
    return State.set(Reply.messages, Cond.maybe(event.body, then=lambda error: error.details))  # pyright: ignore[reportAttributeAccessIssue]


def invalid_examples() -> None:
    create = Http.post("/todos", expect=Http.expectJson(Todo, error=ValidationError))
    # The error handler must take the declared error body.
    Cmd.task(create, Actions.CREATED, Actions.FAILED)  # pyright: ignore[reportArgumentType]
    Cmd.task(Http.post("/todos", expect=Http.expectJson(Todo)), Actions.CREATED, Actions.REJECTED)  # pyright: ignore[reportArgumentType]
    Actions.REJECTED.then(lambda event: misread(event))
    Actions.REJECTED.then(lambda event: failed(event))  # pyright: ignore[reportArgumentType]
