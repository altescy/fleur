from __future__ import annotations

from typing import Any, Literal, Unpack

from fleur.core.events import PointerEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from . import _utils
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Button(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild,
        variant: Literal["primary", "secondary", "ghost"] = "primary",
        onclick: GroupedMsg[MsgGroupT, PointerEvent, Any] | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, element="button", **style_args)
        if variant != "primary":
            merged = _utils.extend_props(merged, {"data-fleur-variant": variant})
        if onclick is not None:
            merged = _utils.extend_props(merged, {"onclick": onclick})
        super().__init__(*children, tag="button", props=merged)
