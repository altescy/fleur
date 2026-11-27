from typing import Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import merge_props
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Card(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(*children, tag="div", props=merge_props(props, element="card", **style_args))
