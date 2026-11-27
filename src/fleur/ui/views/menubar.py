from typing import Unpack

from fleur.core.types import ModelT, MsgGroupT
from fleur.core.view import View

from ._navigation_behavior import menubar_effect
from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .menu import Menu
from .types import String, ViewStyleArgs


class Menubar(Element[ModelT, MsgGroupT]):
    """A horizontal group of action menus with one tab stop."""

    def __init__(
        self,
        *menus: Menu[ModelT, MsgGroupT],
        label: String,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            *menus,
            tag="div",
            props=extend_props(
                merge_props(props, element="menubar", **style_args),
                {"role": "menubar", "aria-label": label, **View.dom_effect(menubar_effect())},
            ),
        )
