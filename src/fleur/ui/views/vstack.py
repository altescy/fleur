from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.types import JsonValue

from .base import (
    ColorArg,
    Element,
    FlexDirection,
    FlexWrap,
    LengthArg,
    Props,
    RadiusArg,
    SpacingArg,
    StringArg,
    StyleMap,
    StyleValue,
    ViewChild,
    _merge_props,
)


class VStack(Element[ModelT_co, MsgGroupT_co]):
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
        max_w: LengthArg | None = None,
        border: StringArg | None = None,
        font_family: StringArg | None = None,
        flex_direction: FlexDirection | Expr[JsonValue] | None = None,
        flex_wrap: FlexWrap | Expr[JsonValue] | None = None,
        justify: StringArg | None = None,
        align: StringArg | None = None,
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
        style_props: dict[str, StyleValue] = (
            {key: cast(StyleValue, value) for key, value in existing_style.items()}
            if isinstance(existing_style, Mapping)
            else {}
        )
        style_props.setdefault("display", "flex")
        style_props.setdefault("flex-direction", "column")
        merged["style"] = style_props
        super().__init__(*children, tag="div", props=merged)
