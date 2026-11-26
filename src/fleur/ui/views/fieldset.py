from typing import Unpack

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import String, ViewStyleArgs


class Fieldset(Element[ModelT_co, MsgGroupT_co]):
    """A named group of native form controls with optional group-wide disabling."""

    def __init__(
        self,
        *children: ViewChild,
        label: String,
        disabled: bool | Expr[bool] = False,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        super().__init__(
            Element(label, tag="legend", props={}),
            *children,
            tag="fieldset",
            props=extend_props(merge_props(props, element="fieldset", **style_args), {"disabled": disabled}),
        )
