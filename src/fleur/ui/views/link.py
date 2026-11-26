from typing import Literal, Unpack

from fleur.core.cond import Cond
from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import ViewProp

from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import String, ViewStyleArgs


class Link(Element[ModelT_co, MsgGroupT_co]):
    """A native anchor. A disabled link has no navigation or download target."""

    def __init__(
        self,
        *children: ViewChild,
        href: String,
        download: String | None = None,
        disabled: bool | Expr[bool] = False,
        variant: Literal["text", "button"] = "text",
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp] = {"href": href}
        if download is not None:
            attrs["download"] = download
        if disabled is not False:
            attrs["role"] = "link"
            attrs["href"] = Cond.when(disabled, None, href)
            attrs["aria-disabled"] = Cond.when(disabled, "true", None)
            if download is not None:
                attrs["download"] = Cond.when(disabled, None, download)
        if variant == "button":
            attrs["data-fleur-variant"] = variant
        super().__init__(
            *children, tag="a", props=extend_props(merge_props(props, element="link", **style_args), attrs)
        )
