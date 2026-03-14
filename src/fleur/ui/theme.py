from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Generic

from typing_extensions import TypeVar

from fleur.core.template import Page

ColorT = TypeVar("ColorT", bound=str, default=str)
SpaceT = TypeVar("SpaceT", bound=str | int, default=str | int)
RadiusT = TypeVar("RadiusT", bound=str, default=str)
TypographyT = TypeVar("TypographyT", bound=str, default=str)


@dataclass(slots=True)
class Theme(Generic[ColorT, SpaceT, RadiusT, TypographyT]):
    colors: dict[ColorT, str] = field(default_factory=dict)
    space: dict[SpaceT, int | float | str] = field(default_factory=dict)
    radii: dict[RadiusT, int | float | str] = field(default_factory=dict)
    typography: dict[TypographyT, str] = field(default_factory=dict)


def _normalize_name(name: str | int) -> str:
    return str(name).strip().replace("_", "-")


def _normalize_length(value: int | float | str) -> str:
    if isinstance(value, (int, float)):
        return f"{value}px"
    return value


def theme_variables(theme: Theme) -> dict[str, str]:
    variables: dict[str, str] = {}

    for key, value in theme.colors.items():
        variables[f"--fleur-color-{_normalize_name(key)}"] = value

    for key, value in theme.space.items():
        variables[f"--fleur-space-{_normalize_name(key)}"] = _normalize_length(value)

    for key, value in theme.radii.items():
        variables[f"--fleur-radius-{_normalize_name(key)}"] = _normalize_length(value)

    for key, value in theme.typography.items():
        variables[f"--fleur-font-{_normalize_name(key)}"] = value

    return variables


def theme_style_tag(theme: Theme) -> str:
    variables = theme_variables(theme)
    declarations = "".join(f"{name}: {value};" for name, value in variables.items())
    return f"<style>:root{{{declarations}}}</style>"


def apply_theme(page: Page, theme: Theme) -> Page:
    extra_head_html = [*page.extra_head_html, theme_style_tag(theme)]
    return replace(page, extra_head_html=extra_head_html)
