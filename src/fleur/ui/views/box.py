from __future__ import annotations

from fleur.core.types import ModelT_co, MsgGroupT_co

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
    _merge_props,
)


class Box(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        gap: Spacing | None = None,
        bg: Color | None = None,
        fg: Color | None = None,
        p: Spacing | None = None,
        px: Spacing | None = None,
        py: Spacing | None = None,
        radius: Radius | None = None,
        mx: Spacing | None = None,
        my: Spacing | None = None,
        w: Length | None = None,
        h: Length | None = None,
        max_w: Length | None = None,
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
