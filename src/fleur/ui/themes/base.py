from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias, TypedDict, cast

ThemeColorName: TypeAlias = Literal[
    "background",
    "foreground",
    "card",
    "card-foreground",
    "popover",
    "popover-foreground",
    "primary",
    "primary-foreground",
    "secondary",
    "secondary-foreground",
    "muted",
    "muted-foreground",
    "accent",
    "accent-foreground",
    "destructive",
    "destructive-foreground",
    "border",
    "input",
    "ring",
    "chart-1",
    "chart-2",
    "chart-3",
    "chart-4",
    "chart-5",
    "sidebar",
    "sidebar-foreground",
    "sidebar-primary",
    "sidebar-primary-foreground",
    "sidebar-accent",
    "sidebar-accent-foreground",
    "sidebar-border",
    "sidebar-ring",
]
ThemeSpaceName: TypeAlias = Literal["xs", "sm", "md", "lg", "xl"]
ThemeRadiusName: TypeAlias = Literal["sm", "md", "lg"]
ThemeFontSizeName: TypeAlias = Literal["xs", "sm", "base", "lg", "xl", "2xl"]
ThemeTypographyName: TypeAlias = Literal["body", "mono"]
ThemeComponentName: TypeAlias = Literal["button", "panel", "input"]
ThemeComponentTokenName: TypeAlias = Literal["bg", "fg", "radius", "font-weight", "focus-ring", "border"]
ThemeMode: TypeAlias = Literal["light", "dark"]


ThemeCoreTokens = TypedDict(
    "ThemeCoreTokens",
    {
        "font-sans": str,
        "font-mono": str,
        "font-serif": str,
        "spacing": str,
        "radius": str,
        "tracking-normal": str,
        "tracking-tight": str,
        "tracking-tighter": str,
        "tracking-wide": str,
        "tracking-wider": str,
        "tracking-widest": str,
        "letter-spacing": str,
        "shadow-color": str,
        "shadow-opacity": str,
        "shadow-blur": str,
        "shadow-spread": str,
        "shadow-offset-x": str,
        "shadow-offset-y": str,
        "shadow-2xs": str,
        "shadow-xs": str,
        "shadow-sm": str,
        "shadow": str,
        "shadow-md": str,
        "shadow-lg": str,
        "shadow-xl": str,
        "shadow-2xl": str,
    },
    total=False,
)


ThemePalette = TypedDict(
    "ThemePalette",
    {
        "background": str,
        "foreground": str,
        "card": str,
        "card-foreground": str,
        "popover": str,
        "popover-foreground": str,
        "primary": str,
        "primary-foreground": str,
        "secondary": str,
        "secondary-foreground": str,
        "muted": str,
        "muted-foreground": str,
        "accent": str,
        "accent-foreground": str,
        "destructive": str,
        "destructive-foreground": str,
        "border": str,
        "input": str,
        "ring": str,
        "chart-1": str,
        "chart-2": str,
        "chart-3": str,
        "chart-4": str,
        "chart-5": str,
        "sidebar": str,
        "sidebar-foreground": str,
        "sidebar-primary": str,
        "sidebar-primary-foreground": str,
        "sidebar-accent": str,
        "sidebar-accent-foreground": str,
        "sidebar-border": str,
        "sidebar-ring": str,
        "spacing": str,
        "radius": str,
        "font-sans": str,
        "font-mono": str,
        "font-serif": str,
    },
    total=False,
)


ThemeColors = TypedDict(
    "ThemeColors",
    {
        "background": str,
        "foreground": str,
        "card": str,
        "card-foreground": str,
        "popover": str,
        "popover-foreground": str,
        "primary": str,
        "primary-foreground": str,
        "secondary": str,
        "secondary-foreground": str,
        "muted": str,
        "muted-foreground": str,
        "accent": str,
        "accent-foreground": str,
        "destructive": str,
        "destructive-foreground": str,
        "border": str,
        "input": str,
        "ring": str,
        "chart-1": str,
        "chart-2": str,
        "chart-3": str,
        "chart-4": str,
        "chart-5": str,
        "sidebar": str,
        "sidebar-foreground": str,
        "sidebar-primary": str,
        "sidebar-primary-foreground": str,
        "sidebar-accent": str,
        "sidebar-accent-foreground": str,
        "sidebar-border": str,
        "sidebar-ring": str,
    },
)


ThemeVariables = TypedDict(
    "ThemeVariables",
    {
        "--spacing": str,
        "--radius": str,
        "--font-sans": str,
        "--font-mono": str,
        "--font-serif": str,
        "--tracking-normal": str,
        "--tracking-tight": str,
        "--tracking-tighter": str,
        "--tracking-wide": str,
        "--tracking-wider": str,
        "--tracking-widest": str,
        "--letter-spacing": str,
        "--shadow-color": str,
        "--shadow-opacity": str,
        "--shadow-blur": str,
        "--shadow-spread": str,
        "--shadow-offset-x": str,
        "--shadow-offset-y": str,
        "--shadow-2xs": str,
        "--shadow-xs": str,
        "--shadow-sm": str,
        "--shadow": str,
        "--shadow-md": str,
        "--shadow-lg": str,
        "--shadow-xl": str,
        "--shadow-2xl": str,
    },
    total=False,
)


def _default_theme_core_tokens() -> ThemeCoreTokens:
    return cast(ThemeCoreTokens, {})


def _default_theme_palette() -> ThemePalette:
    return cast(ThemePalette, {})


def _default_theme_variables() -> ThemeVariables:
    return cast(ThemeVariables, {})


def _default_theme_colors() -> ThemeColors:
    return cast(
        ThemeColors,
        {
            "background": "oklch(1 0 0)",
            "foreground": "oklch(0.145 0 0)",
            "card": "oklch(1 0 0)",
            "card-foreground": "oklch(0.145 0 0)",
            "popover": "oklch(1 0 0)",
            "popover-foreground": "oklch(0.145 0 0)",
            "primary": "oklch(0.205 0 0)",
            "primary-foreground": "oklch(0.985 0 0)",
            "secondary": "oklch(0.97 0 0)",
            "secondary-foreground": "oklch(0.205 0 0)",
            "muted": "oklch(0.97 0 0)",
            "muted-foreground": "oklch(0.556 0 0)",
            "accent": "oklch(0.97 0 0)",
            "accent-foreground": "oklch(0.205 0 0)",
            "destructive": "oklch(0.5771 0.2152 27.3250)",
            "destructive-foreground": "oklch(1 0 0)",
            "border": "oklch(0.922 0 0)",
            "input": "oklch(0.922 0 0)",
            "ring": "oklch(0.708 0 0)",
            "chart-1": "oklch(0.646 0.222 41.116)",
            "chart-2": "oklch(0.6 0.118 184.704)",
            "chart-3": "oklch(0.398 0.07 227.392)",
            "chart-4": "oklch(0.828 0.189 84.429)",
            "chart-5": "oklch(0.769 0.188 70.08)",
            "sidebar": "oklch(0.985 0 0)",
            "sidebar-foreground": "oklch(0.145 0 0)",
            "sidebar-primary": "oklch(0.205 0 0)",
            "sidebar-primary-foreground": "oklch(0.985 0 0)",
            "sidebar-accent": "oklch(0.97 0 0)",
            "sidebar-accent-foreground": "oklch(0.205 0 0)",
            "sidebar-border": "oklch(0.922 0 0)",
            "sidebar-ring": "oklch(0.708 0 0)",
        },
    )


@dataclass(slots=True)
class Theme:
    mode: ThemeMode = "light"
    theme: ThemeCoreTokens = field(default_factory=_default_theme_core_tokens)
    light: ThemePalette = field(default_factory=_default_theme_palette)
    dark: ThemePalette = field(default_factory=_default_theme_palette)
    colors: dict[ThemeColorName, str] = field(default_factory=dict)
    font_sizes: dict[ThemeFontSizeName, int | float | str] = field(default_factory=dict)
    components: dict[ThemeComponentName, dict[ThemeComponentTokenName, str]] = field(default_factory=dict)
    variables: ThemeVariables = field(default_factory=_default_theme_variables)
    custom_variables: dict[str, str] = field(default_factory=dict)
    extra_css: list[str] = field(default_factory=list)


def _normalize_name(name: str | int) -> str:
    return str(name).strip().replace("_", "-")


def _normalize_length(value: int | float | str) -> str:
    if isinstance(value, (int, float)):
        return f"{value}px"
    return value
