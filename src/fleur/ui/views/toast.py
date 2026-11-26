from typing import Unpack

from fleur.core.events import ToastCloseEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT, OptionalContextT

from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .button import Button
from .types import String, ViewStyleArgs


class Toast(Element[ModelT_co, MsgGroupT]):
    """A temporary notification. Clear the model's open flag in the close handler."""

    def __init__(
        self,
        message: String,
        *,
        open: bool | Expr[bool],
        onclose: GroupedMsg[MsgGroupT, ToastCloseEvent, OptionalContextT],
        duration_ms: int | Expr[int] | None = 5000,
        dismiss_label: String = "Dismiss",
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            Element(
                tag="div",
                props={"role": "status", "aria-atomic": "true", "data-fleur-part": "toast-announcement"},
            ),
            Element(
                Element(message, tag="div", props={"aria-hidden": "true", "data-fleur-part": "toast-message"}),
                Button(
                    Element(tag="span", props={"aria-hidden": "true", "data-fleur-part": "close-icon"}),
                    variant="ghost",
                    props={"type": "button", "aria-label": dismiss_label, "data-fleur-part": "toast-dismiss"},
                ),
                tag="div",
                props=extend_props(merge_props(props, element="toast", **style_args), {"hidden": True}),
            ),
            tag="div",
            props={
                "fleurToast": True,
                "data-fleur-part": "toast-root",
                "data-fleur-toast-open": open,
                "data-fleur-toast-duration": duration_ms,
                "ontoastclose": onclose,
            },
        )
