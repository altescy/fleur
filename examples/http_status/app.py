"""Fetch a same-origin text resource and display its result."""

from fleur import Cmd, Component, Cond, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State
from fleur.core import PointerEvent
from fleur.ui import Button, Notice, NoticeVariant, Progress, VStack


class StatusModel(Model):
    pending: State[bool]
    text: State[str]
    variant: State[NoticeVariant]


class StatusMsg(MsgGroup):
    REFRESH: Msg[PointerEvent] = Msg()
    RECEIVED: Msg[HttpResponse[str]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def app() -> Component[StatusModel, StatusMsg]:
    return Component(
        StatusModel(pending=False, text="Refresh to check the service.", variant="info"),
        StatusMsg.cases(
            StatusMsg.REFRESH.then(
                (
                    State.set(StatusModel.pending, True),
                    Cmd.task(
                        Http.get("status.txt", expect=Http.expectText(), timeout_ms=4000),
                        ok=StatusMsg.RECEIVED,
                        err=StatusMsg.FAILED,
                    ),
                )
            ),
            StatusMsg.RECEIVED.then(
                State.set(StatusModel.pending, False)
                & State.set(StatusModel.variant, Cond.when(StatusMsg.RECEIVED.event.ok, "success", "error"))
                & State.set(
                    StatusModel.text,
                    Cond.when(
                        StatusMsg.RECEIVED.event.ok,
                        StatusMsg.RECEIVED.event.body,
                        "Could not load the service status.",
                    ),
                )
            ),
            StatusMsg.FAILED.then(
                State.set(StatusModel.pending, False)
                & State.set(StatusModel.text, StatusMsg.FAILED.event.message)
                & State.set(StatusModel.variant, "error")
            ),
        ),
        VStack(
            Cond.when(
                StatusModel.pending,
                Progress(label="Checking service status"),
                Notice(StatusModel.text, variant=StatusModel.variant),
            ),
            Button(
                Cond.when(
                    StatusModel.pending,
                    "Checking…",
                    Cond.when(Cond.equal(StatusModel.variant, "error"), "Retry", "Refresh"),
                ),
                onclick=StatusMsg.REFRESH,
                props={"disabled": StatusModel.pending},
                align_self="flex-start",
            ),
            gap="sm",
        ),
    )
