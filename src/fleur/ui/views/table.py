from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, cast

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.types import JsonValue

from .base import (
    ColorArg,
    Element,
    FontWeightArg,
    LengthArg,
    Props,
    RadiusArg,
    SpacingArg,
    StringArg,
    StyleMap,
    StyleValue,
    ViewChild,
    _merge_props,
)

TableAlign = Literal["left", "center", "right", "justify", "start", "end"]


def _style_props(merged: Mapping[str, object]) -> dict[str, StyleValue]:
    existing_style = merged.get("style")
    return (
        {key: cast(StyleValue, value) for key, value in existing_style.items()}
        if isinstance(existing_style, Mapping)
        else {}
    )


class Table(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        bg: ColorArg | None = None,
        fg: ColorArg | None = None,
        p: SpacingArg | None = None,
        radius: RadiusArg | None = None,
        w: LengthArg | None = None,
        max_w: LengthArg | None = None,
        border: StringArg | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(
            props,
            bg=bg,
            fg=fg,
            p=p,
            radius=radius,
            w=w,
            max_w=max_w,
            border=border,
            style=style,
        )
        style_props = _style_props(merged)
        style_props.setdefault("width", "100%")
        style_props.setdefault("border-collapse", "collapse")
        style_props.setdefault("caption-side", "bottom")
        merged["style"] = style_props
        super().__init__(*children, tag="table", props=merged)


class TableHeader(Element[ModelT_co, MsgGroupT_co]):
    def __init__(self, *children: ViewChild, props: Props | None = None, style: StyleMap | None = None) -> None:
        merged = _merge_props(props, style=style)
        super().__init__(*children, tag="thead", props=merged)


class TableBody(Element[ModelT_co, MsgGroupT_co]):
    def __init__(self, *children: ViewChild, props: Props | None = None, style: StyleMap | None = None) -> None:
        merged = _merge_props(props, style=style)
        super().__init__(*children, tag="tbody", props=merged)


class TableFooter(Element[ModelT_co, MsgGroupT_co]):
    def __init__(self, *children: ViewChild, props: Props | None = None, style: StyleMap | None = None) -> None:
        merged = _merge_props(props, style=style)
        super().__init__(*children, tag="tfoot", props=merged)


class TableRow(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        bg: ColorArg | None = None,
        fg: ColorArg | None = None,
        border: StringArg | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(props, bg=bg, fg=fg, border=border, style=style)
        style_props = _style_props(merged)
        style_props.setdefault("border-bottom", "1px solid var(--fleur-color-border-default)")
        merged["style"] = style_props
        super().__init__(*children, tag="tr", props=merged)


class TableHead(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        align: TableAlign | Expr[TableAlign] | None = None,
        colspan: int | Expr[int] | None = None,
        rowspan: int | Expr[int] | None = None,
        p: SpacingArg | None = "sm",
        font_weight: FontWeightArg | None = 600,
        fg: ColorArg | None = "fg-muted",
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(props, p=p, font_weight=font_weight, fg=fg, style=style)
        style_props = _style_props(merged)
        if align is not None:
            style_props["text-align"] = align
        style_props.setdefault("vertical-align", "middle")
        merged["style"] = style_props
        if colspan is not None:
            merged["colspan"] = colspan
        if rowspan is not None:
            merged["rowspan"] = rowspan
        super().__init__(*children, tag="th", props=merged)


class TableCell(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        align: TableAlign | Expr[TableAlign] | None = None,
        colspan: int | Expr[JsonValue] | None = None,
        rowspan: int | Expr[JsonValue] | None = None,
        p: SpacingArg | None = "sm",
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(props, p=p, style=style)
        style_props = _style_props(merged)
        if align is not None:
            style_props["text-align"] = align
        style_props.setdefault("vertical-align", "middle")
        merged["style"] = style_props
        if colspan is not None:
            merged["colspan"] = colspan
        if rowspan is not None:
            merged["rowspan"] = rowspan
        super().__init__(*children, tag="td", props=merged)


class TableCaption(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        props: Props | None = None,
        p: SpacingArg | None = "xs",
        fg: ColorArg | None = "fg-muted",
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(props, p=p, fg=fg, style=style)
        style_props = _style_props(merged)
        style_props.setdefault("text-align", "left")
        style_props.setdefault("caption-side", "bottom")
        merged["style"] = style_props
        super().__init__(*children, tag="caption", props=merged)
