from __future__ import annotations

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.js.builder import json_expr

from . import _utils
from .base import Element, ViewProps
from .types import Color, Spacing


class Divider(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *,
        props: ViewProps | None = None,
        color: Color = "var(--fleur-color-border-default)",
        my: Spacing | None = "sm",
    ) -> None:
        border_top = f"1px solid {color}" if not isinstance(color, Expr) else Expr[str](json_expr("1px solid ")) + color
        merged = _utils.merge_props(
            props,
            my=my,
            style={
                "border": "0",
                "border-top": border_top,
                "width": "100%",
            },
        )
        super().__init__(tag="hr", props=merged)
