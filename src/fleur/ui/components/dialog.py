from fleur.core.component import Component
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr
from fleur.core.model import Model, State
from fleur.core.msg import Msg, MsgGroup

from ..views import Box, Button, HStack, Text, VStack


class DialogModel(Model):
    open: State[bool]


class DialogMsg(MsgGroup):
    OPEN: Msg[PointerEvent] = Msg()
    CLOSE: Msg[PointerEvent] = Msg()
    TOGGLE: Msg[PointerEvent] = Msg()


def dialog(
    *,
    title: str = "Dialog",
    message: str = "This is a reusable dialog component.",
    trigger: str = "Open dialog",
) -> Component[DialogModel, DialogMsg]:
    return Component(
        DialogModel(open=False),
        DialogMsg.caseof(
            DialogMsg.OPEN.then(DialogModel.open.set(True)),
            DialogMsg.CLOSE.then(DialogModel.open.set(False)),
            DialogMsg.TOGGLE.then(DialogModel.open.set(Expr.when(DialogModel.open, False, True))),
        ),
        VStack(
            Text("Dialog", font_weight=700),
            Button(trigger, onclick=DialogMsg.OPEN),
            Expr.when(
                DialogModel.open,
                Box(
                    Text(title, font_weight=700),
                    Text(message),
                    HStack(
                        Button("Close", onclick=DialogMsg.CLOSE),
                        Button("Toggle", onclick=DialogMsg.TOGGLE, bg="accent-soft-bg", fg="accent-soft-fg"),
                        gap="sm",
                    ),
                    gap="sm",
                    p="md",
                    radius="md",
                    bg="bg-surface",
                    border="var(--fleur-comp-panel-border)",
                ),
                Text("Dialog is closed", fg="fg-muted"),
            ),
            gap="sm",
            p="md",
            bg="bg-canvas",
            border="var(--fleur-comp-panel-border)",
            radius="md",
        ),
    )
