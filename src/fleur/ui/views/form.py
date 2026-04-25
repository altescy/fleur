from __future__ import annotations

from typing import Any

from fleur.core.events import SubmitEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from .base import (
    Color,
    Element,
    Length,
    Radius,
    Spacing,
    String,
    StyleMap,
    ViewChild,
    ViewProps,
    _extend_props,
    _merge_props,
)


class Form(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        onsubmit: GroupedMsg[MsgGroupT, SubmitEvent, Any] | None = None,
        gap: Spacing | None = None,
        bg: Color | None = None,
        fg: Color | None = None,
        p: Spacing | None = None,
        px: Spacing | None = None,
        py: Spacing | None = None,
        radius: Radius | None = None,
        w: Length | None = None,
        h: Length | None = None,
        border: String | None = None,
        font_family: String | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(
            props,
            gap=gap,
            bg=bg,
            fg=fg,
            p=p,
            px=px,
            py=py,
            radius=radius,
            w=w,
            h=h,
            border=border,
            font_family=font_family,
            style=style,
        )
        if onsubmit is not None:
            merged = _extend_props(merged, {"onsubmit": onsubmit})
        super().__init__(*children, tag="form", props=merged)
