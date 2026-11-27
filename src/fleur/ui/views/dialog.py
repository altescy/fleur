from typing import Unpack

from fleur.core.boolean import Boolean
from fleur.core.cond import Cond
from fleur.core.dom import DomAction, DomEffect, DomElement, EventBinding
from fleur.core.events import DialogCloseEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT, OptionalContextT
from fleur.core.view import View

from ._dom_helpers import focus_opener
from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Dialog(Element[ModelT_co, MsgGroupT]):
    """A native modal. Handle the close event by clearing the model's open flag."""

    def __init__(
        self,
        *children: ViewChild,
        open: bool | Expr[bool],
        onclose: GroupedMsg[MsgGroupT, DialogCloseEvent, OptionalContextT],
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        def sync(element: DomElement) -> DomAction:
            dialog = element.as_dialog()
            return DomAction.when(
                Cond.not_equal(dialog.is_open, open),
                DomAction.when(
                    open,
                    DomAction.batch(focus_opener(dialog), dialog.show_modal()),
                    otherwise=dialog.close(),
                ),
            )

        closed = EventBinding(
            onclose,
            when=lambda event: Cond.every(
                event.current_target.connected, Boolean.negate(event.current_target.as_dialog().is_open)
            ),
        )
        merged = merge_props(props, element="dialog", **style_args)
        effect = DomEffect("dialog", sync, dependencies=[open], dispose=lambda element: element.as_dialog().close())
        super().__init__(
            *children,
            tag="dialog",
            props=extend_props(
                merged,
                {
                    "open": None,
                    **View.dom_effect(effect),
                    **closed.properties("close"),
                },
            ),
        )
