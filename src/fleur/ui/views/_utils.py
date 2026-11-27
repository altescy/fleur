from collections.abc import Mapping
from typing import Annotated, Literal, Unpack, assert_never, cast, get_args, get_origin, get_type_hints

from fleur.core.cond import Cond
from fleur.core.expr import Expr
from fleur.core.number import Number
from fleur.core.string import String as StringValue
from fleur.core.types import MsgGroupT
from fleur.core.view import View, ViewProp, ViewProps
from fleur.ui._css import CssValue, color_reference

from .types import (
    Color,
    Dimension,
    FlexDirection,
    FlexWrap,
    FontSize,
    FontWeight,
    Margin,
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

_DIMENSION_KEYWORDS = {
    "full": "100%",
    "fit": "fit-content",
    "1/2": "50%",
    "1/3": "calc(100% / 3)",
    "2/3": "calc(200% / 3)",
    "1/4": "25%",
    "3/4": "75%",
}


def color_value(value: Color) -> str | Expr[str]:
    if isinstance(value, CssValue):
        return value.value
    if isinstance(value, Expr):
        return Cond.when(Cond.equal(value, "transparent"), "transparent", "var(--fleur-color-" + value + ")")
    return color_reference(value)


def scale_value(
    scale: str,
    value: Dimension | Margin | Radius | FontSize,
    *,
    keywords: Mapping[str, str] | None = None,
) -> str | Expr[str]:
    if isinstance(value, CssValue):
        return value.value
    if isinstance(value, Expr):
        text = StringValue.from_value(value)
        resolved = Cond.when(Number.is_finite(value), text + "px", f"var(--fleur-{scale}-" + text + ")")
        for name, css_value in (keywords or {}).items():
            resolved = Cond.when(Cond.equal(value, name), css_value, resolved)
        return resolved
    if isinstance(value, (int, float)):
        return f"{value}px"
    return (keywords or {}).get(value, f"var(--fleur-{scale}-{value})")


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
        case "space":
            return scale_value("space", cast(Spacing, value))
        case "margin":
            return scale_value("space", cast(Margin, value), keywords={"auto": "auto"})
        case "length":
            return scale_value("space", cast(Dimension, value), keywords=_DIMENSION_KEYWORDS)
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


def _merge_declarations(*layers: Mapping[str, ViewProp[MsgGroupT]]) -> dict[str, ViewProp[MsgGroupT]]:
    """Move replaced keys to the end so later layers also win CSS shorthand conflicts."""
    merged: dict[str, ViewProp[MsgGroupT]] = {}
    for layer in layers:
        for key, value in layer.items():
            merged.pop(key, None)
            merged[key] = value
    return merged


def merge_props(
    props: ViewProps[MsgGroupT] | None,
    *,
    element: Literal[
        "box",
        "text",
        "input",
        "number-field",
        "button",
        "link",
        "notice",
        "toast",
        "progress",
        "meter",
        "slider",
        "empty-state",
        "radio-group",
        "checkbox-field",
        "checkbox-group",
        "switch",
        "card",
        "avatar",
        "dialog",
        "popover",
        "menu",
        "menubar",
        "menu-item",
        "navigation-menu",
        "tooltip",
        "preview-card",
        "disclosure",
        "accordion",
        "scroll-area",
        "toolbar",
        "toggle-group",
        "heading",
        "field",
        "fieldset",
        "select",
        "combobox",
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
) -> ViewProps[MsgGroupT]:
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
    return View.merge_styles(props, defaults, overrides)


extend_props = View.extend_props
