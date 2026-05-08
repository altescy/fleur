from collections.abc import Mapping
from typing import Annotated, Unpack, assert_never, cast, get_args, get_origin, get_type_hints

from fleur.core.expr import Expr, ensure_expr
from fleur.core.view import ViewProp, ViewProps, _compile_prop_value
from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, json_expr, member_expr, object_expr

from ._constants import COLOR_KEYWORDS
from .types import (
    Color,
    FlexDirection,
    FlexWrap,
    FontSize,
    FontWeight,
    Length,
    Radius,
    Spacing,
    String,
    Style,
    StyleField,
    StyleTransform,
    StyleTransformValue,
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


def _identity(value: String | FlexDirection | FlexWrap | None) -> Style | None:
    return value


def _font_weight(value: FontWeight | None) -> Style | None:
    if value is None:
        return None
    return value if isinstance(value, Expr) else str(value)


def _transform_value(transform: StyleTransform, value: StyleTransformValue) -> Style | None:
    match transform:
        case "color":
            return _color(cast(Color | None, value))
        case "space":
            return _space(cast(Spacing | None, value))
        case "radius":
            return _radius(cast(Radius | None, value))
        case "length":
            return _length(cast(Length | None, value))
        case "font_size":
            return _font_size(cast(FontSize | None, value))
        case "font_weight":
            return _font_weight(cast(FontWeight | None, value))
        case "identity":
            return _identity(cast(String | FlexDirection | FlexWrap | None, value))
        case _:
            assert_never(transform)


def _get_style_rules() -> dict[str, StyleField]:
    hints = get_type_hints(ViewStyleArgs, include_extras=True)
    rules: dict[str, StyleField] = {}
    for key, annotation in hints.items():
        if key == "style":
            continue
        if get_origin(annotation) is Annotated:
            args = get_args(annotation)
            for meta in args[1:]:
                if isinstance(meta, StyleField):
                    rules[key] = meta
                    break
    missing = set(ViewStyleArgs.__annotations__.keys()) - set(rules.keys()) - {"style"}
    if missing:
        raise ValueError(f"Missing StyleField metadata for keys: {sorted(missing)}")
    return rules


_STYLE_RULES = _get_style_rules()


def merge_props(
    props: ViewProps | None,
    **style_args: Unpack[ViewStyleArgs],
) -> ViewProps:
    style_kwargs: dict[str, Style] = {}
    for key, rule in _STYLE_RULES.items():
        if key not in style_args:
            continue
        normalized = _transform_value(rule.transform, cast(StyleTransformValue, style_args[key]))
        if normalized is None:
            continue
        for css_prop in rule.css_props:
            style_kwargs[css_prop] = normalized

    style = style_args.get("style")
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
