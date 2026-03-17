from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Literal, TypeAlias

from fleur.core.template import Page

ThemeColorName: TypeAlias = Literal[
    "bg-canvas",
    "bg-surface",
    "bg-subtle",
    "fg-default",
    "fg-muted",
    "border-default",
    "accent-solid-bg",
    "accent-solid-fg",
    "accent-soft-bg",
    "accent-soft-fg",
    "focus-ring",
    "overlay",
]
ThemeSpaceName: TypeAlias = Literal["xs", "sm", "md", "lg", "xl"]
ThemeRadiusName: TypeAlias = Literal["sm", "md", "lg"]
ThemeTypographyName: TypeAlias = Literal["body", "mono"]
ThemeSemanticName: TypeAlias = Literal["bg-canvas", "bg-surface", "fg-default", "fg-muted", "border-default"]
ThemeComponentName: TypeAlias = Literal["button", "panel", "input"]
ThemeComponentTokenName: TypeAlias = Literal["bg", "fg", "radius", "font-weight", "focus-ring", "border"]


@dataclass(slots=True)
class Theme:
    colors: dict[ThemeColorName, str] = field(default_factory=dict)
    space: dict[ThemeSpaceName, int | float | str] = field(default_factory=dict)
    radii: dict[ThemeRadiusName, int | float | str] = field(default_factory=dict)
    typography: dict[ThemeTypographyName, str] = field(default_factory=dict)
    semantic: dict[ThemeSemanticName, str] = field(default_factory=dict)
    components: dict[ThemeComponentName, dict[ThemeComponentTokenName, str]] = field(default_factory=dict)


DEFAULT_THEME = Theme(
    colors={
        "bg-canvas": "#f8fafc",
        "bg-surface": "#ffffff",
        "bg-subtle": "#f1f5f9",
        "fg-default": "#0f172a",
        "fg-muted": "#475569",
        "border-default": "#cbd5e1",
        "accent-solid-bg": "#0f766e",
        "accent-solid-fg": "#ffffff",
        "accent-soft-bg": "#ccfbf1",
        "accent-soft-fg": "#134e4a",
        "focus-ring": "#22d3ee",
        "overlay": "rgba(2, 6, 23, 0.42)",
    },
    space={
        "xs": 6,
        "sm": 10,
        "md": 14,
        "lg": 20,
        "xl": 28,
    },
    radii={
        "sm": 8,
        "md": 12,
        "lg": 16,
    },
    typography={
        "body": '"Avenir Next", "Segoe UI", "Helvetica Neue", sans-serif',
        "mono": '"SFMono-Regular", Menlo, Consolas, monospace',
    },
    semantic={
        "bg-canvas": "var(--fleur-color-bg-canvas)",
        "bg-surface": "var(--fleur-color-bg-surface)",
        "fg-default": "var(--fleur-color-fg-default)",
        "fg-muted": "var(--fleur-color-fg-muted)",
        "border-default": "var(--fleur-color-border-default)",
    },
    components={
        "button": {
            "bg": "var(--fleur-color-accent-solid-bg)",
            "fg": "var(--fleur-color-accent-solid-fg)",
            "radius": "var(--fleur-radius-md)",
            "font-weight": "600",
            "focus-ring": "0 0 0 3px color-mix(in srgb, var(--fleur-color-focus-ring) 40%, transparent)",
            "border": "none",
        },
        "panel": {
            "bg": "var(--fleur-color-bg-surface)",
            "fg": "var(--fleur-color-fg-default)",
            "border": "1px solid var(--fleur-color-border-default)",
            "radius": "var(--fleur-radius-md)",
        },
        "input": {
            "bg": "var(--fleur-color-bg-surface)",
            "fg": "var(--fleur-color-fg-default)",
            "border": "1px solid var(--fleur-color-border-default)",
            "radius": "var(--fleur-radius-sm)",
        },
    },
)


def _normalize_name(name: str | int) -> str:
    return str(name).strip().replace("_", "-")


def _normalize_length(value: int | float | str) -> str:
    if isinstance(value, (int, float)):
        return f"{value}px"
    return value


def theme_variables(theme: Theme) -> dict[str, str]:
    merged = Theme(
        colors={**DEFAULT_THEME.colors, **theme.colors},
        space={**DEFAULT_THEME.space, **theme.space},
        radii={**DEFAULT_THEME.radii, **theme.radii},
        typography={**DEFAULT_THEME.typography, **theme.typography},
        semantic={**DEFAULT_THEME.semantic, **theme.semantic},
        components={
            **DEFAULT_THEME.components,
            **{k: {**DEFAULT_THEME.components.get(k, {}), **v} for k, v in theme.components.items()},
        },
    )

    variables: dict[str, str] = {}

    for key, value in merged.colors.items():
        variables[f"--fleur-color-{_normalize_name(key)}"] = value

    for key, value in merged.space.items():
        variables[f"--fleur-space-{_normalize_name(key)}"] = _normalize_length(value)

    for key, value in merged.radii.items():
        variables[f"--fleur-radius-{_normalize_name(key)}"] = _normalize_length(value)

    for key, value in merged.typography.items():
        variables[f"--fleur-font-{_normalize_name(key)}"] = value

    for key, value in merged.semantic.items():
        variables[f"--fleur-sem-{_normalize_name(key)}"] = value

    for comp_name, values in merged.components.items():
        comp_key = _normalize_name(comp_name)
        for key, value in values.items():
            variables[f"--fleur-comp-{comp_key}-{_normalize_name(key)}"] = value

    return variables


def theme_style_tag(theme: Theme) -> str:
    variables = theme_variables(theme)
    declarations = "".join(f"{name}: {value};" for name, value in variables.items())
    base = (
        "*,:before,:after{box-sizing:border-box;}"
        "html,body{margin:0;padding:0;}"
        "body{"
        "font-family:var(--fleur-font-body);"
        "background:var(--fleur-sem-bg-canvas);"
        "color:var(--fleur-sem-fg-default);"
        "text-rendering:optimizeLegibility;"
        "-webkit-font-smoothing:antialiased;"
        "-moz-osx-font-smoothing:grayscale;"
        "}"
        "button,input,select,textarea{font:inherit;color:inherit;}"
        "button{appearance:none;-webkit-appearance:none;background:none;border:0;cursor:pointer;}"
        "hr{border:0;border-top:1px solid var(--fleur-sem-border-default);margin:0;}"
        ":focus-visible{outline:none;box-shadow:var(--fleur-comp-button-focus-ring);border-radius:var(--fleur-radius-sm);}"
    )
    return f"<style>:root{{{declarations}}}{base}</style>"


def apply_theme(page: Page, theme: Theme) -> Page:
    extra_head_html = [*page.extra_head_html, theme_style_tag(theme)]
    return replace(page, extra_head_html=extra_head_html)
