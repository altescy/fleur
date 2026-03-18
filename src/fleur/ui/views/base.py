from __future__ import annotations

import typing
from collections.abc import Mapping
from typing import Final, Generic, Literal, cast

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import View, ViewChild, ViewProp

Props = Mapping[str, ViewProp]

SpacingValue = int | float | str
RadiusValue = int | float | str
LengthValue = int | float | str
FontSizeValue = int | float | str
StyleValue = str | int | float | Expr[str | int | float]
StyleMap = Mapping[str, StyleValue]
SpacingArg = SpacingValue | Expr[SpacingValue]
RadiusArg = RadiusValue | Expr[RadiusValue]
LengthArg = LengthValue | Expr[LengthValue]
FontSizeArg = FontSizeValue | Expr[FontSizeValue]
FontWeightArg = int | str | Expr[int | str]
StringArg = str | Expr[str]
FlexDirection = Literal["row", "column", "row-reverse", "column-reverse"]
FlexWrap = Literal["nowrap", "wrap", "wrap-reverse"]

RawColor = Literal[
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
_RAW_COLORS: Final[set[RawColor]] = set(typing.get_args(RawColor))
ColorArg = RawColor | str | Expr[RawColor | str]


def _is_raw_color(value: str) -> bool:
    lower = value.lower()
    return lower in _RAW_COLORS or lower.startswith(("#", "rgb(", "rgba(", "hsl(", "hsla(", "var("))


def _space(value: SpacingArg | None) -> str | Expr[int | float | str] | None:
    if value is None:
        return None
    if isinstance(value, Expr):
        return value
    if isinstance(value, (int, float)):
        return f"{value}px"

    token = value.strip()
    if token.replace(".", "", 1).isdigit():
        return f"{token}px"

    if token.endswith(("px", "rem", "em", "%", "vh", "vw")):
        return token

    if token.startswith(("var(", "calc(")):
        return token

    if token == "auto":
        return token

    return f"var(--fleur-space-{token})"


def _radius(value: RadiusArg | None) -> RadiusArg | None:
    if value is None:
        return None
    if isinstance(value, Expr):
        return value
    if isinstance(value, (int, float)):
        return f"{value}px"

    token = value.strip()
    if token.endswith(("px", "rem", "em", "%")):
        return token

    if token.startswith(("var(", "calc(")):
        return token

    return f"var(--fleur-radius-{token})"


def _length(value: LengthArg | None) -> LengthArg | None:
    return _space(value)


def _font_size(value: FontSizeArg | None) -> FontSizeArg | None:
    if value is None:
        return None
    if isinstance(value, Expr):
        return value
    if isinstance(value, (int, float)):
        return f"{value}px"

    token = value.strip()
    if token.replace(".", "", 1).isdigit():
        return f"{token}px"

    if token.endswith(("px", "rem", "em", "%", "vh", "vw")):
        return token

    if token.startswith(("var(", "calc(")):
        return token

    return f"var(--fleur-text-{token})"


def _color(value: ColorArg | None) -> ColorArg | None:
    if value is None:
        return None
    if isinstance(value, Expr):
        return value
    return value if _is_raw_color(value) else f"var(--fleur-color-{value})"


def _merge_props(
    props: Props | None,
    *,
    gap: SpacingArg | None = None,
    bg: ColorArg | None = None,
    fg: ColorArg | None = None,
    p: SpacingArg | None = None,
    px: SpacingArg | None = None,
    py: SpacingArg | None = None,
    radius: RadiusArg | None = None,
    mx: SpacingArg | None = None,
    my: SpacingArg | None = None,
    mt: SpacingArg | None = None,
    mr: SpacingArg | None = None,
    mb: SpacingArg | None = None,
    ml: SpacingArg | None = None,
    w: LengthArg | None = None,
    h: LengthArg | None = None,
    max_w: LengthArg | None = None,
    border: StringArg | None = None,
    font_size: FontSizeArg | None = None,
    font_weight: FontWeightArg | None = None,
    font_family: StringArg | None = None,
    display: StringArg | None = None,
    flex_direction: FlexDirection | Expr | None = None,
    flex_wrap: FlexWrap | Expr | None = None,
    justify: StringArg | None = None,
    align: StringArg | None = None,
    style: StyleMap | None = None,
) -> dict[str, ViewProp]:
    merged: dict[str, ViewProp] = dict(props or {})
    existing_style = merged.get("style")
    style_map: dict[str, StyleValue] = (
        {key: cast(StyleValue, value) for key, value in existing_style.items()}
        if isinstance(existing_style, Mapping)
        else {}
    )

    gap_value = _space(gap)
    p_value = _space(p)
    px_value = _space(px)
    py_value = _space(py)
    mx_value = _space(mx)
    my_value = _space(my)
    mt_value = _space(mt)
    mr_value = _space(mr)
    mb_value = _space(mb)
    ml_value = _space(ml)
    bg_value = _color(bg)
    fg_value = _color(fg)
    radius_value = _radius(radius)
    width_value = _length(w)
    height_value = _length(h)
    max_width_value = _length(max_w)
    font_size_value = _font_size(font_size)

    if gap_value is not None:
        style_map["gap"] = gap_value
    if bg_value is not None:
        style_map["background"] = bg_value
    if fg_value is not None:
        style_map["color"] = fg_value
    if p_value is not None:
        style_map["padding"] = p_value
    if px_value is not None:
        style_map["padding-left"] = px_value
        style_map["padding-right"] = px_value
    if py_value is not None:
        style_map["padding-top"] = py_value
        style_map["padding-bottom"] = py_value
    if radius_value is not None:
        style_map["border-radius"] = radius_value
    if mx_value is not None:
        style_map["margin-left"] = mx_value
        style_map["margin-right"] = mx_value
    if my_value is not None:
        style_map["margin-top"] = my_value
        style_map["margin-bottom"] = my_value
    if mt_value is not None:
        style_map["margin-top"] = mt_value
    if mr_value is not None:
        style_map["margin-right"] = mr_value
    if mb_value is not None:
        style_map["margin-bottom"] = mb_value
    if ml_value is not None:
        style_map["margin-left"] = ml_value
    if width_value is not None:
        style_map["width"] = width_value
    if height_value is not None:
        style_map["height"] = height_value
    if max_width_value is not None:
        style_map["max-width"] = max_width_value
    if border is not None:
        style_map["border"] = border
    if font_size_value is not None:
        style_map["font-size"] = font_size_value
    if font_weight is not None:
        style_map["font-weight"] = font_weight if isinstance(font_weight, Expr) else str(font_weight)
    if font_family is not None:
        style_map["font-family"] = font_family
    if display is not None:
        style_map["display"] = display
    if flex_direction is not None:
        style_map["flex-direction"] = flex_direction
    if flex_wrap is not None:
        style_map["flex-wrap"] = flex_wrap
    if justify is not None:
        style_map["justify-content"] = justify
    if align is not None:
        style_map["align-items"] = align

    if style is not None:
        style_map.update(style)

    if style_map:
        merged["style"] = style_map
    return merged


class Element(View[ModelT_co, MsgGroupT_co], Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        tag: str,
        props: Props,
    ) -> None:
        super().__init__(*children, tag=tag, props=props)
