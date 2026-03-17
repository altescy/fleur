from __future__ import annotations

from fleur.core.types import ModelT_co, MsgGroupT_co

from .base import Element, LengthValue, Props, RadiusValue, RawColor, SpacingValue, StyleMap, ViewChild, _merge_props


class Box(Element[ModelT_co, MsgGroupT_co]):
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
        w: LengthValue | None = None,
        h: LengthValue | None = None,
        max_w: LengthValue | None = None,
        border: str | None = None,
        font_family: str | None = None,
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
