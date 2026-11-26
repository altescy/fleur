from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Literal, NotRequired, TypedDict, cast

from fleur.ui.themes import Theme
from fleur.ui.themes.base import ThemeCoreTokens, ThemePalette

ShadcnRegistryMode = Literal["light", "dark"]


class ShadcnRegistryCssVars(TypedDict, total=False):
    theme: dict[str, str]
    light: dict[str, str]
    dark: dict[str, str]


ShadcnCssValue = str | dict[str, "ShadcnCssValue"]


class ShadcnRegistryItem(TypedDict, total=False):
    name: str
    cssVars: ShadcnRegistryCssVars
    css: dict[str, ShadcnCssValue]
    type: str
    description: NotRequired[str]


def _get_mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be an object")
    return value


def _render_css_object(node: Mapping[str, object]) -> str:
    chunks: list[str] = []
    for key, value in node.items():
        if not isinstance(key, str):
            continue
        if isinstance(value, str):
            chunks.append(f"{key}:{value};")
            continue
        if isinstance(value, Mapping):
            nested = _render_css_object(value)
            chunks.append(f"{key}{{{nested}}}")
    return "".join(chunks)


def _tokens(value: object, path: str, names: frozenset[str]) -> dict[str, str]:
    return {k: v for k, v in _get_mapping(value, path).items() if k in names and isinstance(v, str)}


def theme_from_shadcn_registry_item(item: ShadcnRegistryItem, *, mode: ShadcnRegistryMode = "light") -> Theme:
    css_vars = _get_mapping(item.get("cssVars"), "cssVars")
    theme = Theme(
        mode=mode,
        theme=cast(
            ThemeCoreTokens, _tokens(css_vars.get("theme", {}), "cssVars.theme", ThemeCoreTokens.__optional_keys__)
        ),
        light=cast(ThemePalette, _tokens(css_vars.get("light", {}), "cssVars.light", ThemePalette.__optional_keys__)),
        dark=cast(ThemePalette, _tokens(css_vars.get("dark", {}), "cssVars.dark", ThemePalette.__optional_keys__)),
    )

    css = item.get("css")
    if isinstance(css, Mapping):
        rendered = _render_css_object(css)
        if rendered:
            theme.extra_css.append(rendered)
    return theme


def theme_from_shadcn_registry_json(payload: str, *, mode: ShadcnRegistryMode = "light") -> Theme:
    data = json.loads(payload)
    if not isinstance(data, Mapping):
        raise ValueError("Registry payload must decode to an object")
    return theme_from_shadcn_registry_item(cast(ShadcnRegistryItem, data), mode=mode)
