from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Literal, NotRequired, TypedDict, cast

from fleur.ui.themes import Theme
from fleur.ui.themes.base import ThemeCoreTokens, ThemePalette, ThemeVariables

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
    return cast(Mapping[str, object], value)


def _get_str(mapping: Mapping[str, object], key: str) -> str | None:
    value = mapping.get(key)
    return value if isinstance(value, str) else None


def _render_css_object(node: Mapping[str, object]) -> str:
    chunks: list[str] = []
    for key, value in node.items():
        if not isinstance(key, str):
            continue
        if isinstance(value, str):
            chunks.append(f"{key}:{value};")
            continue
        if isinstance(value, Mapping):
            nested = _render_css_object(cast(Mapping[str, object], value))
            chunks.append(f"{key}{{{nested}}}")
    return "".join(chunks)


def _build_registry_variables(global_tokens: Mapping[str, object], mode_tokens: Mapping[str, object]) -> dict[str, str]:
    variables: dict[str, str] = {}
    merged = {**dict(global_tokens), **dict(mode_tokens)}
    for key, value in merged.items():
        if isinstance(key, str) and isinstance(value, str):
            variable = key if key.startswith("--") else f"--{key}"
            variables[variable] = value
    return variables


def _theme_from_token_maps(global_tokens: Mapping[str, object], mode_tokens: Mapping[str, object]) -> Theme:
    radius = _get_str(global_tokens, "radius") or _get_str(mode_tokens, "radius") or "0.5rem"
    spacing = _get_str(mode_tokens, "spacing") or _get_str(global_tokens, "spacing") or "0.25rem"
    font_sans = _get_str(mode_tokens, "font-sans") or _get_str(global_tokens, "font-sans")
    font_mono = _get_str(mode_tokens, "font-mono") or _get_str(global_tokens, "font-mono")

    return Theme(
        theme=cast(
            ThemeCoreTokens,
            {
                **({"font-sans": font_sans} if font_sans is not None else {}),
                **({"font-mono": font_mono} if font_mono is not None else {}),
                "radius": radius,
                "spacing": spacing,
            },
        ),
        light=cast(
            ThemePalette,
            {
                "background": _get_str(mode_tokens, "background") or "oklch(1 0 0)",
                "foreground": _get_str(mode_tokens, "foreground") or "oklch(0.145 0 0)",
                "card": _get_str(mode_tokens, "card") or _get_str(mode_tokens, "popover") or "oklch(1 0 0)",
                "popover": _get_str(mode_tokens, "popover") or _get_str(mode_tokens, "card") or "oklch(1 0 0)",
                "muted": _get_str(mode_tokens, "muted") or _get_str(mode_tokens, "secondary") or "oklch(0.97 0 0)",
                "muted-foreground": _get_str(mode_tokens, "muted-foreground") or "oklch(0.556 0 0)",
                "border": _get_str(mode_tokens, "border") or _get_str(mode_tokens, "input") or "oklch(0.922 0 0)",
                "input": _get_str(mode_tokens, "input") or _get_str(mode_tokens, "border") or "oklch(0.922 0 0)",
                "primary": _get_str(mode_tokens, "primary") or "oklch(0.205 0 0)",
                "primary-foreground": _get_str(mode_tokens, "primary-foreground") or "oklch(0.985 0 0)",
                "accent": _get_str(mode_tokens, "accent") or _get_str(mode_tokens, "secondary") or "oklch(0.97 0 0)",
                "accent-foreground": _get_str(mode_tokens, "accent-foreground")
                or _get_str(mode_tokens, "secondary-foreground")
                or "oklch(0.205 0 0)",
                "ring": _get_str(mode_tokens, "ring") or "oklch(0.708 0 0)",
                "spacing": spacing,
                "radius": radius,
            },
        ),
        variables=cast(ThemeVariables, _build_registry_variables(global_tokens, mode_tokens)),
        custom_variables=_build_registry_variables(global_tokens, mode_tokens),
    )


def theme_from_shadcn_registry_item(item: ShadcnRegistryItem, *, mode: ShadcnRegistryMode = "light") -> Theme:
    css_vars = _get_mapping(item.get("cssVars"), "cssVars")
    global_tokens = _get_mapping(css_vars.get("theme", {}), "cssVars.theme")
    mode_tokens = _get_mapping(css_vars.get(mode), f"cssVars.{mode}")

    theme = _theme_from_token_maps(global_tokens, mode_tokens)
    theme.mode = mode
    if mode == "dark":
        theme.dark = cast(ThemePalette, dict(theme.light))
        theme.light = cast(ThemePalette, {})

    css = item.get("css")
    if isinstance(css, Mapping):
        rendered = _render_css_object(cast(Mapping[str, object], css))
        if rendered:
            theme.extra_css.append(rendered)
    return theme


def theme_from_shadcn_registry_json(payload: str, *, mode: ShadcnRegistryMode = "light") -> Theme:
    data = json.loads(payload)
    if not isinstance(data, Mapping):
        raise ValueError("Registry payload must decode to an object")
    return theme_from_shadcn_registry_item(cast(ShadcnRegistryItem, data), mode=mode)
