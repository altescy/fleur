# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check the result and error payloads accepted by Cmd.task."""

from typing import Literal

from fleur import Cmd, Http, HttpError, HttpResponse, Msg, MsgGroup
from fleur.core import Dom, DomFocusError
from fleur.types import JsonValue


class Actions(MsgGroup):
    FOCUSED: Msg[None] = Msg()
    FOCUS_FAILED: Msg[DomFocusError] = Msg()
    FOCUS_ERROR_TEXT: Msg[str] = Msg()
    NOT_FOUND: Msg[Literal["not_found"]] = Msg()
    COUNT: Msg[int] = Msg()
    TEXT_RECEIVED: Msg[HttpResponse[str]] = Msg()
    JSON_RECEIVED: Msg[HttpResponse[JsonValue]] = Msg()
    REQUEST_FAILED: Msg[HttpError] = Msg()


def valid_examples() -> None:
    Cmd.task(Dom.focus("editor"), Actions.FOCUSED, Actions.FOCUS_FAILED)
    Cmd.task(Dom.focus("editor"), Actions.FOCUSED, Actions.FOCUS_ERROR_TEXT)
    Cmd.task(Http.get("/status.txt", expect=Http.expectText()), Actions.TEXT_RECEIVED, Actions.REQUEST_FAILED)
    Cmd.task(Http.get("/status.json", expect=Http.expectJson()), Actions.JSON_RECEIVED, Actions.REQUEST_FAILED)


def invalid_examples() -> None:
    Cmd.task(Dom.focus("editor"), Actions.COUNT, Actions.FOCUS_FAILED)  # pyright: ignore[reportArgumentType]
    Cmd.task(Dom.focus("editor"), Actions.FOCUSED, Actions.REQUEST_FAILED)  # pyright: ignore[reportArgumentType]
    Cmd.task(Dom.focus("editor"), Actions.FOCUSED, Actions.NOT_FOUND)  # pyright: ignore[reportArgumentType]
    text_request = Http.get("/status.txt", expect=Http.expectText())
    Cmd.task(text_request, Actions.FOCUSED, Actions.REQUEST_FAILED)  # pyright: ignore[reportArgumentType]
    Cmd.task(text_request, Actions.JSON_RECEIVED, Actions.REQUEST_FAILED)  # pyright: ignore[reportArgumentType]
    Cmd.task(text_request, Actions.TEXT_RECEIVED, Actions.FOCUS_FAILED)  # pyright: ignore[reportArgumentType]
