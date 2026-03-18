from __future__ import annotations

from dataclasses import replace
from typing import cast

from fleur.core.template import Page

from .base import (
    Theme,
    ThemeColorName,
    ThemeColors,
    ThemeComponentName,
    ThemeComponentTokenName,
    ThemeCoreTokens,
    ThemeFontSizeName,
    ThemeMode,
    ThemePalette,
    ThemeRadiusName,
    ThemeSpaceName,
    ThemeTypographyName,
    ThemeVariables,
    _normalize_length,
    _normalize_name,
)
from .basic import BASIC_THEME
from .zen import ZEN_THEME

DEFAULT_THEME = BASIC_THEME


def _derive_scale(spacing: str) -> dict[ThemeSpaceName, str]:
    return {
        "xs": spacing,
        "sm": f"calc({spacing} * 2)",
        "md": f"calc({spacing} * 3)",
        "lg": f"calc({spacing} * 4)",
        "xl": f"calc({spacing} * 6)",
    }


def _derive_radii(radius: str) -> dict[ThemeRadiusName, str]:
    return {
        "sm": f"calc({radius} - 2px)",
        "md": radius,
        "lg": f"calc({radius} + 2px)",
    }


def _resolved_shadcn_tokens(theme: Theme) -> dict[str, str]:
    palette = theme.dark if theme.mode == "dark" and theme.dark else theme.light
    return cast(dict[str, str], {**theme.theme, **palette})


def _shadcn_color_overrides(tokens: dict[str, str]) -> ThemeColors:
    return {
        "background": tokens.get("background", "oklch(1 0 0)"),
        "foreground": tokens.get("foreground", "oklch(0.145 0 0)"),
        "card": tokens.get("card", tokens.get("popover", "oklch(1 0 0)")),
        "card-foreground": tokens.get("card-foreground", tokens.get("foreground", "oklch(0.145 0 0)")),
        "popover": tokens.get("popover", tokens.get("card", "oklch(1 0 0)")),
        "popover-foreground": tokens.get("popover-foreground", tokens.get("foreground", "oklch(0.145 0 0)")),
        "primary": tokens.get("primary", "oklch(0.205 0 0)"),
        "primary-foreground": tokens.get("primary-foreground", "oklch(0.985 0 0)"),
        "secondary": tokens.get("secondary", tokens.get("muted", "oklch(0.97 0 0)")),
        "secondary-foreground": tokens.get("secondary-foreground", tokens.get("foreground", "oklch(0.205 0 0)")),
        "muted": tokens.get("muted", tokens.get("secondary", "oklch(0.97 0 0)")),
        "muted-foreground": tokens.get("muted-foreground", "oklch(0.556 0 0)"),
        "accent": tokens.get("accent", tokens.get("secondary", "oklch(0.97 0 0)")),
        "accent-foreground": tokens.get("accent-foreground", tokens.get("secondary-foreground", "oklch(0.205 0 0)")),
        "destructive": tokens.get("destructive", "oklch(0.5771 0.2152 27.3250)"),
        "destructive-foreground": tokens.get("destructive-foreground", "oklch(1 0 0)"),
        "border": tokens.get("border", tokens.get("input", "oklch(0.922 0 0)")),
        "input": tokens.get("input", tokens.get("border", "oklch(0.922 0 0)")),
        "ring": tokens.get("ring", "oklch(0.708 0 0)"),
        "chart-1": tokens.get("chart-1", "oklch(0.646 0.222 41.116)"),
        "chart-2": tokens.get("chart-2", "oklch(0.6 0.118 184.704)"),
        "chart-3": tokens.get("chart-3", "oklch(0.398 0.07 227.392)"),
        "chart-4": tokens.get("chart-4", "oklch(0.828 0.189 84.429)"),
        "chart-5": tokens.get("chart-5", "oklch(0.769 0.188 70.08)"),
        "sidebar": tokens.get("sidebar", tokens.get("background", "oklch(0.985 0 0)")),
        "sidebar-foreground": tokens.get("sidebar-foreground", tokens.get("foreground", "oklch(0.145 0 0)")),
        "sidebar-primary": tokens.get("sidebar-primary", tokens.get("primary", "oklch(0.205 0 0)")),
        "sidebar-primary-foreground": tokens.get(
            "sidebar-primary-foreground", tokens.get("primary-foreground", "oklch(0.985 0 0)")
        ),
        "sidebar-accent": tokens.get("sidebar-accent", tokens.get("accent", "oklch(0.97 0 0)")),
        "sidebar-accent-foreground": tokens.get(
            "sidebar-accent-foreground", tokens.get("accent-foreground", "oklch(0.205 0 0)")
        ),
        "sidebar-border": tokens.get("sidebar-border", tokens.get("border", "oklch(0.922 0 0)")),
        "sidebar-ring": tokens.get("sidebar-ring", tokens.get("ring", "oklch(0.708 0 0)")),
    }


def _theme_with_defaults(theme: Theme, base_theme: Theme) -> Theme:
    tokens = _resolved_shadcn_tokens(base_theme)
    tokens.update(_resolved_shadcn_tokens(theme))

    spacing = tokens.get("spacing", "0.25rem")
    radius = tokens.get("radius", "0.5rem")
    body_font = tokens.get("font-sans")
    mono_font = tokens.get("font-mono")

    colors = cast(
        ThemeColors,
        {
            **_shadcn_color_overrides(tokens),
            **cast(dict[str, str], base_theme.colors),
            **cast(dict[str, str], theme.colors),
        },
    )
    resolved_colors = cast(dict[ThemeColorName, str], dict(colors))
    components = {
        **base_theme.components,
        **{k: {**base_theme.components.get(k, {}), **v} for k, v in theme.components.items()},
    }
    custom_variables = {
        **{(k if k.startswith("--") else f"--{k}"): v for k, v in tokens.items()},
        **base_theme.custom_variables,
        **theme.custom_variables,
    }

    resolved = Theme(
        mode=theme.mode,
        theme={**base_theme.theme, **theme.theme},
        light=cast(ThemePalette, {**cast(dict[str, str], base_theme.light), **cast(dict[str, str], theme.light)}),
        dark=cast(ThemePalette, {**cast(dict[str, str], base_theme.dark), **cast(dict[str, str], theme.dark)}),
        colors=resolved_colors,
        font_sizes={
            "xs": "0.75rem",
            "sm": "0.875rem",
            "base": "1rem",
            "lg": "1.125rem",
            "xl": "1.25rem",
            "2xl": "1.5rem",
            **base_theme.font_sizes,
            **theme.font_sizes,
        },
        components=cast(dict[ThemeComponentName, dict[ThemeComponentTokenName, str]], components),
        variables=cast(
            ThemeVariables, {**cast(dict[str, str], base_theme.variables), **cast(dict[str, str], theme.variables)}
        ),
        custom_variables=custom_variables,
        extra_css=[*base_theme.extra_css, *theme.extra_css],
    )

    # Backfill spacing/radius/font vars derived from shadcn tokens.
    for key, value in _derive_scale(spacing).items():
        resolved.custom_variables.setdefault(f"--fleur-space-{_normalize_name(key)}", _normalize_length(value))
    for key, value in _derive_radii(radius).items():
        resolved.custom_variables.setdefault(f"--fleur-radius-{_normalize_name(key)}", _normalize_length(value))
    if body_font is not None:
        resolved.custom_variables.setdefault("--fleur-font-body", body_font)
    if mono_font is not None:
        resolved.custom_variables.setdefault("--fleur-font-mono", mono_font)

    return resolved


def theme_variables(theme: Theme, *, base_theme: Theme | None = None) -> dict[str, str]:
    merged = _theme_with_defaults(theme, base_theme or DEFAULT_THEME)

    variables: dict[str, str] = {}
    for key, value in merged.colors.items():
        color_value = cast(str, value)
        variables[f"--{_normalize_name(key)}"] = color_value
        variables[f"--fleur-color-{_normalize_name(key)}"] = color_value

    alias_map: dict[str, ThemeColorName] = {
        "bg-canvas": "background",
        "bg-surface": "card",
        "bg-subtle": "muted",
        "fg-default": "foreground",
        "fg-muted": "muted-foreground",
        "border-default": "border",
        "accent-solid-bg": "primary",
        "accent-solid-fg": "primary-foreground",
        "accent-soft-bg": "accent",
        "accent-soft-fg": "accent-foreground",
        "focus-ring": "ring",
        "overlay": "background",
    }
    for fleur_name, shadcn_name in alias_map.items():
        if shadcn_name in merged.colors:
            variables[f"--fleur-color-{fleur_name}"] = cast(str, merged.colors[shadcn_name])
    for key, value in merged.font_sizes.items():
        variables[f"--fleur-text-{_normalize_name(key)}"] = _normalize_length(value)
    for comp_name, values in merged.components.items():
        comp_key = _normalize_name(comp_name)
        for key, value in values.items():
            variables[f"--fleur-comp-{comp_key}-{_normalize_name(key)}"] = value
    variables.update(cast(dict[str, str], merged.variables))
    variables.update(merged.custom_variables)
    return variables


def theme_style_tag(theme: Theme, *, base_theme: Theme | None = None) -> str:
    merged = _theme_with_defaults(theme, base_theme or DEFAULT_THEME)
    variables = theme_variables(theme, base_theme=base_theme)
    declarations = "".join(f"{name}: {value};" for name, value in variables.items())
    base = (
        "*,:before,:after{box-sizing:border-box;}"
        "html,body{margin:0;padding:0;}"
        "body{"
        "font-size:var(--fleur-text-base);"
        "font-family:var(--fleur-font-body);"
        "background:var(--fleur-color-bg-canvas);"
        "color:var(--fleur-color-fg-default);"
        "line-height:1.5;"
        "text-rendering:optimizeLegibility;"
        "-webkit-font-smoothing:antialiased;"
        "-moz-osx-font-smoothing:grayscale;"
        "}"
        "button,input,select,textarea{font:inherit;color:inherit;}"
        "button{appearance:none;-webkit-appearance:none;background:none;border:0;cursor:pointer;transition:background-color .15s ease,color .15s ease,border-color .15s ease,box-shadow .15s ease;}"
        "button:disabled{cursor:not-allowed;opacity:.55;}"
        "hr{border:0;border-top:1px solid var(--fleur-color-border-default);margin:0;}"
        ":focus-visible{outline:none;box-shadow:var(--fleur-comp-button-focus-ring);border-radius:var(--fleur-radius-sm);}"
    )
    extra_css = "".join(merged.extra_css)
    return f"<style>:root{{{declarations}}}{base}{extra_css}</style>"


def apply_theme(page: Page, theme: Theme, *, base_theme: Theme | None = None) -> Page:
    extra_head_html = [*page.extra_head_html, theme_style_tag(theme, base_theme=base_theme)]
    return replace(page, extra_head_html=extra_head_html)


__all__ = [
    "Theme",
    "ThemeColorName",
    "ThemeComponentName",
    "ThemeComponentTokenName",
    "ThemeColors",
    "ThemeCoreTokens",
    "ThemeFontSizeName",
    "ThemeMode",
    "ThemePalette",
    "ThemeRadiusName",
    "ThemeSpaceName",
    "ThemeTypographyName",
    "ThemeVariables",
    "DEFAULT_THEME",
    "BASIC_THEME",
    "ZEN_THEME",
    "apply_theme",
    "theme_style_tag",
    "theme_variables",
]
