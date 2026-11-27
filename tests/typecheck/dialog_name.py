# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check that a dialog cannot be created without an accessible name."""

from fleur import Msg, MsgGroup
from fleur.core import DialogCloseEvent
from fleur.ui import Dialog, Heading


class Actions(MsgGroup):
    CLOSED: Msg[DialogCloseEvent] = Msg()


def valid_examples() -> None:
    Dialog(
        Heading("Settings", level=2, props={"id": "settings-title"}),
        labelledby="settings-title",
        open=True,
        onclose=Actions.CLOSED,
    )
    Dialog(open=True, onclose=Actions.CLOSED, label="Settings")


def invalid_examples() -> None:
    Dialog(open=True, onclose=Actions.CLOSED)  # pyright: ignore[reportCallIssue]
    Dialog(open=True, onclose=Actions.CLOSED, label="A", labelledby="b")  # pyright: ignore[reportCallIssue]
