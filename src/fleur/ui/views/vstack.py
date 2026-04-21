from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from fleur.core.types import ModelT_co, MsgGroupT_co

from .base import (
    Color,
    Element,
    FlexDirection,
    FlexWrap,
    Length,
    Props,
    Radius,
    Spacing,
    String,
    Style,
    StyleMap,
    ViewChild,
    _merge_props,
)


class VStack(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
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
        flex_direction: FlexDirection | None = None,
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
            flex_direction=flex_direction,
            flex_wrap=flex_wrap,
            justify=justify,
            align=align,
            style=style,
        )
        existing_style = merged.get("style")
        style_props: dict[str, Style] = (
            {key: cast(Style, value) for key, value in existing_style.items()}
            if isinstance(existing_style, Mapping)
            else {}
        )
        style_props.setdefault("display", "flex")
        style_props.setdefault("flex-direction", "column")
        merged["style"] = style_props
        super().__init__(*children, tag="div", props=merged)
