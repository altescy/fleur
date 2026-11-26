from collections.abc import Mapping
from typing import Unpack

from fleur.core.array import Array
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.object import Object
from fleur.core.types import KeyT, ModelT_co, MsgGroupT
from fleur.core.view import ViewChild

from ._utils import extend_props, merge_props
from .base import Element, ViewProps
from .input import Input
from .types import String, ViewStyleArgs


class Combobox(Element[ModelT_co, MsgGroupT]):
    """Filter a list of choices and dispatch the selected key as message context."""

    def __init__(
        self,
        options: Mapping[KeyT, String] | Expr[Mapping[KeyT, str]],
        *,
        id: String,
        label: String,
        value: KeyT | Expr[KeyT | None] | None,
        onselect: GroupedMsg[MsgGroupT, PointerEvent, KeyT],
        placeholder: String | None = None,
        empty_text: String = "No matching options.",
        disabled: bool | Expr[bool] = False,
        props: ViewProps | None = None,
        input_props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        label_id = id + "-label"
        list_id = id + "-options"

        def option(key: KeyT | Expr[KeyT], caption: String) -> Element[ModelT_co, MsgGroupT]:
            return Element(
                caption,
                tag="div",
                props={"key": key, "role": "option", "data-fleur-value": key, "onclick": onselect.bind(key)},
            )

        choices: ViewChild
        if isinstance(options, Expr):
            choices = Array.map(Object.keys(options), lambda key: option(key, options[key]))
        else:
            choices = [option(key, caption) for key, caption in options.items()]
        attrs = {
            "id": id,
            "role": "combobox",
            "aria-autocomplete": "list",
            "aria-expanded": "false",
            "aria-controls": list_id,
            "autocomplete": "off",
            "disabled": disabled,
            "value": None,
            "data-fleur-part": "combobox-input",
        }
        super().__init__(
            Element(label, tag="label", props={"id": label_id, "for": id}),
            Input(
                type="text",
                placeholder=placeholder,
                props=extend_props({} if input_props is None else input_props, attrs),
            ),
            Element(
                Element(
                    choices,
                    tag="div",
                    props={"id": list_id, "role": "listbox", "aria-labelledby": label_id},
                ),
                Element(
                    empty_text, tag="div", props={"data-fleur-part": "no-results", "role": "status", "hidden": True}
                ),
                tag="div",
                props={"data-fleur-part": "combobox-popup", "hidden": True},
            ),
            tag="div",
            props=extend_props(
                merge_props(props, element="combobox", **style_args),
                {"fleurCombobox": True, "data-fleur-value": value},
            ),
        )
