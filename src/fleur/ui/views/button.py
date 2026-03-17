from __future__ import annotations

from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT
from fleur.core.view import View
from fleur.types import JsonValue

from .base import Element, LengthValue, Props, RadiusValue, RawColor, SpacingValue, StyleMap, _merge_props


class Button(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: str | View[ModelT_co, MsgGroupT] | Expr[JsonValue | View[ModelT_co, MsgGroupT]],
        onclick: GroupedMsg[MsgGroupT, object],
        props: Props | None = None,
        bg: RawColor | str | None = None,
        fg: RawColor | str | None = None,
        p: SpacingValue | None = None,
        px: SpacingValue | None = None,
        py: SpacingValue | None = None,
        radius: RadiusValue | None = None,
        border: str | None = None,
        font_size: LengthValue | None = None,
        font_weight: int | str | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(
            props,
            bg=bg or "var(--fleur-comp-button-bg)",
            fg=fg or "var(--fleur-comp-button-fg)",
            p=p,
            px=px or "sm",
            py=py or "xs",
            radius=radius or "var(--fleur-comp-button-radius)",
            border=border or "var(--fleur-comp-button-border)",
            font_size=font_size,
            font_weight=font_weight or "var(--fleur-comp-button-font-weight)",
            style=style,
        )
        merged["onclick"] = onclick
        super().__init__(*children, tag="button", props=merged)
