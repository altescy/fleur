from typing import TypeAlias

from fleur.core.component import Component
from fleur.core.cond import Cond
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr
from fleur.core.model import Model, State
from fleur.core.msg import Msg, MsgGroup
from fleur.core.view import View
from fleur.types import JsonValue

from ..views import Box, Button, HStack, Text, VStack


class DialogModel(Model):
    open: State[bool]


class DialogMsg(MsgGroup):
    OPEN: Msg[PointerEvent] = Msg()
    CLOSE: Msg[PointerEvent] = Msg()
    TOGGLE: Msg[PointerEvent] = Msg()


DialogChild: TypeAlias = str | View[DialogModel, DialogMsg] | Expr[JsonValue | View[DialogModel, DialogMsg]]


def dialog(
    *,
    title: str | Expr[str] = "Dialog",
    message: str | Expr[str] = "This is a reusable dialog component.",
    trigger: DialogChild = "Open dialog",
    close_label: DialogChild = "Close",
    toggle_label: DialogChild = "Toggle",
    closed_hint: str | Expr[str] = "Dialog is closed",
) -> Component[DialogModel, DialogMsg]:
    status_label = Cond.when(DialogModel.open, "Open", "Closed")
    status_fg = Cond.when(
        DialogModel.open,
        "var(--fleur-color-accent-soft-fg)",
        "var(--fleur-color-fg-muted)",
    )
    status_bg = Cond.when(
        DialogModel.open,
        "var(--fleur-color-accent-soft-bg)",
        "var(--fleur-color-bg-subtle)",
    )

    return Component(
        DialogModel(open=False),
        DialogMsg.caseof(
            DialogMsg.OPEN.then(State.set(DialogModel.open, True)),
            DialogMsg.CLOSE.then(State.set(DialogModel.open, False)),
            DialogMsg.TOGGLE.then(State.set(DialogModel.open, Cond.when(DialogModel.open, False, True))),
        ),
        VStack(
            HStack(
                Text(title, font_weight=700),
                Box(
                    Text(status_label, fg=status_fg, font_size="sm"),
                    bg=status_bg,
                    px="sm",
                    py="xs",
                    radius="sm",
                ),
                justify="space-between",
                align="center",
            ),
            Button(trigger, onclick=DialogMsg.TOGGLE),
            Cond.when(
                DialogModel.open,
                Box(
                    Text(title, font_weight=700),
                    Text(message),
                    HStack(
                        Button(close_label, onclick=DialogMsg.CLOSE),
                        Button(toggle_label, onclick=DialogMsg.TOGGLE, bg="accent-soft-bg", fg="accent-soft-fg"),
                        gap="sm",
                    ),
                    gap="sm",
                    p="md",
                    radius="md",
                    bg="bg-surface",
                    border="var(--fleur-comp-panel-border)",
                ),
                Text(closed_hint, fg="fg-muted"),
            ),
            gap="sm",
            p="md",
            bg="bg-canvas",
            border="var(--fleur-comp-panel-border)",
            radius="md",
        ),
    )
