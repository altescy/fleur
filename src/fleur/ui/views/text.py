from __future__ import annotations

from typing import Unpack

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co

from . import _utils
from .base import Element, ViewProps
from .types import ViewStyleArgs


class Text(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        text: str | None | Expr[str | None],
        *,
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            text,
            tag="span",
            props=_utils.merge_props(props, element="text", **style_args),
        )
