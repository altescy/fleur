# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Checked by Pyright. Each negative case must continue to produce an argument error."""

from typing import Literal

from fleur import Model, State
from fleur.ui import (
    BASIC_THEME,
    ZEN_THEME,
    Background,
    Box,
    Button,
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
    width: State[Literal["full", "fit", "lg", "2/3"] | int]
    margin: State[Literal["auto", "lg"] | int]
    overflow: State[Literal["auto", "hidden"]]
    whitespace: State[Literal["normal", "nowrap"]]
    wrapping: State[Literal["normal", "anywhere"]]
    raw: State[str]


def valid_examples() -> None:
    ThemeScope(theme=Theme.select(FormModel.preset, PRESETS), mode=FormModel.mode)
    ThemeScope(Button("Save"), mode=FormModel.mode, components={"button": {"bg": "primary"}})
    Theme(components={"button": {"bg": css("teal")}, "input": {"fg": "foreground", "radius": "sm"}})
    Theme(light={"primary": "navy"}, dark={"primary": "skyblue"}, space={"lg": 24})
    Button("Save", bg="primary", p="lg", style={"border": "0"})
    Button("Save", bg=FormModel.color, p=FormModel.padding)
    Button("Save", bg=Background.when(FormModel.selected, "primary", "transparent"), p=8)
    Button("Save", bg=css(FormModel.raw), px=css("1.5rem"))
    Box(w="full", h="full", min_w="full", max_w="full")
    Box(w=FormModel.width, max_w=css("min(100%, 42rem)"))
    Box(w="fit", mx="auto", overflow_x="auto", min_h=css("100dvh"))
    Box(mx=FormModel.margin, overflow_x=FormModel.overflow)
    Box(w="1/2", max_h=css("60dvh"), overflow_y=FormModel.overflow)
    Box(white_space=FormModel.whitespace, overflow_wrap=FormModel.wrapping)


def invalid_examples() -> None:
    Theme.select(FormModel.mode, PRESETS)  # pyright: ignore[reportArgumentType]
    ThemeScope(mode="night")  # pyright: ignore[reportArgumentType]
    ThemeScope(colors={"primray": "teal"})  # pyright: ignore[reportArgumentType]
    ThemeScope(components={"button": {"bg": "primray"}})  # pyright: ignore[reportArgumentType]
    ThemeScope(components={"button": {"bg": css(FormModel.raw)}})  # pyright: ignore[reportArgumentType]
    Theme(components={"buton": {"bg": "primary"}})  # pyright: ignore[reportArgumentType]
    Theme(components={"panel": {"bg": "card"}})  # pyright: ignore[reportArgumentType]
    Theme(components={"input": {"background": "primary"}})  # pyright: ignore[reportArgumentType]
    Theme(components={"input": {"radius": "large"}})  # pyright: ignore[reportArgumentType]
    Button("Save", bg="primray")  # pyright: ignore[reportArgumentType]
    Button("Save", p="primary")  # pyright: ignore[reportArgumentType]
    Button("Save", radius="xl")  # pyright: ignore[reportArgumentType]
    Button("Save", font_size="primary")  # pyright: ignore[reportArgumentType]
    Button("Save", bg=FormModel.raw)  # pyright: ignore[reportArgumentType]
    Button("Save", bg=FormModel.padding)  # pyright: ignore[reportArgumentType]
    Box(w="ful")  # pyright: ignore[reportArgumentType]
    Box(w="min(100%, 42rem)")  # pyright: ignore[reportArgumentType]
    Box(p="full")  # pyright: ignore[reportArgumentType]
    Box(p="auto")  # pyright: ignore[reportArgumentType]
    Box(w="fit-content")  # pyright: ignore[reportArgumentType]
    Box(overflow_x="automatic")  # pyright: ignore[reportArgumentType]
    Box(w="1/0")  # pyright: ignore[reportArgumentType]
    Box(p="1/2")  # pyright: ignore[reportArgumentType]
    Box(overflow_y="automatic")  # pyright: ignore[reportArgumentType]
    Box(white_space="no-wrap")  # pyright: ignore[reportArgumentType]
    Box(overflow_wrap="break-all")  # pyright: ignore[reportArgumentType]
    Background.when(FormModel.selected, "brand", "primary")  # pyright: ignore[reportArgumentType]
    Theme(dark={"primray": "red"})  # pyright: ignore[reportArgumentType]
    Theme(space={"huge": 48})  # pyright: ignore[reportArgumentType]
