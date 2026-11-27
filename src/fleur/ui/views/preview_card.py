from typing import Unpack

from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import View

from ._overlay_behavior import hover_panel_effect
from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .link import Link
from .types import ViewStyleArgs


class PreviewCard(Element[ModelT_co, MsgGroupT_co]):
    """A visual preview of a link destination, shown on hover or keyboard focus."""

    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        trigger: Link[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        content = Element(
            *children,
            tag="span",
            props=extend_props(merge_props(props, element="preview-card", **style_args), {"inert": True}),
        )
        panel = Element(
            content,
            tag="span",
            props={"hidden": True, "aria-hidden": "true", "data-fleur-part": "preview-card-panel"},
        )
        super().__init__(
            trigger,
            panel,
            tag="span",
            props={"data-fleur-part": "preview-card-root", **View.dom_effect(hover_panel_effect(preview=True))},
        )
