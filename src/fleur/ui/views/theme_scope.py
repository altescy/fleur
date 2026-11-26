from collections.abc import Mapping
from enum import Enum, auto
from typing import Unpack, cast

from fleur.core.array import Array
from fleur.core.cond import Cond
from fleur.core.expr import Expr, array, string
from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import ViewProp
from fleur.ui.themes import Theme, ThemeColors, ThemeMode, ThemeSelection, ThemeSpaceName, _scoped_theme_css
from fleur.ui.themes._utils import css_color, normalize_length, scope_variable

from . import _utils
from .base import Element, View, ViewChild, ViewProps
from .types import ViewStyleArgs


class ButtonBackground(Enum):
    PRIMARY = auto()


class ThemeScope(Element[ModelT_co, MsgGroupT_co]):
    """A region inheriting the page theme with optional local token and mode overrides."""

    def __init__(
        self,
        *children: ViewChild,
        theme: Theme | ThemeSelection | None = None,
        mode: ThemeMode | Expr[ThemeMode] | None = None,
        colors: ThemeColors | None = None,
        space: Mapping[ThemeSpaceName, str | int | float] | None = None,
        button_bg: str | ButtonBackground | None = None,
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
        if theme is not None:
            if isinstance(theme, ThemeSelection):
                registered = Array.includes(array(list(theme.choices)), theme.name)
                attrs["data-fleur-theme"] = Cond.when(registered, "", None)
                sheet = string("")
                for name, preset in theme.choices.items():
                    sheet = Cond.when(Cond.equal(theme.name, name), _scoped_theme_css(preset), sheet)
            else:
                attrs["data-fleur-theme"] = ""
                sheet = string(_scoped_theme_css(theme))
            children = (View(sheet, tag="style", props={}), *children)
        if colors is not None and "foreground" in colors:
            attrs["data-fleur-scope-foreground"] = ""
        if mode is not None:
            attrs["data-fleur-mode"] = mode
        if button_bg is not None:
            attrs["data-fleur-button-bg"] = ""
            declarations["--fleur-comp-button-bg"] = "initial" if isinstance(button_bg, ButtonBackground) else button_bg
        merged = _utils.merge_props(props, layout=declarations, **styles)
        super().__init__(*children, tag="div", props=_utils.extend_props(merged, attrs))
