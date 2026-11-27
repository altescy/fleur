from __future__ import annotations

from typing import Any, Unpack

from fleur.core.dom import EventMessage
from fleur.core.events import FocusEvent, InputEvent, KeyboardEvent
from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT

from . import _utils
from .base import (
    Element,
    ViewProps,
)
from .types import String, ViewStyleArgs


class Textarea(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *,
        props: ViewProps[MsgGroupT] | None = None,
        value: String | None = None,
        placeholder: String | None = None,
        rows: int | Expr[int] | None = None,
        cols: int | Expr[int] | None = None,
        oninput: EventMessage[MsgGroupT, InputEvent] | None = None,
        onchange: EventMessage[MsgGroupT, InputEvent] | None = None,
        onfocus: EventMessage[MsgGroupT, FocusEvent] | None = None,
        onblur: EventMessage[MsgGroupT, FocusEvent] | None = None,
        onkeydown: EventMessage[MsgGroupT, KeyboardEvent] | None = None,
        onkeyup: EventMessage[MsgGroupT, KeyboardEvent] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, element="textarea", **style_args)
        extra: dict[str, Any] = {}
        if value is not None:
            extra["value"] = value
        if placeholder is not None:
            extra["placeholder"] = placeholder
        if rows is not None:
            extra["rows"] = rows
        if cols is not None:
            extra["cols"] = cols
        if oninput is not None:
            extra["oninput"] = oninput
        if onchange is not None:
            extra["onchange"] = onchange
        if onfocus is not None:
            extra["onfocus"] = onfocus
        if onblur is not None:
            extra["onblur"] = onblur
        if onkeydown is not None:
            extra["onkeydown"] = onkeydown
        if onkeyup is not None:
            extra["onkeyup"] = onkeyup
        merged = _utils.extend_props(merged, extra)
        super().__init__(tag="textarea", props=merged)
