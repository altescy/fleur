from __future__ import annotations

from typing import Any

from fleur.core.events import PointerEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from .base import (
    ColorArg,
    Element,
    FontSizeArg,
    FontWeightArg,
    Props,
    RadiusArg,
    SpacingArg,
    StringArg,
    StyleMap,
    ViewChild,
    _merge_props,
)


class Button(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild,
        onclick: GroupedMsg[MsgGroupT, PointerEvent, Any],
        props: Props | None = None,
        bg: ColorArg | None = None,
        fg: ColorArg | None = None,
        p: SpacingArg | None = None,
        px: SpacingArg | None = None,
        py: SpacingArg | None = None,
        radius: RadiusArg | None = None,
        border: StringArg | None = None,
        font_size: FontSizeArg | None = None,
        font_weight: FontWeightArg | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(
            props,
            bg=bg if bg is not None else "var(--fleur-comp-button-bg)",
            fg=fg if fg is not None else "var(--fleur-comp-button-fg)",
            p=p,
            px=px if px is not None else "sm",
            py=py if py is not None else "xs",
            radius=radius if radius is not None else "var(--fleur-comp-button-radius)",
            border=border if border is not None else "var(--fleur-comp-button-border)",
            font_size=font_size,
            font_weight=font_weight if font_weight is not None else "var(--fleur-comp-button-font-weight)",
            style=style,
        )
        merged["onclick"] = onclick
        super().__init__(*children, tag="button", props=merged)
