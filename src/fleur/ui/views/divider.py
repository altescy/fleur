from __future__ import annotations

from typing import cast

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.js.builder import json_expr
from fleur.types import JsonValue

from .base import ColorArg, Element, Props, SpacingArg, _merge_props


class Divider(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *,
        props: Props | None = None,
        color: ColorArg = "var(--fleur-color-border-default)",
        my: SpacingArg | None = "sm",
    ) -> None:
        border_top = (
            f"1px solid {color}"
            if not isinstance(color, Expr)
            else cast(Expr[JsonValue], Expr(json_expr("1px solid ")) + color)
        )
        merged = _merge_props(
            props,
            my=my,
            style={
                "border": "0",
                "border-top": border_top,
                "width": "100%",
            },
        )
        super().__init__(tag="hr", props=merged)
