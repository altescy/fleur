from collections.abc import Callable, Mapping
from typing import Unpack

from fleur.core.cond import Cond
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT, ModelT_co, MsgGroupT, OptionalContextT
from fleur.core.view import View, ViewProp

from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .popover import _anchored_panel
from .types import String, ViewStyleArgs


class Menu(Element[ModelT, MsgGroupT]):
    """An action menu. Forward the trigger attributes to a native button."""

    def __init__(
        self,
        *items: ViewChild,
        id: String,
        trigger: Callable[[Mapping[str, ViewProp]], View[ModelT, MsgGroupT]],
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        opener, panel, root = _anchored_panel(
            *items,
            id=id,
            trigger=trigger,
            role="menu",
            panel_props=extend_props(merge_props(props, element="menu", **style_args), {"tabindex": -1}),
            root_props={"fleurMenu": True},
        )
        super().__init__(opener, panel, tag="div", props=root)


class ContextMenu(Element[ModelT, MsgGroupT]):
    """An action menu opened by right-click or the keyboard on a focusable region."""

    def __init__(
        self,
        *items: ViewChild,
        id: String,
        trigger: Callable[[Mapping[str, ViewProp]], View[ModelT, MsgGroupT]],
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        trigger_id = id + "-trigger"
        super().__init__(
            trigger(
                {
                    "id": trigger_id,
                    "tabindex": 0,
                    "aria-haspopup": "menu",
                    "aria-expanded": "false",
                    "aria-controls": id,
                    "aria-keyshortcuts": "Shift+F10",
                }
            ),
            Element(
                *items,
                tag="div",
                props=extend_props(
                    merge_props(props, element="menu", **style_args),
                    {"id": id, "role": "menu", "aria-labelledby": trigger_id, "tabindex": -1, "popover": "auto"},
                ),
            ),
            tag="div",
            props={"data-fleur-part": "context-menu-root", "fleurMenu": True},
        )


class MenuItem(Element[ModelT_co, MsgGroupT]):
    """An action that dispatches a message when selected."""

    def __init__(
        self,
        *children: ViewChild,
        onclick: GroupedMsg[MsgGroupT, PointerEvent, OptionalContextT],
        disabled: bool | Expr[bool] = False,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp] = {
            "type": "button",
            "role": "menuitem",
            "tabindex": -1,
            "aria-disabled": Cond.when(disabled, "true", None),
            "onclick": onclick,
        }
        merged = merge_props(props, element="menu-item", **style_args)
        super().__init__(*children, tag="button", props=extend_props(merged, attrs))
