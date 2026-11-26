from typing import Unpack

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .types import String, ViewStyleArgs


class Avatar(Element[ModelT_co, MsgGroupT_co]):
    """A person's image with a fallback and a stable accessible name."""

    def __init__(
        self,
        *,
        name: String | None,
        fallback: String,
        src: str | Expr[str | None] | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            Element(fallback, tag="span", props={"data-fleur-part": "avatar-fallback", "aria-hidden": "true"}),
            Element(
                tag="img",
                props={
                    "src": src,
                    "alt": "",
                    "aria-hidden": "true",
                    "hidden": True,
                    "data-fleur-part": "avatar-image",
                },
            ),
            tag="span",
            props=extend_props(
                merge_props(props, element="avatar", **style_args),
                {
                    "fleurAvatar": True,
                    "role": "img" if name is not None else None,
                    "aria-label": name,
                    "aria-hidden": "true" if name is None else None,
                },
            ),
        )
