from __future__ import annotations

from typing import Any, Unpack, cast

from fleur.core.events import PointerEvent
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT

from . import _utils
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Button(Element[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: ViewChild,
        onclick: GroupedMsg[MsgGroupT, PointerEvent, Any] | None = None,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged_style_args = cast(ViewStyleArgs, dict(style_args))
        merged_style_args.setdefault("bg", "var(--fleur-comp-button-bg)")
        merged_style_args.setdefault("fg", "var(--fleur-comp-button-fg)")
        merged_style_args.setdefault("px", "sm")
        merged_style_args.setdefault("py", "xs")
        merged_style_args.setdefault("radius", "var(--fleur-comp-button-radius)")
        merged_style_args.setdefault("border", "var(--fleur-comp-button-border)")
        merged_style_args.setdefault("font_weight", "var(--fleur-comp-button-font-weight)")
        merged = _utils.merge_props(
            props,
            **merged_style_args,
        )
        if onclick is not None:
            merged = _utils.extend_props(merged, {"onclick": onclick})
        super().__init__(*children, tag="button", props=merged)
