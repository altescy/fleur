from __future__ import annotations

from typing import Any

from fleur.core.events import FocusEvent, InputEvent, KeyboardEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from .base import (
    Color,
    Element,
    FontSize,
    FontWeight,
    Length,
    Radius,
    Spacing,
    String,
    StyleMap,
    ViewProps,
    _extend_props,
    _merge_props,
)


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
        bg: Color | None = None,
        fg: Color | None = None,
        p: Spacing | None = None,
        px: Spacing | None = None,
        py: Spacing | None = None,
        radius: Radius | None = None,
        w: Length | None = None,
        h: Length | None = None,
        border: String | None = None,
        font_size: FontSize | None = None,
        font_weight: FontWeight | None = None,
        font_family: String | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(
            props,
            bg=bg,
            fg=fg,
            p=p,
            px=px,
            py=py,
            radius=radius,
            w=w,
            h=h,
            border=border,
            font_size=font_size,
            font_weight=font_weight,
            font_family=font_family,
            style=style,
        )
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
        merged = _extend_props(merged, extra)
        super().__init__(tag="input", props=merged)
