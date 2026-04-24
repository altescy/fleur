from __future__ import annotations

from typing import Any

from fleur.core.events import PointerEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from .base import (
    Color,
    Element,
    FontSize,
    FontWeight,
    Radius,
    Spacing,
    String,
    StyleMap,
    ViewChild,
    ViewProps,
    _merge_props,
)


class Button(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild,
        onclick: GroupedMsg[MsgGroupT, PointerEvent, Any],
        props: ViewProps | None = None,
        bg: Color | None = None,
        fg: Color | None = None,
        p: Spacing | None = None,
        px: Spacing | None = None,
        py: Spacing | None = None,
        radius: Radius | None = None,
        border: String | None = None,
        font_size: FontSize | None = None,
        font_weight: FontWeight | None = None,
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
