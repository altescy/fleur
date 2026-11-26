from __future__ import annotations

from typing import Any, Unpack, cast

from fleur.core.events import FocusEvent, InputEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from . import _utils
from .base import Element, ViewProps
from .types import String, ViewStyleArgs


class Checkbox(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *,
        props: ViewProps | None = None,
        checked: bool | Expr[bool] | None = None,
        value: String | None = None,
        name: String | None = None,
        disabled: bool | Expr[bool] | None = None,
        required: bool | Expr[bool] | None = None,
        oninput: GroupedMsg[MsgGroupT, InputEvent, Any] | None = None,
        onchange: GroupedMsg[MsgGroupT, InputEvent, Any] | None = None,
        onfocus: GroupedMsg[MsgGroupT, FocusEvent, Any] | None = None,
        onblur: GroupedMsg[MsgGroupT, FocusEvent, Any] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(
            props,
            defaults={
                "width": "1rem",
                "height": "1rem",
                "accent-color": "var(--fleur-color-accent-solid-bg)",
            },
            **style_args,
        )
        extra: dict[str, Any] = {"type": "checkbox"}
        if checked is not None:
            extra["checked"] = cast(Any, checked)
        if value is not None:
            extra["value"] = value
        if name is not None:
            extra["name"] = name
        if disabled is not None:
            extra["disabled"] = cast(Any, disabled)
        if required is not None:
            extra["required"] = cast(Any, required)
        if oninput is not None:
            extra["oninput"] = oninput
        if onchange is not None:
            extra["onchange"] = onchange
        if onfocus is not None:
            extra["onfocus"] = onfocus
        if onblur is not None:
            extra["onblur"] = onblur
        merged = _utils.extend_props(merged, extra)
        super().__init__(tag="input", props=merged)
