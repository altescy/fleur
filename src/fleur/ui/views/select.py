from typing import Unpack

from fleur.core.events import InputEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT, MsgGroupT_co, OptionalContextT
from fleur.core.view import ViewProp

from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import String, ViewStyleArgs


class Select(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild,
        value: String | None = None,
        onchange: GroupedMsg[MsgGroupT, InputEvent, OptionalContextT] | None = None,
        name: String | None = None,
        disabled: bool | Expr[bool] | None = None,
        required: bool | Expr[bool] | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = merge_props(props, element="select", **style_args)
        attrs: dict[str, ViewProp] = {}
        if value is not None:
            attrs["value"] = value
        if onchange is not None:
            attrs["onchange"] = onchange
        if name is not None:
            attrs["name"] = name
        if disabled is not None:
            attrs["disabled"] = disabled
        if required is not None:
            attrs["required"] = required
        super().__init__(*children, tag="select", props=extend_props(merged, attrs))


class Option(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        label: String,
        *,
        value: String | None = None,
        disabled: bool | Expr[bool] | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp] = {}
        if value is not None:
            attrs["value"] = value
        if disabled is not None:
            attrs["disabled"] = disabled
        super().__init__(label, tag="option", props=extend_props(merge_props(props, **style_args), attrs))
