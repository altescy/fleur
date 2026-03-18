from __future__ import annotations

from typing import Any

from fleur.core.events import FocusEvent, InputEvent, KeyboardEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from .base import (
    ColorArg,
    Element,
    FontSizeArg,
    FontWeightArg,
    LengthArg,
    Props,
    RadiusArg,
    SpacingArg,
    StringArg,
    StyleMap,
    _merge_props,
)


class Input(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *,
        props: Props | None = None,
        type: StringArg | None = "text",
        value: StringArg | None = None,
        placeholder: StringArg | None = None,
        oninput: GroupedMsg[MsgGroupT, InputEvent, Any] | None = None,
        onchange: GroupedMsg[MsgGroupT, InputEvent, Any] | None = None,
        onfocus: GroupedMsg[MsgGroupT, FocusEvent, Any] | None = None,
        onblur: GroupedMsg[MsgGroupT, FocusEvent, Any] | None = None,
        onkeydown: GroupedMsg[MsgGroupT, KeyboardEvent, Any] | None = None,
        onkeyup: GroupedMsg[MsgGroupT, KeyboardEvent, Any] | None = None,
        bg: ColorArg | None = None,
        fg: ColorArg | None = None,
        p: SpacingArg | None = None,
        px: SpacingArg | None = None,
        py: SpacingArg | None = None,
        radius: RadiusArg | None = None,
        w: LengthArg | None = None,
        h: LengthArg | None = None,
        border: StringArg | None = None,
        font_size: FontSizeArg | None = None,
        font_weight: FontWeightArg | None = None,
        font_family: StringArg | None = None,
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
        if type is not None:
            merged["type"] = type
        if value is not None:
            merged["value"] = value
        if placeholder is not None:
            merged["placeholder"] = placeholder
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
        super().__init__(tag="input", props=merged)
