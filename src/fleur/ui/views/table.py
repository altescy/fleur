from __future__ import annotations

from typing import Any, Unpack

from fleur.core.cond import Cond
from fleur.core.dom import EventMessage
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT, MsgGroupT_co
from fleur.types import JsonValue

from . import _utils
from .base import Element, ViewChild, ViewProps
from .button import Button
from .types import ViewStyleArgs


class Table(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(
            props,
            element="table",
            **style_args,
        )
        super().__init__(*children, tag="table", props=merged)


class TableHeader(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        super().__init__(*children, tag="thead", props=merged)


class TableBody(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        super().__init__(*children, tag="tbody", props=merged)


class TableFooter(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, **style_args)
        super().__init__(*children, tag="tfoot", props=merged)


class TableRow(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(props, element="table-row", **style_args)
        super().__init__(*children, tag="tr", props=merged)


class TableHead(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        colspan: int | Expr[int] | None = None,
        rowspan: int | Expr[int] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        normalized_style = ViewStyleArgs(**style_args)
        if "align" in style_args and "text_align" not in style_args:
            # In a table cell, `align` sets the text alignment.
            normalized_style["text_align"] = style_args["align"]
            normalized_style["align"] = None
        merged = _utils.merge_props(
            props,
            element="table-head",
            **normalized_style,
        )
        extra: dict[str, Any] = {}
        if colspan is not None:
            extra["colspan"] = colspan
        if rowspan is not None:
            extra["rowspan"] = rowspan
        merged = _utils.extend_props(merged, extra)
        super().__init__(*children, tag="th", props=merged)


class SortableTableHead(TableHead[ModelT_co, MsgGroupT]):
    """A native sort button with the sort direction exposed on the active column header."""

    def __init__(
        self,
        label: ViewChild[ModelT_co, MsgGroupT],
        *,
        active: bool | Expr[bool],
        descending: bool | Expr[bool] = False,
        onsort: EventMessage[MsgGroupT, PointerEvent],
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        direction = Cond.when(active, Cond.when(descending, "descending", "ascending"), None)
        arrow = Cond.when(active, Cond.when(descending, "↓", "↑"), "↕")
        super().__init__(
            Button(
                label,
                Element(arrow, tag="span", props={"aria-hidden": "true"}),
                onclick=onsort,
                variant="ghost",
                props={"type": "button", "data-fleur-part": "sort"},
            ),
            props=_utils.extend_props(props if props is not None else {}, {"scope": "col", "aria-sort": direction}),
            **style_args,
        )


class TableCell(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        colspan: int | Expr[JsonValue] | None = None,
        rowspan: int | Expr[JsonValue] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        normalized_style = ViewStyleArgs(**style_args)
        if "align" in style_args and "text_align" not in style_args:
            # In a table cell, `align` sets the text alignment.
            normalized_style["text_align"] = style_args["align"]
            normalized_style["align"] = None
        merged = _utils.merge_props(props, element="table-cell", **normalized_style)
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
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        merged = _utils.merge_props(
            props,
            element="table-caption",
            **style_args,
        )
        super().__init__(*children, tag="caption", props=merged)
