from typing import Unpack

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import ViewProp

from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .types import String, ViewStyleArgs


class Progress(Element[ModelT_co, MsgGroupT_co]):
    """A native progress bar. An absent value represents an unknown fraction."""

    def __init__(
        self,
        *,
        value: int | float | Expr[int | float | None] | None = None,
        max: int | float | Expr[int | float] | None = None,
        label: String | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp] = {}
        if max is not None:
            attrs["max"] = max
        if value is not None:
            attrs["value"] = value
        if label is not None:
            attrs["aria-label"] = label
        super().__init__(
            tag="progress", props=extend_props(merge_props(props, element="progress", **style_args), attrs)
        )
