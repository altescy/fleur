from collections.abc import Mapping
from typing import Literal, Unpack, cast

from typing_extensions import TypeAlias

from fleur import Array, Cond, Object, View
from fleur.core import Expr, GroupedMsg, PointerEvent
from fleur.core.expr import ensure_expr
from fleur.core.types import ModelT, MsgGroupT
from fleur.ui.views import Box, Button, HStack, VStack
from fleur.ui.views.types import ViewStyleArgs

_ActiveTab: TypeAlias = str
_TabsContents: TypeAlias = Mapping[str, View[ModelT, MsgGroupT]]
TabsContents: TypeAlias = _TabsContents[ModelT, MsgGroupT] | Expr[_TabsContents[ModelT, MsgGroupT]]
ActiveTab: TypeAlias = _ActiveTab | Expr[_ActiveTab]


def tabs(
    contents: TabsContents[ModelT, MsgGroupT],
    active_tab: ActiveTab,
    onselect: GroupedMsg[MsgGroupT, PointerEvent, str] | None = None,
    **style_args: Unpack[ViewStyleArgs],
) -> View[ModelT, MsgGroupT]:
    contents = Expr(ensure_expr(contents))
    return VStack(
        HStack(
            Array.map(
                Object.keys(contents),
                lambda name: Button(
                    name,
                    onclick=onselect.bind(name) if onselect is not None else None,
                    bg=Cond.when(Cond.equal(name, active_tab), "bg-surface", "transparent"),
                    fg=Cond.when(Cond.equal(name, active_tab), "fg-default", "fg-muted"),
                    border=Cond.when(
                        Cond.equal(name, active_tab),
                        "1px solid var(--fleur-color-border-default)",
                        "1px solid transparent",
                    ),
                    px="sm",
                    py="xs",
                    radius="sm",
                    font_weight=Cond.when(Cond.equal(name, active_tab), 600, 500),
                    box_shadow=Cond.when(
                        Cond.equal(name, active_tab),
                        "0 1px 2px rgba(10, 10, 10, 0.08)",
                        "none",
                    ),
                ),
            ),
            gap="xs",
            bg="bg-subtle",
            radius="md",
            flex_wrap="wrap",
            align="center",
        ),
        Array.map(
            Object.keys(contents),
            lambda name: Box(
                contents[name],
                display=cast(
                    Expr[Literal["block", "none"]],
                    Cond.when(Cond.equal(name, active_tab), "block", "none"),
                ),
            ),
        ),
        **style_args,
    )
