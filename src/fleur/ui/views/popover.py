from collections.abc import Callable, Mapping
from typing import Literal, Unpack

from fleur.core.events import ToggleEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT, MsgGroupT, OptionalContextT
from fleur.core.view import View, ViewProp

from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import String, ViewStyleArgs


def _anchored_panel(
    *children: ViewChild,
    id: String,
    trigger: Callable[[Mapping[str, ViewProp]], View[ModelT, MsgGroupT]],
    role: Literal["dialog", "menu"],
    panel_props: ViewProps,
    root_props: Mapping[str, ViewProp],
) -> tuple[View[ModelT, MsgGroupT], View[ModelT, MsgGroupT], ViewProps]:
    trigger_id = id + "-trigger"
    trigger_attrs: dict[str, ViewProp] = {
        "id": trigger_id,
        "type": "button",
        "popovertarget": id,
        "aria-haspopup": role,
    }
    if role == "menu":
        trigger_attrs.update({"aria-expanded": "false", "aria-controls": id})
    panel = Element(
        *children,
        tag="div",
        props=extend_props(
            extend_props({"role": role, "aria-labelledby": trigger_id}, panel_props),
            {"id": id, "popover": "auto"},
        ),
    )
    return trigger(trigger_attrs), panel, {"data-fleur-part": "popover-root", **root_props}


class Popover(Element[ModelT, MsgGroupT]):
    """A non-modal panel. Forward the trigger attributes to a native button."""

    def __init__(
        self,
        *children: ViewChild,
        id: String,
        trigger: Callable[[Mapping[str, ViewProp]], View[ModelT, MsgGroupT]],
        open: bool | Expr[bool] | None = None,
        ontoggle: GroupedMsg[MsgGroupT, ToggleEvent, OptionalContextT] | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp] = {}
        if open is not None:
            attrs["fleurPopoverOpen"] = open
        if ontoggle is not None:
            attrs["ontoggle"] = ontoggle
        opener, panel, root = _anchored_panel(
            *children,
            id=id,
            trigger=trigger,
            role="dialog",
            panel_props=extend_props(merge_props(props, element="popover", **style_args), attrs),
            root_props={},
        )
        super().__init__(opener, panel, tag="div", props=root)
