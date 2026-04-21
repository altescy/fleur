from __future__ import annotations

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co

from .base import Color, Element, FontSize, FontWeight, Props, String, _merge_props


class Text(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        text: str | None | Expr[str | None],
        *,
        props: Props | None = None,
        fg: Color | None = None,
        bg: Color | None = None,
        font_size: FontSize | None = None,
        font_weight: FontWeight | None = None,
        font_family: String | None = None,
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
