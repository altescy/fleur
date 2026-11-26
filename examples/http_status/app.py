"""Fetch a same-origin text resource and display its result."""

from fleur import Cmd, Component, Cond, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State
from fleur.core import PointerEvent
from fleur.ui import Button, Text, VStack


class StatusModel(Model):
    pending: State[bool]
    text: State[str]


class StatusMsg(MsgGroup):
    REFRESH: Msg[PointerEvent] = Msg()
    RECEIVED: Msg[HttpResponse[str]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def app() -> Component[StatusModel, StatusMsg]:
    return Component(
        StatusModel(pending=False, text="Refresh to check the service."),
        StatusMsg.cases(
            StatusMsg.REFRESH.then(
                (
                    State.set(StatusModel.pending, True) & State.set(StatusModel.text, "Loading…"),
                    Cmd.task(
                        Http.get("status.txt", expect=Http.expectText(), timeout_ms=4000),
                        ok=StatusMsg.RECEIVED,
                        err=StatusMsg.FAILED,
                    ),
                )
            ),
            StatusMsg.RECEIVED.then(
                State.set(StatusModel.pending, False)
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
                State.set(StatusModel.pending, False) & State.set(StatusModel.text, StatusMsg.FAILED.event.message)
            ),
        ),
        VStack(
            Button("Refresh", onclick=StatusMsg.REFRESH, props={"disabled": StatusModel.pending}),
            Text(StatusModel.text, props={"role": "status"}),
            gap="sm",
        ),
    )
