from typing import Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .disclosure import Disclosure
from .types import String, ViewStyleArgs


class Accordion(Element[ModelT_co, MsgGroupT_co]):
    """A group of accordion items with at most one open at a time."""

    def __init__(
        self,
        *items: ViewChild,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            *items,
            tag="div",
            props=extend_props(merge_props(props, element="accordion", **style_args), {"fleurAccordion": True}),
        )


class AccordionItem(Disclosure[ModelT_co, MsgGroupT_co]):
    """A native disclosure for use inside an Accordion."""

    def __init__(
        self,
        title: String,
        *children: ViewChild,
        initial_open: bool = False,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            title,
            Element(*children, tag="div", props={"data-fleur-part": "accordion-panel"}),
            props=extend_props(
                {} if props is None else props,
                {"data-fleur-part": "accordion-item", "name": None, "open": initial_open},
            ),
            **style_args,
        )
