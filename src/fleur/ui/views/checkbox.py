from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from fleur.core.events import FocusEvent, InputEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from .base import (
    Color,
    Element,
    Length,
    Props,
    Radius,
    Spacing,
    String,
    Style,
    StyleMap,
    _merge_props,
)


class Checkbox(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *,
        props: Props | None = None,
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
        existing_style = merged.get("style")
        style_props: dict[str, Style] = (
            {key: cast(Style, value) for key, value in existing_style.items()}
            if isinstance(existing_style, Mapping)
            else {}
        )
        style_props.setdefault("width", "1rem")
        style_props.setdefault("height", "1rem")
        style_props.setdefault("accent-color", "var(--fleur-color-accent-solid-bg)")
        merged = {**merged, "style": style_props}

        merged["type"] = "checkbox"
        if checked is not None:
            merged["checked"] = cast(Any, checked)
        if value is not None:
            merged["value"] = value
        if name is not None:
            merged["name"] = name
        if disabled is not None:
            merged["disabled"] = cast(Any, disabled)
        if required is not None:
            merged["required"] = cast(Any, required)
        if oninput is not None:
            merged["oninput"] = oninput
        if onchange is not None:
            merged["onchange"] = onchange
        if onfocus is not None:
            merged["onfocus"] = onfocus
        if onblur is not None:
            merged["onblur"] = onblur
        super().__init__(tag="input", props=merged)
