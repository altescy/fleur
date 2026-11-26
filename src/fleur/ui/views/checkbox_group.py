from collections.abc import Mapping, Sequence
from typing import Unpack

from fleur.core.array import Array
from fleur.core.events import InputEvent
from fleur.core.expr import Expr, ensure_expr
from fleur.core.msg import GroupedMsg
from fleur.core.object import Object
from fleur.core.types import KeyT, ModelT_co, MsgGroupT
from fleur.core.view import ViewChild

from ._selection import toggle_selection
from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .checkbox import CheckboxField
from .types import String, ViewStyleArgs


class CheckboxGroup(Element[ModelT_co, MsgGroupT]):
    """A labelled group of checkboxes. Each change sends the complete selection."""

    def __init__(
        self,
        options: Mapping[KeyT, String] | Expr[Mapping[KeyT, str]],
        *,
        label: String,
        value: Sequence[KeyT] | Expr[Sequence[KeyT]],
        onchange: GroupedMsg[MsgGroupT, InputEvent, Sequence[KeyT]],
        name: String | None = None,
        disabled: bool | Expr[bool] = False,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        selected = value if isinstance(value, Expr) else Expr[Sequence[KeyT]](ensure_expr(value))

        def checkbox(key: KeyT | Expr[KeyT], caption: String) -> CheckboxField[ModelT_co, MsgGroupT]:
            return CheckboxField(
                caption,
                checked=Array.includes(selected, key),
                onchange=onchange.bind(toggle_selection(selected, key)),
                name=name,
                value=key,
                props={"key": key},
            )

        choices: ViewChild
        if isinstance(options, Expr):
            choices = Array.map(Object.keys(options), lambda key: checkbox(key, options[key]))
        else:
            choices = [checkbox(key, caption) for key, caption in options.items()]
        super().__init__(
            Element(label, tag="legend", props={}),
            choices,
            tag="fieldset",
            props=extend_props(merge_props(props, element="checkbox-group", **style_args), {"disabled": disabled}),
        )
