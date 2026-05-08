from collections.abc import Mapping
from typing import Unpack, assert_never, cast

from fleur.core.expr import Expr, ensure_expr
from fleur.core.view import ViewProp, ViewProps, _compile_prop_value
from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, json_expr, member_expr, object_expr

from ._constants import COLOR_KEYWORDS
from .types import (
    Color,
    FontSize,
    Length,
    Radius,
    Spacing,
    Style,
    ViewStyleArgs,
)


def _is_raw_color(value: str) -> bool:
    lower = value.lower()
    return lower in COLOR_KEYWORDS or lower.startswith(("#", "rgb(", "rgba(", "hsl(", "hsla(", "var("))


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


def merge_props(
    props: ViewProps | None,
    **style_args: Unpack[ViewStyleArgs],
) -> ViewProps:
    gap = style_args.get("gap")
    bg = style_args.get("bg")
    fg = style_args.get("fg")
    p = style_args.get("p")
    px = style_args.get("px")
    py = style_args.get("py")
    pt = style_args.get("pt")
    pr = style_args.get("pr")
    pb = style_args.get("pb")
    pl = style_args.get("pl")
    radius = style_args.get("radius")
    mx = style_args.get("mx")
    my = style_args.get("my")
    mt = style_args.get("mt")
    mr = style_args.get("mr")
    mb = style_args.get("mb")
    ml = style_args.get("ml")
    w = style_args.get("w")
    h = style_args.get("h")
    min_w = style_args.get("min_w")
    max_w = style_args.get("max_w")
    border = style_args.get("border")
    font_size = style_args.get("font_size")
    font_weight = style_args.get("font_weight")
    font_family = style_args.get("font_family")
    display = style_args.get("display")
    flex_direction = style_args.get("flex_direction")
    flex_wrap = style_args.get("flex_wrap")
    justify = style_args.get("justify")
    align = style_args.get("align")
    text_align = style_args.get("text_align")
    align_self = style_args.get("align_self")
    justify_self = style_args.get("justify_self")
    style = style_args.get("style")

    gap_value = _space(gap)
    p_value = _space(p)
    px_value = _space(px)
    py_value = _space(py)
    pt_value = _space(pt)
    pr_value = _space(pr)
    pb_value = _space(pb)
    pl_value = _space(pl)
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
    min_width_value = _length(min_w)
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
    if pt_value is not None:
        style_kwargs["padding-top"] = pt_value
    if pr_value is not None:
        style_kwargs["padding-right"] = pr_value
    if pb_value is not None:
        style_kwargs["padding-bottom"] = pb_value
    if pl_value is not None:
        style_kwargs["padding-left"] = pl_value
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
    if min_width_value is not None:
        style_kwargs["min-width"] = min_width_value
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
    if text_align is not None:
        style_kwargs["text-align"] = text_align
    if align_self is not None:
        style_kwargs["align-self"] = align_self
    if justify_self is not None:
        style_kwargs["justify-self"] = justify_self
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


def extend_props(props: ViewProps, extra: ViewProps) -> ViewProps:
    """Add extra top-level properties (e.g. event handlers, HTML attributes) to ViewProps."""
    if not extra:
        return props
    match (props, extra):
        case (Expr(), Mapping()):
            compiled_extra = object_expr((k, _compile_prop_value(v)) for k, v in extra.items())
            return Expr(_js_assign(props.__compile__(), compiled_extra))
        case (Mapping(), Expr()):
            return Expr(_js_assign(ensure_expr(props), ensure_expr(extra)))
        case (Expr(), Expr()):
            return Expr(_js_assign(props.__compile__(), extra.__compile__()))
        case (Mapping(), Mapping()):
            return {**props, **extra}
        case _:
            assert_never((props, extra))


def set_default_style(props: ViewProps, defaults: dict[str, Style]) -> ViewProps:
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
