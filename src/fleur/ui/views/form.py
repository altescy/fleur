from __future__ import annotations

from typing import Any

from fleur.core.events import SubmitEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from .base import (
    ColorArg,
    Element,
    LengthArg,
    Props,
    RadiusArg,
    SpacingArg,
    StringArg,
    StyleMap,
    ViewChild,
    _merge_props,
)


class Form(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        onsubmit: GroupedMsg[MsgGroupT, SubmitEvent, Any] | None = None,
        gap: SpacingArg | None = None,
        bg: ColorArg | None = None,
        fg: ColorArg | None = None,
        p: SpacingArg | None = None,
        px: SpacingArg | None = None,
        py: SpacingArg | None = None,
        radius: RadiusArg | None = None,
        w: LengthArg | None = None,
        h: LengthArg | None = None,
        border: StringArg | None = None,
        font_family: StringArg | None = None,
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
            merged["onsubmit"] = onsubmit
        super().__init__(*children, tag="form", props=merged)
