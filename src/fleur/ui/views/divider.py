from __future__ import annotations

from fleur.core.types import ModelT_co, MsgGroupT_co

from .base import Element, Props, SpacingValue, _merge_props


class Divider(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *,
        props: Props | None = None,
        color: str = "var(--fleur-sem-border-default)",
        my: SpacingValue | None = "sm",
    ) -> None:
        merged = _merge_props(
            props,
            my=my,
            style={
                "border": "0",
                "border-top": f"1px solid {color}",
                "width": "100%",
            },
        )
        super().__init__(tag="hr", props=merged)
