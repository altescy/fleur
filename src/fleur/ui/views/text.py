from __future__ import annotations

from fleur.core.types import ModelT_co, MsgGroupT_co

from .base import Element, LengthValue, Props, _merge_props


class Text(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        text: str,
        *,
        props: Props | None = None,
        fg: str | None = None,
        bg: str | None = None,
        font_size: LengthValue | None = None,
        font_weight: int | str | None = None,
        font_family: str | None = None,
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
