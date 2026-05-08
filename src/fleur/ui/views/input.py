from __future__ import annotations

from typing import Any, Unpack

from fleur.core.events import FocusEvent, InputEvent, KeyboardEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from . import _utils
from .base import Element, ViewProps
from .types import String, ViewStyleArgs


class Input(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *,
        props: ViewProps | None = None,
        type: String | None = "text",
        value: String | None = None,
        placeholder: String | None = None,
        oninput: GroupedMsg[MsgGroupT, InputEvent, Any] | None = None,
        onchange: GroupedMsg[MsgGroupT, InputEvent, Any] | None = None,
        onfocus: GroupedMsg[MsgGroupT, FocusEvent, Any] | None = None,
        onblur: GroupedMsg[MsgGroupT, FocusEvent, Any] | None = None,
        onkeydown: GroupedMsg[MsgGroupT, KeyboardEvent, Any] | None = None,
        onkeyup: GroupedMsg[MsgGroupT, KeyboardEvent, Any] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        extra: dict[str, Any] = {}
        if type is not None:
            extra["type"] = type
        if value is not None:
            extra["value"] = value
        if placeholder is not None:
            extra["placeholder"] = placeholder
        if oninput is not None:
            extra["oninput"] = oninput
        if onchange is not None:
            extra["onchange"] = onchange
        if onfocus is not None:
            extra["onfocus"] = onfocus
        if onblur is not None:
            extra["onblur"] = onblur
        if onkeydown is not None:
            extra["onkeydown"] = onkeydown
        if onkeyup is not None:
            extra["onkeyup"] = onkeyup
        merged = _utils.extend_props(merged, extra)
        super().__init__(tag="input", props=merged)
