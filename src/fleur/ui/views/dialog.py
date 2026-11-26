from typing import Unpack

from fleur.core.events import DialogCloseEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT, OptionalContextT

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
        merged = merge_props(props, element="dialog", **style_args)
        super().__init__(*children, tag="dialog", props=extend_props(merged, {"open": open, "onclose": onclose}))
