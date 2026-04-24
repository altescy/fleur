from __future__ import annotations

from typing import Any

from fleur.core.events import FocusEvent, InputEvent, KeyboardEvent
from fleur.core.expr import Expr
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
    _merge_props,
)


class Textarea(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *,
        props: ViewProps | None = None,
        value: String | None = None,
        placeholder: String | None = None,
        rows: int | Expr[int] | None = None,
        cols: int | Expr[int] | None = None,
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
        if value is not None:
            merged["value"] = value
        if placeholder is not None:
            merged["placeholder"] = placeholder
        if rows is not None:
            merged["rows"] = rows
        if cols is not None:
            merged["cols"] = cols
        if oninput is not None:
            merged["oninput"] = oninput
        if onchange is not None:
            merged["onchange"] = onchange
        if onfocus is not None:
            merged["onfocus"] = onfocus
        if onblur is not None:
            merged["onblur"] = onblur
        if onkeydown is not None:
            merged["onkeydown"] = onkeydown
        if onkeyup is not None:
            merged["onkeyup"] = onkeyup
        super().__init__(tag="textarea", props=merged)
