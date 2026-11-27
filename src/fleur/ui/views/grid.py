from __future__ import annotations

from typing import Unpack

from fleur.core.expr import Expr, string
from fleur.core.types import ModelT_co, MsgGroupT_co

from . import _utils
from .base import (
    Element,
    ViewChild,
    ViewProps,
)
from .types import Length, Style, ViewStyleArgs


class Grid(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        columns: int | Expr[int] | None = None,
        min_col: Length | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        grid_template_columns = None
        if columns is not None:
            grid_template_columns = (
                f"repeat({columns}, minmax(0, 1fr))"
                if not isinstance(columns, Expr)
                else string("repeat(") + columns + ", minmax(0, 1fr))"
            )
        elif min_col is not None:
            size = _utils.scale_value("space", min_col)
            grid_template_columns = "repeat(auto-fit, minmax(" + size + ", 1fr))"

        merged = _utils.merge_props(
            props,
            element="grid",
            layout={"grid-template-columns": grid_template_columns} if grid_template_columns is not None else {},
            **style_args,
        )
        super().__init__(*children, tag="div", props=merged)


class GridItem(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        props: ViewProps[MsgGroupT_co] | None = None,
        col_span: int | None | Expr[int] = None,
        row_span: int | None | Expr[int] = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        item_style: dict[str, Style] = {}
        if col_span is not None:
            item_style["grid-column"] = (
                f"span {col_span}" if not isinstance(col_span, Expr) else string("span ") + col_span
            )
        if row_span is not None:
            item_style["grid-row"] = (
                f"span {row_span}" if not isinstance(row_span, Expr) else string("span ") + row_span
            )
        merged = _utils.merge_props(props, element="grid-item", layout=item_style, **style_args)
        super().__init__(*children, tag="div", props=merged)
