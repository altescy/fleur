from __future__ import annotations

from fleur.core.types import ModelT_co, MsgGroupT_co

from .base import (
    Element,
    LengthValue,
    Props,
    RadiusValue,
    RawColor,
    SpacingValue,
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
        columns: int | None = None,
        min_col: LengthValue | None = None,
        gap: SpacingValue | None = None,
        bg: RawColor | str | None = None,
        fg: RawColor | str | None = None,
        p: SpacingValue | None = None,
        px: SpacingValue | None = None,
        py: SpacingValue | None = None,
        radius: RadiusValue | None = None,
        mx: SpacingValue | None = None,
        my: SpacingValue | None = None,
        max_w: LengthValue | None = None,
        border: str | None = None,
        font_family: str | None = None,
        justify: str | None = None,
        align: str | None = None,
        style: StyleMap | None = None,
    ) -> None:
        grid_template_columns = None
        if columns is not None:
            grid_template_columns = f"repeat({columns}, minmax(0, 1fr))"
        elif min_col is not None:
            min_col_value = _length(min_col)
            if min_col_value is not None:
                grid_template_columns = f"repeat(auto-fit, minmax({min_col_value}, 1fr))"

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
        col_span: int | None = None,
        row_span: int | None = None,
        align_self: str | None = None,
        justify_self: str | None = None,
        style: StyleMap | None = None,
    ) -> None:
        item_style: dict[str, StyleValue] = dict(style) if style is not None else {}
        if col_span is not None:
            item_style["grid-column"] = f"span {col_span}"
        if row_span is not None:
            item_style["grid-row"] = f"span {row_span}"
        if align_self is not None:
            item_style["align-self"] = align_self
        if justify_self is not None:
            item_style["justify-self"] = justify_self

        merged = _merge_props(props, style=item_style)
        super().__init__(*children, tag="div", props=merged)
