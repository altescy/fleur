from typing import Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import View

from ._navigation_behavior import navigation_menu_effect
from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .link import Link
from .types import String, ViewStyleArgs


class NavigationMenuGroup(Element[ModelT_co, MsgGroupT_co]):
    """A button and its expandable list of navigation links."""

    def __init__(
        self,
        title: String,
        *links: Link[ModelT_co, MsgGroupT_co],
        id: str,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            Element(
                title,
                tag="button",
                props={
                    "type": "button",
                    "aria-expanded": "false",
                    "aria-controls": id,
                    "data-fleur-part": "navigation-trigger",
                },
            ),
            Element(
                *(Element(link, tag="li", props={}) for link in links),
                tag="ul",
                props={"id": id, "hidden": True, "data-fleur-part": "navigation-links"},
            ),
            tag="li",
            props=extend_props(merge_props(props, **style_args), {"key": id}),
        )


class NavigationMenu(Element[ModelT_co, MsgGroupT_co]):
    """A navigation landmark with expandable groups of native links."""

    def __init__(
        self,
        *groups: NavigationMenuGroup[ModelT_co, MsgGroupT_co],
        label: String,
        auto_close: bool = True,
        multiple: bool = False,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            Element(*groups, tag="ul", props={"data-fleur-part": "navigation-groups"}),
            tag="nav",
            props=extend_props(
                merge_props(props, element="navigation-menu", **style_args),
                {
                    "aria-label": label,
                    "data-fleur-keep-open": not auto_close,
                    "data-fleur-multiple": multiple,
                    **View.dom_effect(navigation_menu_effect()),
                },
            ),
        )
