# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check the types of inputs and optional values in scoped DOM effects."""

from typing import assert_type

from fleur import Expr, Model, State, View
from fleur.core import DomAction, DomScope


class Settings(Model):
    opened: State[bool]
    duration: State[int | None]


def valid_examples(scope: DomScope, settings: Settings) -> None:
    opened = assert_type(scope.input(settings.opened), Expr[bool])
    duration = assert_type(scope.input(settings.duration), Expr[int | None])

    def schedule(milliseconds: Expr[int]) -> DomAction:
        assert_type(milliseconds, Expr[int])
        return scope.timer().start(milliseconds, DomAction.batch())

    DomAction.when(opened, DomAction.maybe(duration, schedule))


def invalid_examples(scope: DomScope, settings: Settings) -> None:
    duration = scope.input(settings.duration)

    def update_text(text: Expr[str]) -> DomAction:
        return DomAction.with_value(text, lambda _: DomAction.batch())

    DomAction.when(duration, DomAction.batch())  # pyright: ignore[reportArgumentType]
    DomAction.maybe(duration, update_text)  # pyright: ignore[reportArgumentType]
    duration.set(2000)  # pyright: ignore[reportAttributeAccessIssue]
    scope.input(View(tag="div", props={}))  # pyright: ignore[reportArgumentType]
