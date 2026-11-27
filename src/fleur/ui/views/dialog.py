from typing import Unpack, overload

from fleur.core.boolean import Boolean
from fleur.core.cond import Cond
from fleur.core.dom import DomAction, DomEffect, DomElement, EventBinding, EventMessage
from fleur.core.events import DialogCloseEvent
from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT
from fleur.core.view import View, ViewProp

from ._dom_helpers import focus_opener
from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import String, ViewStyleArgs


class Dialog(Element[ModelT_co, MsgGroupT]):
    """A native modal. Handle the close event by clearing the model's open flag.

    Name the dialog with either `labelledby`, the id of a visible title inside it, or `label`.
    """

    @overload
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT],
        labelledby: String,
        open: bool | Expr[bool],
        onclose: EventMessage[MsgGroupT, DialogCloseEvent],
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None: ...

    @overload
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT],
        label: String,
        open: bool | Expr[bool],
        onclose: EventMessage[MsgGroupT, DialogCloseEvent],
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None: ...

    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT],
        open: bool | Expr[bool],
        onclose: EventMessage[MsgGroupT, DialogCloseEvent],
        labelledby: String | None = None,
        label: String | None = None,
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        if (labelledby is None) == (label is None):
            raise TypeError("Dialog requires exactly one of `labelledby` or `label` as its accessible name.")
        name: dict[str, ViewProp[MsgGroupT]] = (
            {"aria-labelledby": labelledby} if labelledby is not None else {"aria-label": label}
        )

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

        closed = EventBinding[MsgGroupT, DialogCloseEvent](
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
                    **name,
                    "open": None,
                    **View.dom_effect(effect),
                    **closed.properties("close"),
                },
            ),
        )
