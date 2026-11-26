from typing import Unpack

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import ViewProp

from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .types import String, ViewStyleArgs


class Meter(Element[ModelT_co, MsgGroupT_co]):
    """A native meter for displaying a measurement within a known range."""

    def __init__(
        self,
        *,
        value: int | float | Expr[int | float],
        min: int | float | Expr[int | float] | None = None,
        max: int | float | Expr[int | float] | None = None,
        low: int | float | Expr[int | float] | None = None,
        high: int | float | Expr[int | float] | None = None,
        optimum: int | float | Expr[int | float] | None = None,
        label: String | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp] = {"value": value}
        for key, setting in (("min", min), ("max", max), ("low", low), ("high", high), ("optimum", optimum)):
            if setting is not None:
                attrs[key] = setting
        if label is not None:
            attrs["aria-label"] = label
        super().__init__(tag="meter", props=extend_props(merge_props(props, element="meter", **style_args), attrs))
