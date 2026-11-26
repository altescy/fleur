from __future__ import annotations

from typing import Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co

from . import _utils
from .base import Element, ViewProps
from .types import Color, ViewStyleArgs


class Divider(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *,
        props: ViewProps | None = None,
        color: Color | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(
            props,
            element="divider",
            layout={"--fleur-local-divider-color": _utils.color_value(color)} if color is not None else None,
            **style_args,
        )
        if "my" in style_args and style_args["my"] is None:
            merged = _utils.extend_props(merged, {"data-fleur-divider-flush": ""})
        super().__init__(tag="hr", props=merged)
