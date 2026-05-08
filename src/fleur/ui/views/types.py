from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, TypedDict

from typing_extensions import TypeAlias

from fleur.core.expr import Expr

_ColorKeyword: TypeAlias = Literal[
    "black",
    "white",
    "red",
    "green",
    "blue",
    "yellow",
    "orange",
    "purple",
    "pink",
    "gray",
    "grey",
    "brown",
    "teal",
    "cyan",
    "magenta",
    "transparent",
    "currentColor",
    "inherit",
]

_String: TypeAlias = str
_Integer: TypeAlias = int
_Color: TypeAlias = _ColorKeyword | str
_Spacing: TypeAlias = int | float | str
_Radius: TypeAlias = int | float | str
_Length: TypeAlias = int | float | str
_FontSize: TypeAlias = int | float | str
_FontWeight: TypeAlias = int | str
_Style: TypeAlias = int | float | str
_Display: TypeAlias = Literal["block", "inline", "inline-block", "flex", "inline-flex", "grid", "inline-grid", "none"]
_FlexDirection: TypeAlias = Literal["row", "column", "row-reverse", "column-reverse"]
_FlexWrap: TypeAlias = Literal["nowrap", "wrap", "wrap-reverse"]
_JustifyContent: TypeAlias = Literal[
    "flex-start",
    "flex-end",
    "center",
    "space-between",
    "space-around",
    "space-evenly",
]
_AlignItems: TypeAlias = Literal["stretch", "flex-start", "flex-end", "center", "baseline"]

String: TypeAlias = _String | Expr[_String]
Integer: TypeAlias = _Integer | Expr[_Integer]
Color: TypeAlias = _Color | Expr[_Color]
RawColor: TypeAlias = Color
Style: TypeAlias = _Style | Expr[_Style]
StyleMap: TypeAlias = Mapping[str, Style]
Spacing: TypeAlias = _Spacing | Expr[_Spacing]
Radius: TypeAlias = _Radius | Expr[_Radius]
Length: TypeAlias = _Length | Expr[_Length]
FontSize: TypeAlias = _FontSize | Expr[_FontSize]
FontWeight: TypeAlias = _FontWeight | Expr[_FontWeight]
Display: TypeAlias = _Display | Expr[_Display]
FlexDirection: TypeAlias = _FlexDirection | Expr[_FlexDirection]
FlexWrap: TypeAlias = _FlexWrap | Expr[_FlexWrap]
JustifyContent: TypeAlias = _JustifyContent | Expr[_JustifyContent]
AlignItems: TypeAlias = _AlignItems | Expr[_AlignItems]


class ViewStyleArgs(TypedDict, total=False):
    bg: Color | None
    fg: Color | None
    p: Spacing | None
    px: Spacing | None
    py: Spacing | None
    pt: Spacing | None
    pr: Spacing | None
    pb: Spacing | None
    pl: Spacing | None
    mx: Spacing | None
    my: Spacing | None
    mt: Spacing | None
    mr: Spacing | None
    mb: Spacing | None
    ml: Spacing | None
    w: Length | None
    h: Length | None
    radius: Radius | None
    min_w: Length | None
    max_w: Length | None
    border: String | None
    font_size: FontSize | None
    font_weight: FontWeight | None
    font_family: String | None
    display: String | None
    flex_direction: FlexDirection | None
    flex_wrap: FlexWrap | None
    gap: Spacing | None
    justify: String | None
    align: String | None
    text_align: String | None
    align_self: String | None
    justify_self: String | None
    style: StyleMap | None
