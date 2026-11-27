from __future__ import annotations

from typing import Literal, Unpack

from fleur.core.dom import EventMessage
from fleur.core.events import PointerEvent
from fleur.core.types import ModelT_co, MsgGroupT

from . import _utils
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Button(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT],
        variant: Literal["primary", "secondary", "ghost"] = "primary",
        onclick: EventMessage[MsgGroupT, PointerEvent] | None = None,
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, element="button", **style_args)
        if variant != "primary":
            merged = _utils.extend_props(merged, {"data-fleur-variant": variant})
        if onclick is not None:
            merged = _utils.extend_props(merged, {"onclick": onclick})
        super().__init__(*children, tag="button", props=merged)
