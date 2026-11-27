from typing import Unpack

from fleur.core.dom import EventMessage
from fleur.core.events import PointerEvent
from fleur.core.types import ModelT_co, MsgGroupT_co

from . import _utils
from .base import (
    Element,
    ViewChild,
    ViewProps,
)
from .types import ViewStyleArgs


class Box(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        onclick: EventMessage[MsgGroupT_co, PointerEvent] | None = None,
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, element="box", **style_args)
        if onclick is not None:
            merged = _utils.extend_props(merged, {"onclick": onclick})
        super().__init__(*children, tag="div", props=merged)
