from __future__ import annotations

from typing import cast

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.js.builder import json_expr
from fleur.types import JsonValue

from .base import (
    ColorArg,
    Element,
    LengthArg,
    Props,
    RadiusArg,
    SpacingArg,
    StringArg,
    StyleMap,
    StyleValue,
    ViewChild,
    _length,
    _merge_props,
)


class Grid(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        columns: int | Expr[JsonValue] | None = None,
        min_col: LengthArg | None = None,
        gap: SpacingArg | None = None,
        bg: ColorArg | None = None,
        fg: ColorArg | None = None,
        p: SpacingArg | None = None,
        px: SpacingArg | None = None,
        py: SpacingArg | None = None,
        radius: RadiusArg | None = None,
        mx: SpacingArg | None = None,
        my: SpacingArg | None = None,
        max_w: LengthArg | None = None,
        border: StringArg | None = None,
        font_family: StringArg | None = None,
        justify: StringArg | None = None,
        align: StringArg | None = None,
        style: StyleMap | None = None,
    ) -> None:
        grid_template_columns = None
        if columns is not None:
            grid_template_columns = (
                f"repeat({columns}, minmax(0, 1fr))"
                if not isinstance(columns, Expr)
                else cast(Expr[JsonValue], Expr(json_expr("repeat(")) + columns + ", minmax(0, 1fr))")
            )
        elif min_col is not None:
            min_col_value = _length(min_col)
            if min_col_value is not None:
                grid_template_columns = (
                    f"repeat(auto-fit, minmax({min_col_value}, 1fr))"
                    if not isinstance(min_col_value, Expr)
                    else cast(Expr[JsonValue], Expr(json_expr("repeat(auto-fit, minmax(")) + min_col_value + ", 1fr))")
                )

        merged = _merge_props(
            props,
            gap=gap,
            bg=bg,
            fg=fg,
            p=p,
            px=px,
            py=py,
            radius=radius,
            mx=mx,
            my=my,
            max_w=max_w,
            border=border,
            font_family=font_family,
            display="grid",
            justify=justify,
            align=align,
            style={
                **({"grid-template-columns": grid_template_columns} if grid_template_columns is not None else {}),
                **(dict(style) if style is not None else {}),
            },
        )
        super().__init__(*children, tag="div", props=merged)


class GridItem(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        col_span: int | Expr[JsonValue] | None = None,
        row_span: int | Expr[JsonValue] | None = None,
        align_self: StringArg | None = None,
        justify_self: StringArg | None = None,
        style: StyleMap | None = None,
    ) -> None:
        item_style: dict[str, StyleValue] = dict(style) if style is not None else {}
        if col_span is not None:
            item_style["grid-column"] = (
                f"span {col_span}"
                if not isinstance(col_span, Expr)
                else cast(Expr[JsonValue], Expr(json_expr("span ")) + col_span)
            )
        if row_span is not None:
            item_style["grid-row"] = (
                f"span {row_span}"
                if not isinstance(row_span, Expr)
                else cast(Expr[JsonValue], Expr(json_expr("span ")) + row_span)
            )
        if align_self is not None:
            item_style["align-self"] = align_self
        if justify_self is not None:
            item_style["justify-self"] = justify_self

        merged = _merge_props(props, style=item_style)
        super().__init__(*children, tag="div", props=merged)
