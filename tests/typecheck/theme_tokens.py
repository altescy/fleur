# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Checked by Pyright. Each negative case must continue to produce an argument error."""

from typing import Literal

from fleur import Model, State
from fleur.ui import (
    BASIC_THEME,
    ZEN_THEME,
    Background,
    Button,
    ButtonBackground,
    Theme,
    ThemeColorName,
    ThemeMode,
    ThemeScope,
    ThemeSpaceName,
    css,
)


Preset = Literal["basic", "zen"]
PRESETS: dict[Preset, Theme] = {"basic": BASIC_THEME, "zen": ZEN_THEME}


class FormModel(Model):
    preset: State[Preset]
    mode: State[ThemeMode]
    selected: State[bool]
    color: State[ThemeColorName]
    padding: State[ThemeSpaceName]
    raw: State[str]


def valid_examples() -> None:
    ThemeScope(theme=Theme.select(FormModel.preset, PRESETS), mode=FormModel.mode)
    ThemeScope(Button("Save"), mode=FormModel.mode, colors={"primary": "teal"}, button_bg=ButtonBackground.PRIMARY)
    Theme(light={"primary": "navy"}, dark={"primary": "skyblue"}, space={"lg": 24})
    Button("Save", bg="primary", p="lg", style={"border": "0"})
    Button("Save", bg=FormModel.color, p=FormModel.padding)
    Button("Save", bg=Background.when(FormModel.selected, "primary", "transparent"), p=8)
    Button("Save", bg=css(FormModel.raw), px=css("1.5rem"))


def invalid_examples() -> None:
    Theme.select(FormModel.mode, PRESETS)  # pyright: ignore[reportArgumentType]
    ThemeScope(mode="night")  # pyright: ignore[reportArgumentType]
    ThemeScope(colors={"primray": "teal"})  # pyright: ignore[reportArgumentType]
    Button("Save", bg="primray")  # pyright: ignore[reportArgumentType]
    Button("Save", p="primary")  # pyright: ignore[reportArgumentType]
    Button("Save", radius="xl")  # pyright: ignore[reportArgumentType]
    Button("Save", font_size="primary")  # pyright: ignore[reportArgumentType]
    Button("Save", bg=FormModel.raw)  # pyright: ignore[reportArgumentType]
    Button("Save", bg=FormModel.padding)  # pyright: ignore[reportArgumentType]
    Background.when(FormModel.selected, "brand", "primary")  # pyright: ignore[reportArgumentType]
    Theme(dark={"primray": "red"})  # pyright: ignore[reportArgumentType]
    Theme(space={"huge": 48})  # pyright: ignore[reportArgumentType]
