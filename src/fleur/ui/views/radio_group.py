from collections.abc import Mapping
from typing import Unpack

from fleur.core.cond import Cond
from fleur.core.events import InputEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import KeyT, ModelT_co, MsgGroupT

from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .types import String, ViewStyleArgs


class RadioGroup(Element[ModelT_co, MsgGroupT]):
    """A labelled group of native radios. The selected option key is the message context."""

    def __init__(
        self,
        options: Mapping[KeyT, String],
        *,
        name: str,
        label: String,
        value: KeyT | Expr[KeyT],
        onselect: GroupedMsg[MsgGroupT, InputEvent, KeyT],
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        if not name:
            raise ValueError("RadioGroup requires a nonempty name to group its inputs")
        choices = (
            Element(
                Element(
                    tag="input",
                    props={
                        "type": "radio",
                        "name": name,
                        "value": key,
                        "checked": Cond.equal(value, key),
                        "onchange": onselect.bind(key),
                        "data-fleur-ui": "radio",
                    },
                ),
                caption,
                tag="label",
                props={"key": key},
            )
            for key, caption in options.items()
        )
        super().__init__(
            Element(label, tag="legend", props={}),
            *choices,
            tag="fieldset",
            props=extend_props(merge_props(props, element="radio-group", **style_args), {"role": "radiogroup"}),
        )
