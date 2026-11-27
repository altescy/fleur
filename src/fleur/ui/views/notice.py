from typing import Literal, TypeAlias, Unpack

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co

from ._utils import extend_props, merge_props
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs

NoticeVariant: TypeAlias = Literal["info", "success", "error"]


class Notice(Element[ModelT_co, MsgGroupT_co]):
    """An inline message with optional actions outside its live region."""

    def __init__(
        self,
        message: ViewChild[ModelT_co, MsgGroupT_co],
        *actions: ViewChild[ModelT_co, MsgGroupT_co],
        variant: NoticeVariant | Expr[NoticeVariant] = "info",
        announce: Literal["polite", "assertive", "off"] = "polite",
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        role = {"polite": "status", "assertive": "alert", "off": None}[announce]
        body = Element(message, tag="div", props={"role": role})
        merged = merge_props(props, element="notice", **style_args)
        super().__init__(body, *actions, tag="div", props=extend_props(merged, {"data-fleur-variant": variant}))
