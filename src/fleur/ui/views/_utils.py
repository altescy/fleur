from collections.abc import Mapping
from typing import Annotated, Literal, Unpack, assert_never, cast, get_args, get_origin, get_type_hints

from fleur.core.cond import Cond
from fleur.core.expr import Expr
from fleur.core.number import Number
from fleur.core.runtime import runtime_call
from fleur.core.view import ViewProp, ViewProps, _compile_prop_value
from fleur.js.builder import call, ident, member_expr, object_expr

from .types import (
    Color,
    CssValue,
    FlexDirection,
    FlexWrap,
    FontSize,
    FontWeight,
    Radius,
    Spacing,
    String,
    Style,
    StyleField,
    StyleMap,
    StyleTransform,
    StyleTransformValue,
    ViewStyleArgs,
)


def color_value(value: Color) -> str | Expr[str]:
    if isinstance(value, CssValue):
        return value.value
    if isinstance(value, Expr):
        return Cond.when(Cond.equal(value, "transparent"), "transparent", "var(--fleur-color-" + value + ")")
    return value if value == "transparent" else f"var(--fleur-color-{value})"


def scale_value(scale: str, value: Spacing | Radius | FontSize) -> str | Expr[str]:
    if isinstance(value, CssValue):
        return value.value
    if isinstance(value, Expr):
        text = Expr[str](call(ident("String"), value.__compile__()))
        return Cond.when(Number.is_finite(value), text + "px", f"var(--fleur-{scale}-" + text + ")")
    if isinstance(value, (int, float)):
        return f"{value}px"
    return f"var(--fleur-{scale}-{value})"


def _identity(value: String | FlexDirection | FlexWrap | None) -> Style | None:
    return value


def _font_weight(value: FontWeight | None) -> Style | None:
    if value is None:
        return None
    return value if isinstance(value, Expr) else str(value)


def _transform_value(transform: StyleTransform, value: StyleTransformValue) -> Style | None:
    if value is None:
        return None
    match transform:
        case "color":
            return color_value(cast(Color, value))
        case "space" | "length":
            return scale_value("space", cast(Spacing, value))
        case "radius":
            return scale_value("radius", cast(Radius, value))
        case "font_size":
            return scale_value("text", cast(FontSize, value))
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


def _merge_declarations(*layers: Mapping[str, ViewProp]) -> dict[str, ViewProp]:
    """Move replaced keys to the end so later layers also win CSS shorthand conflicts."""
    merged: dict[str, ViewProp] = {}
    for layer in layers:
        for key, value in layer.items():
            merged.pop(key, None)
            merged[key] = value
    return merged


def merge_props(
    props: ViewProps | None,
    *,
    element: Literal[
        "box",
        "text",
        "input",
        "button",
        "grid",
        "grid-item",
        "hstack",
        "vstack",
        "divider",
        "textarea",
        "table",
        "table-row",
        "table-head",
        "table-cell",
        "table-caption",
    ]
    | None = None,
    defaults: StyleMap | None = None,
    layout: StyleMap | None = None,
    **style_args: Unpack[ViewStyleArgs],
) -> ViewProps:
    """Compose defaults, supplied style, layout arguments, shorthands, then explicit style."""
    style_kwargs: dict[str, Style] = {}
    for key, rule in _STYLE_RULES.items():
        if key not in style_args:
            continue
        normalized = _transform_value(rule.transform, cast(StyleTransformValue, style_args[key]))
        if normalized is None:
            continue
        for css_prop in rule.css_props:
            style_kwargs.pop(css_prop, None)
            style_kwargs[css_prop] = normalized

    props = {} if props is None else props
    if element is not None:
        props = extend_props(props, {"data-fleur-ui": element})
    elif style_args.get("bg") is not None:
        props = extend_props(props, {"data-fleur-bg": ""})
    defaults = defaults or {}
    overrides = _merge_declarations(layout or {}, style_kwargs, style_args.get("style") or {})
    if not defaults and not overrides:
        return props

    if isinstance(props, Expr) or isinstance(props.get("style"), Expr):
        return Expr(
            runtime_call(
                ("mergeStyleProps",),
                _compile_prop_value(props),
                _compile_prop_value(defaults),
                _compile_prop_value(overrides),
            )
        )

    supplied = props.get("style")
    style = _merge_declarations(defaults, supplied if isinstance(supplied, Mapping) else {}, overrides)
    return {**props, "style": style}


def extend_props(props: ViewProps, extra: ViewProps) -> ViewProps:
    """Append top-level attributes, evaluating each dynamic source once."""
    if isinstance(extra, Mapping) and not extra:
        return props
    if isinstance(props, Mapping) and isinstance(extra, Mapping):
        return {**props, **extra}
    return Expr(
        call(
            member_expr(ident("Object"), "assign"),
            object_expr([]),
            _compile_prop_value(props),
            _compile_prop_value(extra),
        )
    )
