from __future__ import annotations

import typing
from collections.abc import Mapping
from typing import Any, Final, Generic, Literal, cast

from fleur.core.expr import Expr
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import View, ViewChild, ViewProp, ViewProps, _compile_prop_value
from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, json_expr, member_expr, object_expr

_Spacing = int | float | str
_Radius = int | float | str
_Length = int | float | str
_FontSize = int | float | str
_FontWeight = int | str
_Style = int | float | str
_String = str
_FlexDirection = Literal["row", "column", "row-reverse", "column-reverse"]
_FlexWrap = Literal["nowrap", "wrap", "wrap-reverse"]
Style = _Style | Expr[_Style]
StyleMap = Mapping[str, Style]
Spacing = _Spacing | Expr[_Spacing]
Radius = _Radius | Expr[_Radius]
Length = _Length | Expr[_Length]
FontSize = _FontSize | Expr[_FontSize]
FontWeight = _FontWeight | Expr[_FontWeight]
String = _String | Expr[_String]
FlexDirection = _FlexDirection | Expr[_FlexDirection]
FlexWrap = _FlexWrap | Expr[_FlexWrap]


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
Color = RawColor | str | Expr[RawColor | str]


def _is_raw_color(value: str) -> bool:
    lower = value.lower()
    return lower in _RAW_COLORS or lower.startswith(("#", "rgb(", "rgba(", "hsl(", "hsla(", "var("))


def _space(value: Spacing | None) -> str | Expr[int | float | str] | None:
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


def _radius(value: Radius | None) -> Radius | None:
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


def _length(value: Length | None) -> Length | None:
    return _space(value)


def _font_size(value: FontSize | None) -> FontSize | None:
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


def _color(value: Color | None) -> Color | None:
    if value is None:
        return None
    if isinstance(value, Expr):
        return value
    return value if _is_raw_color(value) else f"var(--fleur-color-{value})"


def _compile_style_value(v: Style) -> ESTreeExpression:
    if isinstance(v, Expr):
        return v.__compile__()
    return json_expr(v)


def _js_assign(*sources: ESTreeExpression) -> ESTreeExpression:
    """Build Object.assign({}, ...sources) expression."""
    return call(member_expr(ident("Object"), "assign"), object_expr([]), *sources)


def _merge_props(
    props: ViewProps | None,
    *,
    gap: Spacing | None = None,
    bg: Color | None = None,
    fg: Color | None = None,
    p: Spacing | None = None,
    px: Spacing | None = None,
    py: Spacing | None = None,
    radius: Radius | None = None,
    mx: Spacing | None = None,
    my: Spacing | None = None,
    mt: Spacing | None = None,
    mr: Spacing | None = None,
    mb: Spacing | None = None,
    ml: Spacing | None = None,
    w: Length | None = None,
    h: Length | None = None,
    max_w: Length | None = None,
    border: String | None = None,
    font_size: FontSize | None = None,
    font_weight: FontWeight | None = None,
    font_family: String | None = None,
    display: String | None = None,
    flex_direction: FlexDirection | None = None,
    flex_wrap: FlexWrap | None = None,
    justify: String | None = None,
    align: String | None = None,
    style: StyleMap | None = None,
) -> ViewProps:
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

    style_kwargs: dict[str, Style] = {}
    if gap_value is not None:
        style_kwargs["gap"] = gap_value
    if bg_value is not None:
        style_kwargs["background"] = bg_value
    if fg_value is not None:
        style_kwargs["color"] = fg_value
    if p_value is not None:
        style_kwargs["padding"] = p_value
    if px_value is not None:
        style_kwargs["padding-left"] = px_value
        style_kwargs["padding-right"] = px_value
    if py_value is not None:
        style_kwargs["padding-top"] = py_value
        style_kwargs["padding-bottom"] = py_value
    if radius_value is not None:
        style_kwargs["border-radius"] = radius_value
    if mx_value is not None:
        style_kwargs["margin-left"] = mx_value
        style_kwargs["margin-right"] = mx_value
    if my_value is not None:
        style_kwargs["margin-top"] = my_value
        style_kwargs["margin-bottom"] = my_value
    if mt_value is not None:
        style_kwargs["margin-top"] = mt_value
    if mr_value is not None:
        style_kwargs["margin-right"] = mr_value
    if mb_value is not None:
        style_kwargs["margin-bottom"] = mb_value
    if ml_value is not None:
        style_kwargs["margin-left"] = ml_value
    if width_value is not None:
        style_kwargs["width"] = width_value
    if height_value is not None:
        style_kwargs["height"] = height_value
    if max_width_value is not None:
        style_kwargs["max-width"] = max_width_value
    if border is not None:
        style_kwargs["border"] = border
    if font_size_value is not None:
        style_kwargs["font-size"] = font_size_value
    if font_weight is not None:
        style_kwargs["font-weight"] = font_weight if isinstance(font_weight, Expr) else str(font_weight)
    if font_family is not None:
        style_kwargs["font-family"] = font_family
    if display is not None:
        style_kwargs["display"] = display
    if flex_direction is not None:
        style_kwargs["flex-direction"] = flex_direction
    if flex_wrap is not None:
        style_kwargs["flex-wrap"] = flex_wrap
    if justify is not None:
        style_kwargs["justify-content"] = justify
    if align is not None:
        style_kwargs["align-items"] = align
    if style is not None:
        style_kwargs.update(style)

    if isinstance(props, Expr):
        if not style_kwargs:
            return props
        props_expr = props.__compile__()
        compiled_style_kwargs = object_expr((k, _compile_style_value(v)) for k, v in style_kwargs.items())
        # Object.assign({}, propsExpr, {style: Object.assign({}, propsExpr.style, styleKwargs)})
        merged_style = _js_assign(member_expr(props_expr, "style"), compiled_style_kwargs)
        return Expr(_js_assign(props_expr, object_expr([("style", merged_style)])))

    merged = dict(props or {})
    existing_style = merged.get("style")
    style_map: dict[str, Style] = (
        {key: cast(Style, value) for key, value in existing_style.items()}
        if isinstance(existing_style, Mapping)
        else {}
    )
    style_map.update(style_kwargs)

    if style_map:
        merged = {**merged, "style": style_map}
    return merged


def _extend_props(props: ViewProps, extra: dict[str, Any]) -> ViewProps:
    """Add extra top-level properties (e.g. event handlers, HTML attributes) to ViewProps."""
    if not extra:
        return props
    if isinstance(props, Expr):
        compiled_extra = object_expr((k, _compile_prop_value(v)) for k, v in extra.items())
        return Expr(_js_assign(props.__compile__(), compiled_extra))
    merged: dict[str, ViewProp] = dict(props)
    merged.update(extra)
    return cast(ViewProps, merged)


def _set_default_style(props: ViewProps, defaults: dict[str, Style]) -> ViewProps:
    """Apply style defaults (setdefault semantics) to ViewProps."""
    if not defaults:
        return props
    if isinstance(props, Expr):
        # defaults are the base; props.style overwrites them (setdefault semantics)
        props_expr = props.__compile__()
        compiled_defaults = object_expr((k, _compile_style_value(v)) for k, v in defaults.items())
        # Object.assign(defaults, props.style) — props.style wins over defaults
        merged_style = call(member_expr(ident("Object"), "assign"), compiled_defaults, member_expr(props_expr, "style"))
        return Expr(_js_assign(props_expr, object_expr([("style", merged_style)])))
    merged: dict[str, ViewProp] = dict(props)
    existing_style = merged.get("style")
    style_map: dict[str, Style] = (
        {key: cast(Style, value) for key, value in existing_style.items()}
        if isinstance(existing_style, Mapping)
        else {}
    )
    for k, v in defaults.items():
        style_map.setdefault(k, v)
    return cast(ViewProps, {**merged, "style": style_map})


class Element(View[ModelT_co, MsgGroupT_co], Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        tag: str,
        props: ViewProps,
    ) -> None:
        super().__init__(*children, tag=tag, props=props)
