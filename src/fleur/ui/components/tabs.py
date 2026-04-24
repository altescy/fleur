from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Sequence, TypeAlias

from fleur.core.cmd import Cmd
from fleur.core.component import Component
from fleur.core.cond import Cond
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr, ensure_expr
from fleur.core.model import Model, State
from fleur.core.msg import GroupedMsg, Msg, MsgGroup
from fleur.core.task import TaskLike
from fleur.core.types import FleurValue
from fleur.core.view import View
from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, member_expr
from fleur.types import JsonValue

from ..views import Box, Button, HStack, Text, VStack
from ..views.base import ViewProps

TabsChild: TypeAlias = str | View["TabsModel", "TabsMsg"] | Expr[JsonValue | View["TabsModel", "TabsMsg"]]


@dataclass(frozen=True, slots=True)
class TabSpec:
    label: str | Expr[str]
    content: JsonValue | View | Expr[JsonValue | View]


class TabsModel(Model):
    active_index: State[int]


class TabsMsg(MsgGroup):
    SELECT = Msg[PointerEvent, int]()
    NEXT = Msg[PointerEvent, Any]()
    PREV = Msg[PointerEvent, Any]()
    NOOP = Msg()


class _ImmediateTask(TaskLike):
    def __init__(self, value: FleurValue | Expr) -> None:
        self._value = value

    def __compile__(self) -> ESTreeExpression:
        return call(member_expr(ident("Promise"), "resolve"), ensure_expr(self._value))


def _on_change_cmd(index: int | Expr[int], on_change: GroupedMsg[TabsMsg, int] | None) -> Cmd[TabsModel, TabsMsg]:
    if on_change is None:
        return Cmd.none()
    return Cmd.task(_ImmediateTask(index), on_change, TabsMsg.NOOP)


def _merge_component_props(defaults: ViewProps | None, overrides: ViewProps | None) -> ViewProps:
    merged: ViewProps = dict(defaults or {})
    if overrides is None:
        return merged

    for key, value in overrides.items():
        if key == "style" and isinstance(value, Mapping) and isinstance(merged.get("style"), Mapping):
            style = merged["style"]
            assert isinstance(style, Mapping)
            style = {**style, **value}
            merged = {**merged, "style": style}
            continue
        merged[key] = value
    return merged


def tabs(
    items: Sequence[TabSpec],
    *,
    title: str | None | Expr[str | None] = None,
    initial_index: int = 0,
    on_change: GroupedMsg[TabsMsg, int] | None = None,
    empty_message: str | Expr[str] = "No tab selected",
    props: ViewProps | None = None,
    list_props: ViewProps | None = None,
    panel_props: ViewProps | None = None,
) -> Component[TabsModel, TabsMsg]:
    if not items:
        items = [TabSpec(label="Empty", content="No tabs configured")]

    max_index = len(items) - 1
    clamped_initial = min(max(initial_index, 0), max_index)

    resolved_root_props = _merge_component_props(
        {
            "style": {
                "gap": "var(--fleur-space-sm)",
                "padding": "var(--fleur-space-md)",
                "background": "var(--fleur-color-bg-canvas)",
                "border": "var(--fleur-comp-panel-border)",
                "border-radius": "var(--fleur-radius-md)",
            }
        },
        props,
    )
    resolved_list_props = _merge_component_props(
        {
            "style": {
                "gap": "var(--fleur-space-xs)",
                "padding": "var(--fleur-space-xs)",
                "background": "var(--fleur-color-bg-subtle)",
                "border-radius": "var(--fleur-radius-md)",
                "flex-wrap": "wrap",
                "align-items": "center",
            }
        },
        list_props,
    )
    resolved_panel_props = _merge_component_props(
        {
            "style": {
                "padding": "var(--fleur-space-sm)",
                "background": "var(--fleur-color-bg-surface)",
            }
        },
        panel_props,
    )

    panel_expr: Expr[FleurValue | View[TabsModel, TabsMsg]] | View[TabsModel, TabsMsg]
    panel_expr = Box(Text(empty_message), props=resolved_panel_props)
    for index in range(max_index, -1, -1):
        panel_expr = Cond.when(
            TabsModel.active_index.eq(index),
            Box(items[index].content, props=resolved_panel_props),
            panel_expr,
        )

    tab_buttons = [
        Button(
            item.label,
            onclick=TabsMsg.SELECT.bind(index),
            bg=Cond.when(
                TabsModel.active_index.eq(index),
                "var(--fleur-color-bg-surface)",
                "transparent",
            ),
            fg=Cond.when(
                TabsModel.active_index.eq(index),
                "var(--fleur-color-fg-default)",
                "var(--fleur-color-fg-muted)",
            ),
            border=Cond.when(
                TabsModel.active_index.eq(index),
                "1px solid var(--fleur-color-border-default)",
                "1px solid transparent",
            ),
            px="sm",
            py="xs",
            radius="sm",
            font_weight=Cond.when(TabsModel.active_index.eq(index), "600", "500"),
            style={
                "box-shadow": Cond.when(
                    TabsModel.active_index.eq(index),
                    "0 1px 2px rgba(10, 10, 10, 0.08)",
                    "none",
                )
            },
        )
        for index, item in enumerate(items)
    ]

    next_index = Cond.when(TabsModel.active_index < max_index, TabsModel.active_index + 1, 0)
    prev_index = Cond.when(TabsModel.active_index > 0, TabsModel.active_index - 1, max_index)

    root_children: list[TabsChild] = []
    if title is not None:
        root_children.append(Text(title, font_weight=700))
    root_children.extend(
        [
            HStack(
                *tab_buttons,
                props=resolved_list_props,
            ),
            panel_expr,
        ]
    )

    return Component(
        TabsModel(active_index=clamped_initial),
        TabsMsg.caseof(
            TabsMsg.SELECT.then(
                (
                    State.set(TabsModel.active_index, TabsMsg.SELECT.context),
                    _on_change_cmd(TabsMsg.SELECT.context, on_change),
                )
            ),
            TabsMsg.NEXT.then(
                (
                    State.set(TabsModel.active_index, next_index),
                    _on_change_cmd(next_index, on_change),
                )
            ),
            TabsMsg.PREV.then(
                (
                    State.set(TabsModel.active_index, prev_index),
                    _on_change_cmd(prev_index, on_change),
                )
            ),
            TabsMsg.NOOP.then(State.set(TabsModel.active_index, TabsModel.active_index)),
        ),
        VStack(*root_children, props=resolved_root_props),
    )
