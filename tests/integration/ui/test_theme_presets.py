import json
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest

from fleur import Component, Model, Msg, MsgGroup, Page, State, View, bloom
from fleur.core import PointerEvent
from fleur.integrations.shadcn import theme_from_shadcn_registry_json
from fleur.ui import BASIC_THEME, ZEN_THEME, Box, Button, Input, Text, ThemeMode, ThemeScope, tabs


class Screen(Model):
    mode: State[ThemeMode]
    tab: State[str]


class Actions(MsgGroup):
    MODE: Msg[PointerEvent, ThemeMode] = Msg()
    SELECT: Msg[PointerEvent, str] = Msg()


def _controls(region: str) -> View[Screen, Actions]:
    panels: Mapping[str, View[Screen, Actions]] = {"One": Text("Panel One"), "Two": Text("Panel Two")}
    return Box(
        Button("Action"),
        Input(props={"aria-label": "Name"}),
        tabs(panels, Screen.tab, Actions.SELECT),
        props={"id": region},
    )


@pytest.mark.parametrize("preset", ["basic", "zen", "emerald"])
def test_preset_mode_and_scoped_colors(preset: str, playwright_page: Callable[[str, Path], str]) -> None:
    if preset == "emerald":
        payload = Path(__file__).with_name("fixtures").joinpath("shadcn-theme-emerald.json").read_text(encoding="utf-8")
        theme = theme_from_shadcn_registry_json(payload)
        # Keep the reference palette independent of the importer and CSS generator.
        source = json.loads(payload)["cssVars"]
        expected = {mode: {key: f"hsl({v})" for key, v in source[mode].items()} for mode in ("light", "dark")}
    else:
        theme = BASIC_THEME if preset == "basic" else ZEN_THEME
        expected = {"light": theme.light, "dark": BASIC_THEME.dark}

    app = Component(
        Screen(mode="light", tab="One"),
        Actions.cases(
            Actions.MODE.then(State.set(Screen.mode, Actions.MODE.context)),
            Actions.SELECT.then(State.set(Screen.tab, Actions.SELECT.context)),
        ),
        Box(
            Button("Light", onclick=Actions.MODE.bind("light")),
            Button("Dark", onclick=Actions.MODE.bind("dark")),
            _controls("outside"),
            ThemeScope(
                _controls("parent"),
                ThemeScope(_controls("child"), colors={"primary": "#704092", "card": "#efdead", "ring": "#157768"}),
                mode=Screen.mode,
            ),
        ),
    )
    page = Page(
        extra_head_html=[
            "<style>* { transition: none !important }</style>",
            f'<script id="expected" type="application/json">{json.dumps(expected)}</script>',
        ]
    )
    playwright_page(bloom(app, page=page, theme=theme), Path(__file__).with_name("theme_presets.cjs"))
