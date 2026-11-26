from collections.abc import Mapping
from typing import Unpack, cast

from fleur.core.array import Array
from fleur.core.cond import Cond
from fleur.core.expr import Expr, array, string
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import View, ViewChild, ViewProp, ViewProps
from fleur.ui.views._utils import extend_props, merge_props
from fleur.ui.views.base import Element
from fleur.ui.views.types import ViewStyleArgs

from . import _scope_component_css, _scoped_theme_css
from ._utils import css_color, normalize_length, scope_variable
from .base import Theme, ThemeColors, ThemeComponents, ThemeMode, ThemeSelection, ThemeSpaceName


class ThemeScope(Element[ModelT_co, MsgGroupT_co]):
    """A region inheriting the page theme with optional local token and mode overrides."""

    def __init__(
        self,
        *children: ViewChild,
        theme: Theme | ThemeSelection | None = None,
        mode: ThemeMode | Expr[ThemeMode] | None = None,
        colors: ThemeColors | None = None,
        space: Mapping[ThemeSpaceName, str | int | float] | None = None,
        components: ThemeComponents | None = None,
        props: ViewProps | None = None,
        **styles: Unpack[ViewStyleArgs],
    ) -> None:
        values: dict[str, str] = {}
        for key, value in cast(Mapping[str, str], colors or {}).items():
            values[f"--{key}"] = value
            values[f"--fleur-color-{key}"] = css_color(value)
        for key, size in (space or {}).items():
            values[f"--fleur-space-{key}"] = normalize_length(size)
        # Keep a separate inherited value for mode boundaries inside this override.
        declarations = {scope_variable(key): value for key, value in values.items()}
        declarations.update(values)
        attrs: dict[str, ViewProp] = {"data-fleur-scope": ""}
        sheet: str | Expr[str] = ""
        if isinstance(theme, ThemeSelection):
            registered = Array.includes(array(list(theme.choices)), theme.name)
            attrs["data-fleur-theme"] = Cond.when(registered, "", None)
            sheet = string("")
            for name, preset in theme.choices.items():
                sheet = Cond.when(Cond.equal(theme.name, name), _scoped_theme_css(preset), sheet)
        elif theme is not None:
            attrs["data-fleur-theme"] = ""
            sheet = _scoped_theme_css(theme)
        component_scope = _scope_component_css(components) if components else None
        if component_scope is not None:
            key, css = component_scope
            attrs["data-fleur-components"] = key
            sheet = sheet + css
        if isinstance(sheet, Expr) or sheet:
            css_text = string(sheet) if isinstance(sheet, str) else sheet
            children = (View(css_text, tag="style", props={}), *children)
        if colors is not None and "foreground" in colors:
            attrs["data-fleur-scope-foreground"] = ""
        if mode is not None:
            attrs["data-fleur-mode"] = mode
        merged = merge_props(props, layout=declarations, **styles)
        super().__init__(*children, tag="div", props=extend_props(merged, attrs))
