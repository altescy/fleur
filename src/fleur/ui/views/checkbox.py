from __future__ import annotations

from typing import Any, cast

from fleur.core.events import FocusEvent, InputEvent
from fleur.core.expr import Expr
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
    ViewProps,
    _extend_props,
    _merge_props,
    _set_default_style,
)


class Checkbox(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *,
        props: ViewProps | None = None,
        checked: bool | Expr[bool] | None = None,
        value: String | None = None,
        name: String | None = None,
        disabled: bool | Expr[bool] | None = None,
        required: bool | Expr[bool] | None = None,
        oninput: GroupedMsg[MsgGroupT, InputEvent, Any] | None = None,
        onchange: GroupedMsg[MsgGroupT, InputEvent, Any] | None = None,
        onfocus: GroupedMsg[MsgGroupT, FocusEvent, Any] | None = None,
        onblur: GroupedMsg[MsgGroupT, FocusEvent, Any] | None = None,
        bg: Color | None = None,
        p: Spacing | None = None,
        radius: Radius | None = None,
        w: Length | None = None,
        h: Length | None = None,
        border: String | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(
            props,
            bg=bg,
            p=p,
            radius=radius,
            w=w,
            h=h,
            border=border,
            style=style,
        )
        merged = _set_default_style(
            merged,
            {
                "width": "1rem",
                "height": "1rem",
                "accent-color": "var(--fleur-color-accent-solid-bg)",
            },
        )
        extra: dict[str, Any] = {"type": "checkbox"}
        if checked is not None:
            extra["checked"] = cast(Any, checked)
        if value is not None:
            extra["value"] = value
        if name is not None:
            extra["name"] = name
        if disabled is not None:
            extra["disabled"] = cast(Any, disabled)
        if required is not None:
            extra["required"] = cast(Any, required)
        if oninput is not None:
            extra["oninput"] = oninput
        if onchange is not None:
            extra["onchange"] = onchange
        if onfocus is not None:
            extra["onfocus"] = onfocus
        if onblur is not None:
            extra["onblur"] = onblur
        merged = _extend_props(merged, extra)
        super().__init__(tag="input", props=merged)
