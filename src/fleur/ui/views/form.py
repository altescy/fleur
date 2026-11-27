from __future__ import annotations

from typing import Any, Unpack

from fleur.core.dom import DomEvents, EventBinding
from fleur.core.events import SubmitEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from . import _utils
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Form(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        onsubmit: GroupedMsg[MsgGroupT, SubmitEvent, Any] | None = None,
        prevent_default: bool | Expr[bool] = False,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        if prevent_default is not False:
            cancel = EventBinding.on(
                DomEvents.submit,
                prevent_default=prevent_default,
                when=lambda event: event.target.same_as(event.current_target),
                capture=True,
            )
            merged = _utils.extend_props(merged, cancel)
        if onsubmit is not None:
            merged = _utils.extend_props(merged, {"onsubmit": onsubmit})
        super().__init__(*children, tag="form", props=merged)
