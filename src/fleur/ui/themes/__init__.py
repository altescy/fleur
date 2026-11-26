from __future__ import annotations

from dataclasses import replace
from importlib.resources import files
from typing import cast, get_args

from fleur.core.template import Page

from . import _utils
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
        for component, settings in layer.components.items():
            for key, value in settings.items():
                variables[f"--fleur-comp-{component}-{key}"] = value

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
    button_bg = "--fleur-comp-button-bg"
    recipes.update(
        {key: value for key, value in variables.items() if key.startswith("--fleur-comp-") and key != button_bg}
    )
    scope = ":where(:scope, [data-fleur-scope])" if scoped else ":where([data-fleur-scope])"
    return (
        f"{scope}{{{_declarations(recipes)}}}"
        f"{scope}:where(:not([data-fleur-button-bg] *)){{{button_bg}:{variables[button_bg]};}}"
    )


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
    for component in get_args(ThemeComponentName):
        for token in get_args(ThemeComponentTokenName):
            light.setdefault(f"--fleur-comp-{component}-{token}", "initial")
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
    base = (
        "*,:before,:after{box-sizing:border-box;}"
        "*{border-color:var(--fleur-color-border);outline-color:color-mix(in srgb,var(--fleur-color-ring) 50%,transparent);}"
        "html,body{margin:0;padding:0;}"
        "html{line-height:1.5;-webkit-text-size-adjust:100%;tab-size:4;font-family:var(--fleur-font-body);}"
        ":where([data-fleur-scope][data-fleur-mode],[data-fleur-theme]){background-color:var(--fleur-color-bg-canvas);color:var(--fleur-color-fg-default);font-family:var(--fleur-font-body);}"
        ":where([data-fleur-theme]){font-size:var(--fleur-text-base);}"
        ":where([data-fleur-scope-foreground]){color:var(--fleur-color-foreground);}"
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
        "::selection{background:var(--fleur-color-selection);color:var(--fleur-color-selection-foreground);}"
        "a{color:inherit;text-decoration:underline;text-decoration-color:color-mix(in srgb,var(--fleur-color-foreground) 35%,transparent);text-underline-offset:.2em;}"
        "a:hover{text-decoration-color:currentColor;}"
        "h1,h2,h3,h4,h5,h6,p,figure,blockquote,dl,dd{margin:0;}"
        "p{line-height:1.7;}"
        "small{font-size:var(--fleur-text-sm);}"
        "strong,b{font-weight:600;}"
        "em,i{font-style:italic;}"
        "code,kbd,samp,pre{font-family:var(--fleur-font-mono);}"
        "code,kbd,samp{font-size:.9em;}"
        "code{background:var(--fleur-color-code);color:var(--fleur-color-code-foreground);border-radius:var(--fleur-radius-sm);padding:.125em .375em;}"
        "pre{margin:0;overflow:auto;background:var(--fleur-color-code);color:var(--fleur-color-code-foreground);border-radius:var(--fleur-radius-md);padding:calc(var(--fleur-space-md) + var(--fleur-space-xs));}"
        "pre code{background:transparent;color:inherit;padding:0;border-radius:0;}"
        "kbd{background:var(--fleur-color-surface);border:1px solid var(--fleur-color-border);border-bottom-width:2px;border-radius:var(--fleur-radius-sm);padding:.125em .375em;}"
        "mark{background:color-mix(in srgb,var(--fleur-color-accent) 55%,transparent);color:inherit;}"
        "blockquote{margin:0;padding-left:1rem;border-left:3px solid var(--fleur-color-border);color:var(--fleur-color-muted-foreground);font-style:italic;}"
        "ul,ol{margin:0;padding-left:1.375rem;}"
        "li{margin:0;}"
        "table{border-collapse:collapse;border-spacing:0;width:100%;}"
        "caption{caption-side:bottom;color:var(--fleur-color-muted-foreground);font-size:var(--fleur-text-sm);padding-top:var(--fleur-space-sm);text-align:left;}"
        "th,td{padding:calc(var(--fleur-space-sm) + var(--fleur-space-xs)) var(--fleur-space-md);border-bottom:1px solid var(--fleur-color-border);text-align:left;vertical-align:top;}"
        "th{font-weight:600;color:var(--fleur-color-fg-default);}"
        "img,svg,video,canvas,audio,iframe,embed,object{display:block;max-width:100%;}"
        "img,video{height:auto;}"
        "button,input,select,textarea{font:inherit;color:inherit;}"
        "input:where(:not([data-fleur-ui])),select,textarea{background:var(--fleur-color-card);border:1px solid var(--fleur-color-input);border-radius:var(--fleur-radius-sm);padding:var(--fleur-space-sm) var(--fleur-space-md);}"
        "button{appearance:none;-webkit-appearance:none;background:none;border:0;cursor:pointer;transition:background-color .15s ease,color .15s ease,border-color .15s ease,box-shadow .15s ease;}"
        ":where([data-fleur-bg]),:is(button,input,select,textarea):where([data-fleur-bg]){background:var(--fleur-local-bg);}"
        "button:disabled{cursor:not-allowed;opacity:.55;}"
        "fieldset{margin:0;padding:0;border:0;min-width:0;}"
        "legend{padding:0;}"
        "hr{border:0;border-top:1px solid var(--fleur-color-border-default);margin:0;}"
        ":focus-visible:where(:not([data-fleur-ui])){outline:none;box-shadow:var(--fleur-comp-button-focus-ring);border-radius:var(--fleur-radius-sm);}"
    )
    extra_css = "".join([*(base_theme.extra_css if base_theme is not None else []), *theme.extra_css])
    elements = files(__name__).joinpath("elements.css").read_text(encoding="utf-8")
    return f"<style>:root{{color-scheme:{theme.mode};--fleur-mode:{theme.mode};{declarations}}}{_mode_rules(theme, base_theme, variables)}{base}{elements}{extra_css}</style>"


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
