from __future__ import annotations

from fleur.core.types import ModelT_co, MsgGroupT_co

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


class Box(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        gap: SpacingArg | None = None,
        bg: ColorArg | None = None,
        fg: ColorArg | None = None,
        p: SpacingArg | None = None,
        px: SpacingArg | None = None,
        py: SpacingArg | None = None,
        radius: RadiusArg | None = None,
        mx: SpacingArg | None = None,
        my: SpacingArg | None = None,
        w: LengthArg | None = None,
        h: LengthArg | None = None,
        max_w: LengthArg | None = None,
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
            mx=mx,
            my=my,
            w=w,
            h=h,
            max_w=max_w,
            border=border,
            font_family=font_family,
            style=style,
        )
        super().__init__(*children, tag="div", props=merged)
