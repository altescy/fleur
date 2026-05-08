from __future__ import annotations

from typing import Unpack

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.js.builder import json_expr

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
        *children: ViewChild,
        props: ViewProps | None = None,
        columns: int | Expr[int] | None = None,
        min_col: Length | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        grid_template_columns = None
        if columns is not None:
            grid_template_columns = (
                f"repeat({columns}, minmax(0, 1fr))"
                if not isinstance(columns, Expr)
                else Expr[str](json_expr("repeat(")) + columns + ", minmax(0, 1fr))"
            )
        elif min_col is not None:
            if min_col is not None:
                grid_template_columns = (
                    "repeat(auto-fit, minmax(" + min_col + ", 1fr))"
                    if isinstance(min_col, Expr)
                    else f"repeat(auto-fit, minmax({min_col}, 1fr))"
                )

        base_style = style_args.get("style")
        style_overrides = ViewStyleArgs(display="grid")
        merged = _utils.merge_props(
            props,
            **{
                **style_args,
                **style_overrides,
                "style": {
                    **({"grid-template-columns": grid_template_columns} if grid_template_columns is not None else {}),
                    **(dict(base_style) if base_style is not None else {}),
                },
            },
        )
        super().__init__(*children, tag="div", props=merged)


class GridItem(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: ViewProps | None = None,
        col_span: int | None | Expr[int] = None,
        row_span: int | None | Expr[int] = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        item_style: dict[str, Style] = {}
        if col_span is not None:
            item_style["grid-column"] = (
                f"span {col_span}" if not isinstance(col_span, Expr) else Expr[str](json_expr("span ")) + col_span
            )
        if row_span is not None:
            item_style["grid-row"] = (
                f"span {row_span}" if not isinstance(row_span, Expr) else Expr[str](json_expr("span ")) + row_span
            )
        style_override = dict(style_args.get("style") or {})
        style_override.update(item_style)
        merged = _utils.merge_props(props, **{**style_args, "style": style_override or None})
        super().__init__(*children, tag="div", props=merged)
