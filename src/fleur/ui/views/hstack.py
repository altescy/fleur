from __future__ import annotations

from typing import Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co

from . import _utils
from .base import (
    Element,
    ViewChild,
    ViewProps,
)
from .types import ViewStyleArgs


class HStack(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        style_overrides = ViewStyleArgs(
            display="flex",
            flex_direction="row",
        )
        merged = _utils.merge_props(
            props,
            **{**style_args, **style_overrides},
        )
        super().__init__(*children, tag="div", props=merged)
