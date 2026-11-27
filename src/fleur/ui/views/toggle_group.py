from collections.abc import Mapping, Sequence
from typing import Literal, Unpack

from fleur.core.array import Array
from fleur.core.cond import Cond
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr, ensure_expr
from fleur.core.msg import GroupedMsg
from fleur.core.object import Object
from fleur.core.types import KeyT, ModelT_co, MsgGroupT
from fleur.core.view import View, ViewChild

from ._navigation_behavior import toolbar_effect
from ._selection import toggle_selection
from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .button import Button
from .types import String, ViewStyleArgs


class ToggleGroup(Element[ModelT_co, MsgGroupT]):
    """A group of independently pressed buttons. Each change sends the new selection."""

    def __init__(
        self,
        options: Mapping[KeyT, String] | Expr[Mapping[KeyT, str]],
        *,
        label: String,
        value: Sequence[KeyT] | Expr[Sequence[KeyT]],
        onchange: GroupedMsg[MsgGroupT, PointerEvent, Sequence[KeyT]],
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        selected = value if isinstance(value, Expr) else Expr[Sequence[KeyT]](ensure_expr(value))

        def toggle(key: KeyT | Expr[KeyT], caption: String) -> Button[ModelT_co, MsgGroupT]:
            pressed = Array.includes(selected, key)
            return Button(
                caption,
                variant="ghost",
                onclick=onchange.bind(toggle_selection(selected, key)),
                props={"key": key, "type": "button", "aria-pressed": Cond.when(pressed, "true", "false")},
            )

        buttons: ViewChild[ModelT_co, MsgGroupT]
        if isinstance(options, Expr):
            buttons = Array.map(Object.keys(options), lambda key: toggle(key, options[key]))
        else:
            buttons = [toggle(key, caption) for key, caption in options.items()]
        super().__init__(
            buttons,
            tag="div",
            props=extend_props(
                merge_props(props, element="toggle-group", **style_args),
                {
                    "role": "group",
                    "aria-label": label,
                    "data-fleur-orientation": orientation,
                    **View.dom_effect(toolbar_effect()),
                },
            ),
        )
