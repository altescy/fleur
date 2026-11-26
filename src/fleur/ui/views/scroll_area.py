from typing import Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import String, ViewStyleArgs


class ScrollArea(Element[ModelT_co, MsgGroupT_co]):
    """A labelled, keyboard-focusable viewport that uses native scrolling."""

    def __init__(
        self,
        *children: ViewChild,
        label: String,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            *children,
            tag="div",
            props=extend_props(
                merge_props(props, element="scroll-area", **style_args),
                {"role": "region", "aria-label": label, "tabindex": 0},
            ),
        )
