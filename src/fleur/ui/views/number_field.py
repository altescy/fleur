from typing import Unpack

from fleur.core.events import InputEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT, OptionalContextT
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
        step: int | float | Expr[int | float] = 1,
        label: String | None = None,
        name: String | None = None,
        required: bool | Expr[bool] = False,
        disabled: bool | Expr[bool] = False,
        oninput: GroupedMsg[MsgGroupT, InputEvent, OptionalContextT] | None = None,
        onchange: GroupedMsg[MsgGroupT, InputEvent, OptionalContextT] | None = None,
        decrease_label: String = "Decrease value",
        increase_label: String = "Increase value",
        props: ViewProps | None = None,
        input_props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp] = {
            "value": value,
            "min": min,
            "max": max,
            "step": step,
            "name": name,
            "required": required,
            "disabled": disabled,
        }
        if label is not None:
            attrs["aria-label"] = label
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
