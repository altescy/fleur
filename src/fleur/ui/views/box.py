from typing import Any, Unpack

from fleur.core.events import PointerEvent
from fleur.core.msg import GroupedMsg
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
        *children: ViewChild,
        onclick: GroupedMsg[MsgGroupT_co, PointerEvent, Any] | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        if onclick is not None:
            merged = _utils.extend_props(merged, {"onclick": onclick})
        super().__init__(*children, tag="div", props=merged)
