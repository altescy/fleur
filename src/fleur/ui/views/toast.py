from typing import Unpack

from fleur.core.cond import Cond
from fleur.core.dom import EventBinding, EventMessage
from fleur.core.events import ToastCloseEvent
from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT
from fleur.core.view import View

from ._toast_behavior import toast_effect
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
        onclose: EventMessage[MsgGroupT, ToastCloseEvent],
        duration_ms: int | Expr[int | None] | None = 5000,
        dismiss_label: String = "Dismiss",
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        close = EventBinding[MsgGroupT, ToastCloseEvent](
            onclose,
            payload=lambda event: {"reason": Cond.when(Cond.equal(event.detail_text, "timeout"), "timeout", "dismiss")},
        )
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
                **View.dom_effect(toast_effect(open, duration_ms)),
                "data-fleur-part": "toast-root",
                **close.properties("toastclose"),
            },
        )
