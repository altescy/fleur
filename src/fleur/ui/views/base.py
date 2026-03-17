from __future__ import annotations

import typing
from collections.abc import Mapping
from typing import Any, Final, Generic, Literal, TypeAlias

from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import View
from fleur.types import JsonValue

ViewChild: TypeAlias = JsonValue | View[ModelT_co, MsgGroupT_co] | Expr[JsonValue | View[ModelT_co, MsgGroupT_co]]
PropValue: TypeAlias = JsonValue | Expr[JsonValue] | GroupedMsg[MsgGroupT_co, object, Any]
Props = Mapping[str, PropValue]

SpacingValue = int | float | str
RadiusValue = int | float | str
LengthValue = int | float | str
StyleValue = str | int | float
StyleMap = Mapping[str, StyleValue]
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


def _is_raw_color(value: str) -> bool:
    lower = value.lower()
    return lower in _RAW_COLORS or lower.startswith(("#", "rgb(", "rgba(", "hsl(", "hsla(", "var("))


def _space(value: SpacingValue | None) -> str | None:
    if value is None:
        return None
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


def _radius(value: RadiusValue | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return f"{value}px"

    token = value.strip()
    if token.endswith(("px", "rem", "em", "%")):
        return token

    if token.startswith(("var(", "calc(")):
        return token

    return f"var(--fleur-radius-{token})"


def _length(value: LengthValue | None) -> str | None:
    return _space(value)


def _color(value: str | None) -> str | None:
    if value is None:
        return None
    return value if _is_raw_color(value) else f"var(--fleur-color-{value})"


def _merge_props(
    props: Props | None,
    *,
    gap: SpacingValue | None = None,
    bg: RawColor | str | None = None,
    fg: RawColor | str | None = None,
    p: SpacingValue | None = None,
    px: SpacingValue | None = None,
    py: SpacingValue | None = None,
    radius: RadiusValue | None = None,
    mx: SpacingValue | None = None,
    my: SpacingValue | None = None,
    mt: SpacingValue | None = None,
    mr: SpacingValue | None = None,
    mb: SpacingValue | None = None,
    ml: SpacingValue | None = None,
    w: LengthValue | None = None,
    h: LengthValue | None = None,
    max_w: LengthValue | None = None,
    border: str | None = None,
    font_size: LengthValue | None = None,
    font_weight: int | str | None = None,
    font_family: str | None = None,
    display: str | None = None,
    flex_direction: FlexDirection | None = None,
    flex_wrap: FlexWrap | None = None,
    justify: str | None = None,
    align: str | None = None,
    style: StyleMap | None = None,
) -> dict[str, PropValue]:
    merged: dict[str, PropValue] = dict(props or {})
    existing_style = merged.get("style")
    style_map: dict[str, JsonValue] = dict(existing_style.items()) if isinstance(existing_style, Mapping) else {}

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
    font_size_value = _length(font_size)

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
        style_map["font-weight"] = str(font_weight)
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
