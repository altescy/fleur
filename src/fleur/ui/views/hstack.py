from __future__ import annotations

from collections.abc import Mapping

from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.types import JsonValue

from .base import (
    Element,
    FlexWrap,
    LengthValue,
    Props,
    RadiusValue,
    RawColor,
    SpacingValue,
    StyleMap,
    ViewChild,
    _merge_props,
)


class HStack(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        gap: SpacingValue | None = None,
        bg: RawColor | str | None = None,
        fg: RawColor | str | None = None,
        p: SpacingValue | None = None,
        px: SpacingValue | None = None,
        py: SpacingValue | None = None,
        radius: RadiusValue | None = None,
        mx: SpacingValue | None = None,
        my: SpacingValue | None = None,
        max_w: LengthValue | None = None,
        border: str | None = None,
        font_family: str | None = None,
        flex_wrap: FlexWrap | None = None,
        justify: str | None = None,
        align: str | None = None,
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
        existing_style = merged.get("style")
        style_props: dict[str, JsonValue] = dict(existing_style.items()) if isinstance(existing_style, Mapping) else {}
        style_props.setdefault("display", "flex")
        style_props.setdefault("flex-direction", "row")
        merged["style"] = style_props
        super().__init__(*children, tag="div", props=merged)
