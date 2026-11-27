from typing import Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import merge_props
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Disclosure(Element[ModelT_co, MsgGroupT_co]):
    """Show or hide content with the browser's native disclosure control."""

    def __init__(
        self,
        summary: ViewChild[ModelT_co, MsgGroupT_co],
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            Element(summary, tag="summary", props={}),
            *children,
            tag="details",
            props=merge_props(props, element="disclosure", **style_args),
        )
