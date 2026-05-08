from __future__ import annotations

from typing import Any, Unpack

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.types import JsonValue

from . import _utils
from .base import Element, ViewChild, ViewProps
from .types import ViewStyleArgs


class Table(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        merged = _utils.set_default_style(
            merged,
            {
                "width": "100%",
                "border-collapse": "collapse",
                "caption-side": "bottom",
            },
        )
        super().__init__(*children, tag="table", props=merged)


class TableHeader(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self, *children: ViewChild, props: ViewProps | None = None, **style_args: Unpack[ViewStyleArgs]
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        super().__init__(*children, tag="thead", props=merged)


class TableBody(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self, *children: ViewChild, props: ViewProps | None = None, **style_args: Unpack[ViewStyleArgs]
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        super().__init__(*children, tag="tbody", props=merged)


class TableFooter(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self, *children: ViewChild, props: ViewProps | None = None, **style_args: Unpack[ViewStyleArgs]
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        super().__init__(*children, tag="tfoot", props=merged)


class TableRow(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        merged = _utils.set_default_style(merged, {"border-bottom": "1px solid var(--fleur-color-border-default)"})
        super().__init__(*children, tag="tr", props=merged)


class TableHead(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        colspan: int | Expr[int] | None = None,
        rowspan: int | Expr[int] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        normalized_style = (
            ViewStyleArgs(**{**style_args, "align": None, "text_align": style_args["align"]})
            if "align" in style_args and "text_align" not in style_args
            else ViewStyleArgs(**style_args)
        )
        style_overrides = ViewStyleArgs(
            p="sm",
            font_weight=600,
            fg="fg-muted",
        )
        merged = _utils.merge_props(props, **{**style_overrides, **normalized_style})
        merged = _utils.set_default_style(merged, {"vertical-align": "middle"})
        extra: dict[str, Any] = {}
        if colspan is not None:
            extra["colspan"] = colspan
        if rowspan is not None:
            extra["rowspan"] = rowspan
        merged = _utils.extend_props(merged, extra)
        super().__init__(*children, tag="th", props=merged)


class TableCell(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        colspan: int | Expr[JsonValue] | None = None,
        rowspan: int | Expr[JsonValue] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        normalized_style = (
            ViewStyleArgs(**{**style_args, "align": None, "text_align": style_args["align"]})
            if "align" in style_args and "text_align" not in style_args
            else ViewStyleArgs(**style_args)
        )
        style_overrides = ViewStyleArgs(p="sm")
        merged = _utils.merge_props(props, **{**style_overrides, **normalized_style})
        merged = _utils.set_default_style(merged, {"vertical-align": "middle"})
        extra: dict[str, Any] = {}
        if colspan is not None:
            extra["colspan"] = colspan
        if rowspan is not None:
            extra["rowspan"] = rowspan
        merged = _utils.extend_props(merged, extra)
        super().__init__(*children, tag="td", props=merged)


class TableCaption(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        style_overrides = ViewStyleArgs(p="xs", fg="fg-muted")
        merged = _utils.merge_props(props, **{**style_overrides, **style_args})
        merged = _utils.set_default_style(merged, {"text-align": "left", "caption-side": "bottom"})
        super().__init__(*children, tag="caption", props=merged)
