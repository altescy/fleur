from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from hashlib import blake2b
from importlib.resources import files
from typing import cast, get_args, get_type_hints

from fleur.core.template import Page
from fleur.ui._css import CssValue, color_reference

from . import _utils
from .base import (
    Theme,
    ThemeColorName,
    ThemeColors,
    ThemeComponents,
    ThemeCoreTokens,
    ThemeFontSizeName,
    ThemeMode,
    ThemePalette,
    ThemeRadiusName,
    ThemeSelection,
    ThemeSpaceName,
    ThemeTypographyName,
)
from .basic import BASIC_THEME
from .zen import ZEN_THEME

DEFAULT_THEME = BASIC_THEME

_COLOR_ALIASES: dict[str, ThemeColorName] = {
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


def _component_variable(component: str, field: str) -> str:
    return f"--fleur-comp-{component}-{field.replace('_', '-')}"


def _component_variables(components: ThemeComponents) -> dict[str, str]:
    settings = cast(Mapping[str, Mapping[str, str | int | float | CssValue]], components)
    variables: dict[str, str] = {}
    for component, fields in settings.items():
        for field, value in fields.items():
            if isinstance(value, CssValue):
                if not isinstance(value.value, str):
                    raise TypeError("Theme component styles require literal CSS values")
                resolved = value.value
            elif field in ("bg", "fg") and isinstance(value, str):
                resolved = color_reference(value)
            elif field == "radius":
                resolved = f"var(--fleur-radius-{value})" if isinstance(value, str) else _utils.normalize_length(value)
            else:
                resolved = str(value)
            variables[_component_variable(component, field)] = resolved
    return variables


def theme_variables(theme: Theme, *, base_theme: Theme | None = None) -> dict[str, str]:
    """Resolve each layer in the requested mode, starting with the complete BASIC palette."""
    layers = (BASIC_THEME, base_theme, theme) if base_theme is not None else (BASIC_THEME, theme)
    tokens: dict[str, str] = {}
    space: dict[ThemeSpaceName, int | float | str] = {}
    radii: dict[ThemeRadiusName, int | float | str] = {}
    variables: dict[str, str] = {}
    for layer in layers:
        palette = layer.dark if theme.mode == "dark" else layer.light
        for group in (layer.theme, layer.colors, palette):
            tokens.update(cast(dict[str, str], group))
        space.update(layer.space)
        radii.update(layer.radii)
        for key, value in layer.font_sizes.items():
            variables[f"--fleur-text-{key}"] = _utils.normalize_length(value)
        variables.update(_component_variables(layer.components))

    variables.update({f"--{key}": value for key, value in tokens.items()})
    for key in get_args(ThemeColorName):
        color = tokens[key]
        variables[f"--fleur-color-{key}"] = _utils.css_color(color)
    for fleur_name, shadcn_name in _COLOR_ALIASES.items():
        variables[f"--fleur-color-{fleur_name}"] = variables[f"--fleur-color-{shadcn_name}"]
    for key, size in {**_derive_scale(tokens["spacing"]), **space}.items():
        variables[f"--fleur-space-{key}"] = _utils.normalize_length(size)
    for key, size in {**_derive_radii(tokens["radius"]), **radii}.items():
        variables[f"--fleur-radius-{key}"] = _utils.normalize_length(size)
    variables["--fleur-font-body"] = tokens["font-sans"]
    variables["--fleur-font-mono"] = tokens["font-mono"]
    return variables


def _declarations(values: dict[str, str]) -> str:
    return "".join(f"{name}: {value};" for name, value in values.items())


def _mode_rules(theme: Theme, base_theme: Theme | None, current: dict[str, str]) -> str:
    other_mode: ThemeMode = "light" if theme.mode == "dark" else "dark"
    other = theme_variables(replace(theme, mode=other_mode), base_theme=base_theme)
    # Only mode-dependent inputs need switching. An enclosing scope's override stays in force.
    aliases = {f"--fleur-color-{alias}": f"var(--fleur-color-{color})" for alias, color in _COLOR_ALIASES.items()}
    changed = sorted(
        name for name in current.keys() | other.keys() if current.get(name) != other.get(name) and name not in aliases
    )
    rules: list[str] = []
    for mode, palette in ((theme.mode, current), (other_mode, other)):
        values = {
            name: f"var({_utils.scope_variable(name)}, {palette[name]})"
            if name in palette
            else f"var({_utils.scope_variable(name)})"
            for name in changed
        }
        rules.append(f'[data-fleur-mode="{mode}"]{{color-scheme:{mode};--fleur-mode:{mode};{_declarations(values)}}}')

    return "".join(rules) + _scope_recipes(current)


def _scope_recipes(variables: dict[str, str], *, scoped: bool = False) -> str:
    # Resolve var() at each scope so component recipes use local overrides.
    recipes = {f"--fleur-color-{alias}": f"var(--fleur-color-{color})" for alias, color in _COLOR_ALIASES.items()}
    recipes.update({key: value for key, value in variables.items() if key.startswith("--fleur-comp-")})
    scope = ":where(:scope, [data-fleur-scope])" if scoped else ":where([data-fleur-scope])"
    return f"{scope}{{{_declarations(recipes)}}}"


def _scope_component_css(components: ThemeComponents) -> tuple[str, str] | None:
    declarations = _declarations(_component_variables(components))
    if not declarations:
        return None
    # Explicit scope roots keep sibling regions isolated in WebKit.
    key = blake2b(declarations.encode(), digest_size=16).hexdigest()
    # :is() gives explicit overrides priority over theme defaults. Between overrides,
    # scoping proximity chooses the closest region. Rebind references at every ThemeScope.
    css = f'@scope ([data-fleur-components="{key}"]){{:is(:scope,[data-fleur-scope]){{{declarations}}}}}'
    return key, css


def _scoped_theme_css(theme: Theme) -> str:
    light = theme_variables(replace(theme, mode="light"))
    dark = theme_variables(replace(theme, mode="dark"))
    aliases = {f"--fleur-color-{alias}" for alias in _COLOR_ALIASES}
    # Optional core tokens may exist only on the enclosing theme or in one mode.
    keys = (light.keys() | dark.keys() | {f"--{key}" for key in ThemeCoreTokens.__optional_keys__}) - aliases
    inputs = sorted(key for key in keys if not key.startswith("--fleur-comp-"))

    def palette(values: dict[str, str], names: list[str]) -> str:
        return _declarations({key: f"var({_utils.scope_variable(key)}, {values.get(key, 'initial')})" for key in names})

    changed = [key for key in inputs if light.get(key) != dark.get(key)]
    common = [key for key in inputs if light.get(key) == dark.get(key)]
    light_changes = palette(light, changed)
    dark_changes = palette(dark, changed)
    # @scope without a start selector is rooted at the parent of this style element.
    # Mode boundaries inside it use this theme until another theme scope begins.
    for component, style in get_type_hints(ThemeComponents).items():
        for field in style.__annotations__:
            light.setdefault(_component_variable(component, field), "initial")
    return (
        "@scope to ([data-fleur-theme]){"
        f":scope,[data-fleur-mode]{{{palette(light, common)}}}"
        f':scope,[data-fleur-mode="light"]{{{light_changes}}}'
        f"@container style(--fleur-mode: dark){{:scope:where(:not([data-fleur-mode])){{{dark_changes}}}}}"
        f':scope:where([data-fleur-mode="dark"]),[data-fleur-mode="dark"]{{{dark_changes}}}'
        f"{_scope_recipes(light, scoped=True)}{''.join(theme.extra_css)}"
        "}"
    )


def theme_style_tag(theme: Theme, *, base_theme: Theme | None = None) -> str:
    variables = theme_variables(theme, base_theme=base_theme)
    declarations = _declarations(variables)
    root_css = f":root{{color-scheme:{theme.mode};--fleur-mode:{theme.mode};{declarations}}}"
    mode_css = _mode_rules(theme, base_theme, variables)
    styles = files(__name__)
    base = styles.joinpath("base.css").read_text(encoding="utf-8")
    elements = styles.joinpath("elements.css").read_text(encoding="utf-8")
    extra_css = "".join([*(base_theme.extra_css if base_theme is not None else []), *theme.extra_css])
    return f"<style>{root_css}{mode_css}{base}{elements}{extra_css}</style>"


def apply_theme(page: Page, theme: Theme, *, base_theme: Theme | None = None) -> Page:
    extra_head_html = [*page.extra_head_html, theme_style_tag(theme, base_theme=base_theme)]
    return replace(page, extra_head_html=extra_head_html)


__all__ = [
    "Theme",
    "ThemeColorName",
    "ThemeComponents",
    "ThemeColors",
    "ThemeCoreTokens",
    "ThemeFontSizeName",
    "ThemeMode",
    "ThemePalette",
    "ThemeSelection",
    "ThemeRadiusName",
    "ThemeSpaceName",
    "ThemeTypographyName",
    "DEFAULT_THEME",
    "BASIC_THEME",
    "ZEN_THEME",
    "apply_theme",
    "theme_style_tag",
    "theme_variables",
]
