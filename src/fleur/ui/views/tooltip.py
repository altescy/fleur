from collections.abc import Callable, Mapping
from typing import Unpack

from fleur.core.types import ModelT, MsgGroupT
from fleur.core.view import View, ViewProp

from ._overlay_behavior import hover_panel_effect
from ._utils import merge_props
from .base import Element, ViewProps
from .types import String, ViewStyleArgs


class Tooltip(Element[ModelT, MsgGroupT]):
    """Supplemental text for a focusable control. Forward the trigger attributes to it."""

    def __init__(
        self,
        text: String,
        *,
        id: String,
        trigger: Callable[[Mapping[str, ViewProp]], View[ModelT, MsgGroupT]],
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        content = Element(text, tag="span", props=merge_props(props, element="tooltip", **style_args))
        panel = Element(
            content,
            tag="span",
            props={"id": id, "role": "tooltip", "hidden": True, "data-fleur-part": "tooltip-panel"},
        )
        super().__init__(
            trigger({"aria-describedby": id}),
            panel,
            tag="span",
            props={"data-fleur-part": "tooltip-root", **View.dom_effect(hover_panel_effect(preview=False))},
        )
