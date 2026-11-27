from typing import Literal, Unpack

from fleur.core.dom import EventMessage
from fleur.core.events import InputEvent
from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT
from fleur.core.view import View, ViewProp

from ._native_behavior import number_field_effect
from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .button import Button
from .input import Input
from .types import String, ViewStyleArgs


class NumberField(Element[ModelT_co, MsgGroupT]):
    """A native numeric input with buttons to step the value."""

    def __init__(
        self,
        *,
        value: str | int | float | Expr[str | int | float] | None = None,
        min: int | float | Expr[int | float] | None = None,
        max: int | float | Expr[int | float] | None = None,
        step: int | float | Expr[int | float] | Literal["any"] | None = None,
        label: String | None = None,
        name: String | None = None,
        required: bool | Expr[bool] | None = None,
        disabled: bool | Expr[bool] | None = None,
        oninput: EventMessage[MsgGroupT, InputEvent] | None = None,
        onchange: EventMessage[MsgGroupT, InputEvent] | None = None,
        decrease_label: String = "Decrease value",
        increase_label: String = "Increase value",
        props: ViewProps[MsgGroupT] | None = None,
        input_props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        # Arguments left as None keep the corresponding attribute from `input_props`.
        given: dict[str, ViewProp[MsgGroupT] | None] = {
            "value": value,
            "min": min,
            "max": max,
            "step": step,
            "name": name,
            "required": required,
            "disabled": disabled,
            "aria-label": label,
        }
        attrs: dict[str, ViewProp[MsgGroupT]] = {key: prop for key, prop in given.items() if prop is not None}
        super().__init__(
            Input(
                type="number",
                oninput=oninput,
                onchange=onchange,
                props=extend_props({} if input_props is None else input_props, attrs),
            ),
            Button("−", variant="ghost", props={"type": "button", "aria-label": decrease_label}),
            Button("+", variant="ghost", props={"type": "button", "aria-label": increase_label}),
            tag="div",
            props=extend_props(
                merge_props(props, element="number-field", **style_args), View.dom_effect(number_field_effect())
            ),
        )
