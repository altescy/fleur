from __future__ import annotations

import typing
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Final, Generic, Literal

from fleur.core.component import Component
from fleur.core.template import Page, TemplateInput
from fleur.core.types import ModelT, ModelT_co, MsgGroupT, MsgGroupT_co
from fleur.core.view import View
from fleur.js.ast import ESTreeExpression
from fleur.types import ICompilable, JsonValue

from .theme import Theme, apply_theme

if TYPE_CHECKING:
    from fleur.core.msg import GroupedMsg

PropValue = ICompilable[ESTreeExpression] | JsonValue
Props = Mapping[str, PropValue]

SpacingValue = int | float | str
RadiusValue = int | float | str
StyleValue = str | int | float
StyleMap = Mapping[str, StyleValue]

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

    return f"var(--fleur-space-{token})"


def _radius(value: RadiusValue | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return f"{value}px"

    token = value.strip()
    if token.endswith(("px", "rem", "em", "%")):
        return token

    return f"var(--fleur-radius-{token})"


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
    style: StyleMap | None = None,
) -> dict[str, PropValue]:
    merged: dict[str, PropValue] = dict(props or {})
    existing_style = merged.get("style")
    style_map: dict[str, JsonValue] = dict(existing_style.items()) if isinstance(existing_style, Mapping) else {}

    gap_value = _space(gap)
    p_value = _space(p)
    px_value = _space(px)
    py_value = _space(py)
    bg_value = _color(bg)
    fg_value = _color(fg)
    radius_value = _radius(radius)

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

    if style is not None:
        style_map.update(style)

    if style_map:
        merged["style"] = style_map
    return merged


class Element(View[ModelT_co, MsgGroupT_co], Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: JsonValue | View[ModelT_co, MsgGroupT_co],
        tag: str,
        props: Props,
    ) -> None:
        super().__init__(*children, tag=tag, props=props)


class Text(Element[ModelT_co, MsgGroupT_co]):
    def __init__(self, text: str, *, props: Props | None = None, fg: str | None = None, bg: str | None = None) -> None:
        super().__init__(text, tag="span", props=_merge_props(props, fg=fg, bg=bg))


class VStack(Element[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: JsonValue | View[ModelT_co, MsgGroupT_co],
        props: Props | None = None,
        gap: SpacingValue | None = None,
        bg: RawColor | str | None = None,
        fg: RawColor | str | None = None,
        p: SpacingValue | None = None,
        px: SpacingValue | None = None,
        py: SpacingValue | None = None,
        radius: RadiusValue | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(
            props,
            gap=gap,
            bg=bg,
            fg=fg,
            p=p,
            px=px,
            py=py,
            radius=radius,
            style=style,
        )
        existing_style = merged.get("style")
        style_props: dict[str, JsonValue] = dict(existing_style.items()) if isinstance(existing_style, Mapping) else {}
        style_props.setdefault("display", "flex")
        style_props.setdefault("flex-direction", "column")
        merged["style"] = style_props
        super().__init__(*children, tag="div", props=merged)


class Button(Element[ModelT_co, MsgGroupT], Generic[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: str | View[ModelT_co, MsgGroupT],
        onclick: "GroupedMsg[MsgGroupT, object]",
        props: Props | None = None,
        bg: RawColor | str | None = None,
        fg: RawColor | str | None = None,
        p: SpacingValue | None = None,
        px: SpacingValue | None = None,
        py: SpacingValue | None = None,
        radius: RadiusValue | None = None,
        style: StyleMap | None = None,
    ) -> None:
        merged = _merge_props(props, bg=bg, fg=fg, p=p, px=px, py=py, radius=radius, style=style)
        merged["onclick"] = onclick
        super().__init__(*children, tag="button", props=merged)


def bloom(
    component: Component[ModelT, MsgGroupT] | type[object] | Callable[[], Component[ModelT, MsgGroupT]],
    *,
    theme: Theme | None = None,
    page: Page | None = None,
    template: TemplateInput | None = None,
    component_name: str | None = None,
) -> str:
    from fleur import bloom as core_bloom

    resolved_page = page or Page()
    if theme is not None:
        resolved_page = apply_theme(resolved_page, theme)

    return core_bloom(component, page=resolved_page, template=template, component_name=component_name)
