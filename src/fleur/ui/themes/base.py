from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal, TypeAlias, TypedDict

from fleur.core.expr import Expr
from fleur.core.types import KeyT

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
    "surface",
    "surface-foreground",
    "code",
    "code-foreground",
    "code-highlight",
    "code-number",
    "selection",
    "selection-foreground",
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
        "surface": str,
        "surface-foreground": str,
        "code": str,
        "code-foreground": str,
        "code-highlight": str,
        "code-number": str,
        "selection": str,
        "selection-foreground": str,
    },
    total=False,
)


class ThemePalette(ThemeCoreTokens, ThemeColors):
    """Overrides for one mode, including imported shadcn core variables."""


@dataclass(slots=True, kw_only=True)
class Theme:
    """Shared tokens are applied first, then the palette for the selected mode."""

    mode: ThemeMode = "light"
    theme: ThemeCoreTokens = field(default_factory=ThemeCoreTokens)
    colors: ThemeColors = field(default_factory=ThemeColors)
    light: ThemePalette = field(default_factory=ThemePalette)
    dark: ThemePalette = field(default_factory=ThemePalette)
    space: dict[ThemeSpaceName, int | float | str] = field(default_factory=dict)
    radii: dict[ThemeRadiusName, int | float | str] = field(default_factory=dict)
    font_sizes: dict[ThemeFontSizeName, int | float | str] = field(default_factory=dict)
    components: dict[ThemeComponentName, dict[ThemeComponentTokenName, str]] = field(default_factory=dict)
    extra_css: list[str] = field(default_factory=list)

    @staticmethod
    def select(name: KeyT | Expr[KeyT], choices: Mapping[KeyT, Theme]) -> Theme | ThemeSelection:
        """Select a Python theme by a literal or reactive key."""
        if not isinstance(name, Expr):
            return choices[name]
        return ThemeSelection(name, {key: theme for key, theme in choices.items()})


@dataclass(frozen=True, slots=True)
class ThemeSelection:
    name: Expr[str]
    choices: Mapping[str, Theme]
