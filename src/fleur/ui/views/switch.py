from typing import Unpack

from fleur.core.events import InputEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT, OptionalContextT

from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .checkbox import Checkbox
from .types import String, ViewStyleArgs


class Switch(Element[ModelT_co, MsgGroupT]):
    """A labeled on/off control backed by a native checkbox."""

    def __init__(
        self,
        label: String,
        *,
        checked: bool | Expr[bool] | None = None,
        onchange: GroupedMsg[MsgGroupT, InputEvent, OptionalContextT] | None = None,
        disabled: bool | Expr[bool] | None = None,
        required: bool | Expr[bool] | None = None,
        name: String | None = None,
        value: String | None = None,
        props: ViewProps | None = None,
        input_props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        control = Element(
            Checkbox(
                checked=checked,
                onchange=onchange,
                disabled=disabled,
                required=required,
                name=name,
                value=value,
                props=extend_props({} if input_props is None else input_props, {"role": "switch"}),
                w="full",
                h="full",
            ),
            Element(tag="span", props={"data-fleur-part": "track", "aria-hidden": "true"}),
            tag="span",
            props={"data-fleur-part": "control"},
        )
        super().__init__(
            control,
            Element(label, tag="span", props={}),
            tag="label",
            props=merge_props(props, element="switch", **style_args),
        )
