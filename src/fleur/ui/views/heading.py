from typing import Literal, Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import merge_props
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Heading(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        level: Literal[1, 2, 3, 4, 5, 6],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        if type(level) is not int or not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6")
        super().__init__(*children, tag=f"h{level}", props=merge_props(props, element="heading", **style_args))
