from dataclasses import dataclass
from typing import Sequence

from fleur.core.cmd import Cmd
from fleur.core.component import Component
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr, compile_operand
from fleur.core.model import Model, State
from fleur.core.msg import GroupedMsg, Msg, MsgGroup
from fleur.core.task import TaskLike
from fleur.core.view import View
from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, member_expr
from fleur.types import JsonValue

from ..views import Box, Button, HStack, Text, VStack


@dataclass(frozen=True, slots=True)
class TabSpec:
    label: str
    content: str


class TabsModel(Model):
    active_index: State[int]


class TabsMsg(MsgGroup):
    SELECT: Msg[PointerEvent, int] = Msg()
    NEXT: Msg[PointerEvent, object] = Msg()
    PREV: Msg[PointerEvent, object] = Msg()
    NOOP: Msg[object, object] = Msg()


class _ImmediateTask(TaskLike[object, object]):
    def __init__(self, value: object) -> None:
        self._value = value

    def __compile__(self) -> ESTreeExpression:
        return call(member_expr(ident("Promise"), "resolve"), compile_operand(self._value))


def _on_change_cmd(index: object, on_change: GroupedMsg[TabsMsg, int, object] | None) -> Cmd[TabsModel, TabsMsg]:
    if on_change is None:
        return Cmd.none()
    return Cmd.task(_ImmediateTask(index), on_change, TabsMsg.NOOP)


def tabs(
    items: Sequence[TabSpec],
    *,
    title: str = "Tabs",
    initial_index: int = 0,
    on_change: GroupedMsg[TabsMsg, int, object] | None = None,
) -> Component[TabsModel, TabsMsg]:
    if not items:
        items = [TabSpec(label="Empty", content="No tabs configured")]

    max_index = len(items) - 1
    clamped_initial = min(max(initial_index, 0), max_index)

    panel_expr: Expr[JsonValue | View[TabsModel, TabsMsg]] | View[TabsModel, TabsMsg]
    panel_expr = Box(Text("No tab selected"), p="sm", bg="bg-surface", border="var(--fleur-comp-panel-border)")
    for index in range(max_index, -1, -1):
        panel_expr = Expr.when(
            TabsModel.active_index.equals(index),
            Box(Text(items[index].content), p="sm", bg="bg-surface", border="var(--fleur-comp-panel-border)"),
            panel_expr,
        )

    tab_buttons = [
        Button(
            Expr.when(TabsModel.active_index.equals(index), f"- {item.label}", item.label),
            onclick=TabsMsg.SELECT.bind(index),
            bg="bg-subtle",
            fg="fg-default",
            px="sm",
            py="xs",
            radius="sm",
        )
        for index, item in enumerate(items)
    ]

    next_index = Expr.when(TabsModel.active_index < max_index, TabsModel.active_index + 1, 0)
    prev_index = Expr.when(TabsModel.active_index > 0, TabsModel.active_index - 1, max_index)

    return Component(
        TabsModel(active_index=clamped_initial),
        TabsMsg.caseof(
            TabsMsg.SELECT.then(
                (
                    TabsModel.active_index.set(TabsMsg.SELECT.context),
                    _on_change_cmd(TabsMsg.SELECT.context, on_change),
                )
            ),
            TabsMsg.NEXT.then(
                (
                    TabsModel.active_index.set(next_index),
                    _on_change_cmd(next_index, on_change),
                )
            ),
            TabsMsg.PREV.then(
                (
                    TabsModel.active_index.set(prev_index),
                    _on_change_cmd(prev_index, on_change),
                )
            ),
            TabsMsg.NOOP.then(TabsModel.active_index.set(TabsModel.active_index)),
        ),
        VStack(
            Text(title, font_weight=700),
            HStack(*tab_buttons, gap="xs", flex_wrap="wrap"),
            HStack(
                Button("Prev", onclick=TabsMsg.PREV),
                Button("Next", onclick=TabsMsg.NEXT),
                gap="xs",
            ),
            panel_expr,
            gap="sm",
            p="md",
            bg="bg-canvas",
            border="var(--fleur-comp-panel-border)",
            radius="md",
        ),
    )
