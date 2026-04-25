from __future__ import annotations

from fleur.core.types import ModelT_co, MsgGroupT_co

from .base import (
    Color,
    Element,
    FlexWrap,
    Length,
    Radius,
    Spacing,
    String,
    StyleMap,
    ViewChild,
    ViewProps,
    _merge_props,
)


class HStack(Element[ModelT_co, MsgGroupT_co]):
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
        max_w: Length | None = None,
        border: String | None = None,
        font_family: String | None = None,
        flex_wrap: FlexWrap | None = None,
        justify: String | None = None,
        align: String | None = None,
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
            max_w=max_w,
            border=border,
            font_family=font_family,
            display="flex",
            flex_direction="row",
            flex_wrap=flex_wrap,
            justify=justify,
            align=align,
            style=style,
        )
        super().__init__(*children, tag="div", props=merged)
