from typing import Literal, Unpack

from fleur.core.dom import EventMessage
from fleur.core.events import InputEvent
from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT
from fleur.core.view import ViewProp

from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .types import String, ViewStyleArgs


class Slider(Element[ModelT_co, MsgGroupT]):
    """A native range input for choosing a single number."""

    def __init__(
        self,
        *,
        value: int | float | Expr[int | float] | None = None,
        min: int | float | Expr[int | float] = 0,
        max: int | float | Expr[int | float] = 100,
        step: int | float | Expr[int | float] | Literal["any"] = 1,
        label: String | None = None,
        oninput: EventMessage[MsgGroupT, InputEvent] | None = None,
        onchange: EventMessage[MsgGroupT, InputEvent] | None = None,
        name: String | None = None,
        disabled: bool | Expr[bool] | None = None,
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp[MsgGroupT]] = {"type": "range", "min": min, "max": max, "step": step}
        if value is not None:
            attrs["value"] = value
        if label is not None:
            attrs["aria-label"] = label
        if oninput is not None:
            attrs["oninput"] = oninput
        if onchange is not None:
            attrs["onchange"] = onchange
        if name is not None:
            attrs["name"] = name
        if disabled is not None:
            attrs["disabled"] = disabled
        super().__init__(
            tag="input",
            props=extend_props(merge_props(props, element="slider", **style_args), attrs),
        )
