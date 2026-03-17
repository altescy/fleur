from __future__ import annotations

from fleur.core.types import ModelT_co, MsgGroupT_co

from .base import ColorArg, Element, FontSizeArg, FontWeightArg, Props, StringArg, ViewChild, _merge_props


class Text(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        text: ViewChild,
        *,
        props: Props | None = None,
        fg: ColorArg | None = None,
        bg: ColorArg | None = None,
        font_size: FontSizeArg | None = None,
        font_weight: FontWeightArg | None = None,
        font_family: StringArg | None = None,
    ) -> None:
        super().__init__(
            text,
            tag="span",
            props=_merge_props(
                props,
                fg=fg,
                bg=bg,
                font_size=font_size,
                font_weight=font_weight,
                font_family=font_family,
            ),
        )
