from typing import Literal, Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import View

from ._navigation_behavior import toolbar_effect
from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import String, ViewStyleArgs


class Toolbar(Element[ModelT_co, MsgGroupT_co]):
    """A labelled group of buttons and links with one tab stop."""

    def __init__(
        self,
        *children: ViewChild,
        label: String,
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            *children,
            tag="div",
            props=extend_props(
                merge_props(props, element="toolbar", **style_args),
                {
                    "role": "toolbar",
                    "aria-label": label,
                    "aria-orientation": orientation,
                    **View.dom_effect(toolbar_effect()),
                },
            ),
        )
