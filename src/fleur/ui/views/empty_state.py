from typing import Literal, Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import merge_props
from .base import Element, ViewChild, ViewProps
from .heading import Heading
from .types import String, ViewStyleArgs


class EmptyState(Element[ModelT_co, MsgGroupT_co]):
    """Describe an empty collection and offer optional next steps."""

    def __init__(
        self,
        title: String,
        description: String | None = None,
        *actions: ViewChild,
        level: Literal[1, 2, 3, 4, 5, 6] = 3,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        children: list[ViewChild] = [Heading(title, level=level, font_size="base")]
        if description is not None:
            children.append(Element(description, tag="p", props={}))
        super().__init__(*children, *actions, tag="div", props=merge_props(props, element="empty-state", **style_args))
