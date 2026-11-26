from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Annotated, Literal, NamedTuple, TypedDict

from typing_extensions import TypeAlias

from fleur.core.cond import Cond
from fleur.core.expr import Expr, ensure_expr
from fleur.ui.themes import ThemeColorName, ThemeFontSizeName, ThemeRadiusName, ThemeSpaceName


@dataclass(frozen=True, slots=True)
class CssValue:
    value: str | Expr[str]


def css(value: str | Expr[str]) -> CssValue:
    """Pass a literal or reactive CSS value to a token-aware shorthand."""
    return CssValue(value)


ColorName: TypeAlias = ThemeColorName | Literal["transparent"]


class Background:
    @staticmethod
    def when(condition: bool | Expr[bool], yes: ColorName, no: ColorName) -> Expr[ColorName]:
        """Select a named color without widening the branches to arbitrary strings."""
        return Cond.when(condition, Expr[ColorName](ensure_expr(yes)), Expr[ColorName](ensure_expr(no)))


_String: TypeAlias = str
_Integer: TypeAlias = int
_Spacing: TypeAlias = int | float | ThemeSpaceName
_Dimension: TypeAlias = _Spacing | Literal["full", "fit", "1/2", "1/3", "2/3", "1/4", "3/4"]
_Margin: TypeAlias = _Spacing | Literal["auto"]
_Overflow: TypeAlias = Literal["visible", "hidden", "clip", "scroll", "auto"]
_WhiteSpace: TypeAlias = Literal["normal", "nowrap", "pre", "pre-wrap", "pre-line", "break-spaces"]
_OverflowWrap: TypeAlias = Literal["normal", "break-word", "anywhere"]
_Radius: TypeAlias = int | float | ThemeRadiusName
_FontSize: TypeAlias = int | float | ThemeFontSizeName
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
Color: TypeAlias = ColorName | Expr[ColorName] | CssValue
RawColor: TypeAlias = CssValue
Style: TypeAlias = _Style | Expr[_Style]
StyleMap: TypeAlias = Mapping[str, Style]
Spacing: TypeAlias = _Spacing | Expr[_Spacing] | CssValue
Radius: TypeAlias = _Radius | Expr[_Radius] | CssValue
Length: TypeAlias = Spacing
Dimension: TypeAlias = _Dimension | Expr[_Dimension] | CssValue
Margin: TypeAlias = _Margin | Expr[_Margin] | CssValue
Overflow: TypeAlias = _Overflow | Expr[_Overflow]
WhiteSpace: TypeAlias = _WhiteSpace | Expr[_WhiteSpace]
OverflowWrap: TypeAlias = _OverflowWrap | Expr[_OverflowWrap]
FontSize: TypeAlias = _FontSize | Expr[_FontSize] | CssValue
FontWeight: TypeAlias = _FontWeight | Expr[_FontWeight]
Display: TypeAlias = _Display | Expr[_Display]
FlexDirection: TypeAlias = _FlexDirection | Expr[_FlexDirection]
FlexWrap: TypeAlias = _FlexWrap | Expr[_FlexWrap]
JustifyContent: TypeAlias = _JustifyContent | Expr[_JustifyContent]
AlignItems: TypeAlias = _AlignItems | Expr[_AlignItems]
StyleTransform: TypeAlias = Literal[
    "color", "space", "margin", "radius", "length", "font_size", "font_weight", "identity"
]
StyleTransformValue: TypeAlias = (
    Color | Dimension | Margin | Radius | FontSize | FontWeight | String | FlexDirection | FlexWrap | None
)


class StyleField(NamedTuple):
    css_props: tuple[str, ...]
    transform: StyleTransform


class ViewStyleArgs(TypedDict, total=False):
    bg: Annotated[Color | None, StyleField(("--fleur-local-bg",), "color")]
    fg: Annotated[Color | None, StyleField(("color",), "color")]
    p: Annotated[Spacing | None, StyleField(("padding",), "space")]
    px: Annotated[Spacing | None, StyleField(("padding-left", "padding-right"), "space")]
    py: Annotated[Spacing | None, StyleField(("padding-top", "padding-bottom"), "space")]
    pt: Annotated[Spacing | None, StyleField(("padding-top",), "space")]
    pr: Annotated[Spacing | None, StyleField(("padding-right",), "space")]
    pb: Annotated[Spacing | None, StyleField(("padding-bottom",), "space")]
    pl: Annotated[Spacing | None, StyleField(("padding-left",), "space")]
    mx: Annotated[Margin | None, StyleField(("margin-left", "margin-right"), "margin")]
    my: Annotated[Margin | None, StyleField(("margin-top", "margin-bottom"), "margin")]
    mt: Annotated[Margin | None, StyleField(("margin-top",), "margin")]
    mr: Annotated[Margin | None, StyleField(("margin-right",), "margin")]
    mb: Annotated[Margin | None, StyleField(("margin-bottom",), "margin")]
    ml: Annotated[Margin | None, StyleField(("margin-left",), "margin")]
    w: Annotated[Dimension | None, StyleField(("width",), "length")]
    h: Annotated[Dimension | None, StyleField(("height",), "length")]
    radius: Annotated[Radius | None, StyleField(("border-radius",), "radius")]
    min_w: Annotated[Dimension | None, StyleField(("min-width",), "length")]
    max_w: Annotated[Dimension | None, StyleField(("max-width",), "length")]
    min_h: Annotated[Dimension | None, StyleField(("min-height",), "length")]
    max_h: Annotated[Dimension | None, StyleField(("max-height",), "length")]
    overflow_x: Annotated[Overflow | None, StyleField(("overflow-x",), "identity")]
    overflow_y: Annotated[Overflow | None, StyleField(("overflow-y",), "identity")]
    border: Annotated[String | None, StyleField(("border",), "identity")]
    box_shadow: Annotated[String | None, StyleField(("box-shadow",), "identity")]
    font_size: Annotated[FontSize | None, StyleField(("font-size",), "font_size")]
    font_weight: Annotated[FontWeight | None, StyleField(("font-weight",), "font_weight")]
    font_family: Annotated[String | None, StyleField(("font-family",), "identity")]
    display: Annotated[Display | None, StyleField(("display",), "identity")]
    flex_direction: Annotated[FlexDirection | None, StyleField(("flex-direction",), "identity")]
    flex_wrap: Annotated[FlexWrap | None, StyleField(("flex-wrap",), "identity")]
    gap: Annotated[Spacing | None, StyleField(("gap",), "space")]
    justify: Annotated[String | None, StyleField(("justify-content",), "identity")]
    align: Annotated[String | None, StyleField(("align-items",), "identity")]
    text_align: Annotated[String | None, StyleField(("text-align",), "identity")]
    white_space: Annotated[WhiteSpace | None, StyleField(("white-space",), "identity")]
    overflow_wrap: Annotated[OverflowWrap | None, StyleField(("overflow-wrap",), "identity")]
    align_self: Annotated[String | None, StyleField(("align-self",), "identity")]
    justify_self: Annotated[String | None, StyleField(("justify-self",), "identity")]
    style: StyleMap | None
