import json
from collections.abc import Callable
from typing import Literal

import pytest

from fleur import Component, Model, Msg, MsgGroup, Page, State, bloom
from fleur.core import PointerEvent
from fleur.ui import Box, Button, ButtonBackground, Input, Theme, ThemeMode, ThemeScope


class Appearance(Model):
    mode: State[ThemeMode]


class Actions(MsgGroup):
    SELECT: Msg[PointerEvent, ThemeMode] = Msg()


def scoped_app() -> Component[Appearance, Actions]:
    return Component(
        Appearance(mode="light"),
        Actions.cases(Actions.SELECT.then(State.set(Appearance.mode, Actions.SELECT.context))),
        Box(
            Button("Outside", props={"id": "outside"}),
            ThemeScope(
                Button("Light", props={"id": "light"}, onclick=Actions.SELECT.bind("light")),
                Button("Dark", props={"id": "dark"}, onclick=Actions.SELECT.bind("dark")),
                Button("Sibling", props={"id": "sibling"}),
                ThemeScope(
                    Button("Parent", props={"id": "parent"}),
                    ThemeScope(Button("Inherited", props={"id": "inherited"})),
                    ThemeScope(
                        Button("Child", props={"id": "child"}),
                        ThemeScope(
                            Button("Grandchild", props={"id": "grandchild"}),
                            ThemeScope(Button("Nested mode", props={"id": "nested"}), mode="light"),
                            colors={"primary": "#21854a"},
                        ),
                        button_bg=ButtonBackground.PRIMARY,
                    ),
                    button_bg="#824399",
                ),
                mode=Appearance.mode,
            ),
        ),
    )


def test_bloom_preserves_page_head_and_emits_both_modes() -> None:
    extras = ['<meta name="app-version" content="1">', '<style id="custom">button{cursor:pointer}</style>']
    page = Page(extra_head_html=list(extras))
    theme = Theme(mode="dark", light={"primary": "navy"}, dark={"primary": "pink", "tracking-wide": "1px"})
    html = bloom(scoped_app, theme=theme, page=page)
    head = html.split("</head>")[0]
    assert page.extra_head_html == extras
    assert head.index(extras[0]) < head.index(extras[1]) < head.index(":root{color-scheme:dark;")
    assert head.count(extras[0]) == head.count(extras[1]) == 1
    assert head.count('[data-fleur-mode="light"]') == head.count('[data-fleur-mode="dark"]') == 1
    assert bloom(scoped_app, theme=theme, page=page) == html


@pytest.mark.parametrize("custom_button", [False, True])
def test_computed_button_background_across_mode_switches(
    chromium_title: Callable[[str], str], custom_button: bool
) -> None:
    """Run using FLEUR_TEST_CHROMIUM=/path/to/chrome or chromium on PATH."""
    theme = Theme(
        mode="dark",
        light={"primary": "#2457a6", "secondary": "#112233"},
        dark={"primary": "#91beff", "secondary": "#445566"},
        components={"button": {"bg": "var(--fleur-color-secondary)"}} if custom_button else {},
    )
    page = Page(extra_head_html=['<style id="custom">button{transition:none !important}</style>'])
    html = bloom(scoped_app, theme=theme, page=page)
    probe = """<script>
    const snapshots = [];
    function sample() {
      snapshots.push(["outside","sibling","parent","inherited","child","grandchild","nested"].map(
        id => getComputedStyle(document.getElementById(id)).backgroundColor));
    }
    sample();
    document.getElementById("dark").click();
    sample();
    document.getElementById("light").click();
    sample();
    document.title = JSON.stringify(snapshots);
    </script>"""
    title = chromium_title(html.replace("</body>", probe + "</body>"))
    primary_light, primary_dark = "rgb(36, 87, 166)", "rgb(145, 190, 255)"
    sibling_light = "rgb(17, 34, 51)" if custom_button else primary_light
    sibling_dark = "rgb(68, 85, 102)" if custom_button else primary_dark
    purple, green = "rgb(130, 67, 153)", "rgb(33, 133, 74)"
    light = [sibling_dark, sibling_light, purple, purple, primary_light, green, green]
    dark = [sibling_dark, sibling_dark, purple, purple, primary_dark, green, green]
    assert json.loads(title) == [light, dark, light]


Preset = Literal["warm", "green"]


class Picker(Model):
    preset: State[Preset]
    mode: State[ThemeMode]


class Pick(MsgGroup):
    THEME: Msg[PointerEvent, Preset] = Msg()
    MODE: Msg[PointerEvent, ThemeMode] = Msg()


def test_reactive_theme_inherits_mode_and_isolates_nested_themes(chromium_title: Callable[[str], str]) -> None:
    themes: dict[Preset, Theme] = {
        "warm": Theme(light={"primary": "red"}, dark={"primary": "orange"}, extra_css=[".sample{height:41px}"]),
        "green": Theme(colors={"primary": "green"}, extra_css=[".sample{height:42px}"]),
    }
    fixed = Theme(light={"primary": "pink"}, dark={"primary": "purple"}, components={"input": {"bg": "teal"}})
    app = Component(
        Picker(preset="warm", mode="dark"),
        Pick.cases(
            Pick.THEME.then(State.set(Picker.preset, Pick.THEME.context)),
            Pick.MODE.then(State.set(Picker.mode, Pick.MODE.context)),
        ),
        Box(
            Button("Outside", props={"id": "outside"}),
            ThemeScope(
                ThemeScope(
                    Button("Inherited override", props={"id": "inherited-bg"}),
                    ThemeScope(Button("Reset", props={"id": "reset"}), button_bg=ButtonBackground.PRIMARY),
                    theme=Theme.select(Picker.preset, themes),
                ),
                button_bg="brown",
            ),
            Button("Green", props={"id": "green"}, onclick=Pick.THEME.bind("green")),
            Button("Light", props={"id": "light"}, onclick=Pick.MODE.bind("light")),
            ThemeScope(
                ThemeScope(
                    Button("Selected", props={"id": "selected", "className": "sample", "key": "selected"}),
                    ThemeScope(Button("Always light", props={"id": "inner-light"}), mode="light"),
                    ThemeScope(Button("Override", props={"id": "override"}), colors={"primary": "blue"}),
                    ThemeScope(
                        Button("Fixed", props={"id": "fixed", "className": "sample"}),
                        ThemeScope(Input(props={"id": "fixed-input"})),
                        theme=fixed,
                    ),
                    theme=Theme.select(Picker.preset, themes),
                ),
                mode=Picker.mode,
            ),
        ),
    )
    page = Page(extra_head_html=["<style>button{transition:none!important}</style>"])
    html = bloom(app, theme=Theme(mode="dark", dark={"primary": "navy"}), page=page)
    probe = """<script>
    const samples = [];
    function sample() {
      const css = id => getComputedStyle(document.getElementById(id));
      samples.push(["outside", "selected", "inner-light", "override", "fixed", "fixed-input", "inherited-bg", "reset"]
        .map(id => css(id).backgroundColor).concat(css("selected").height, css("fixed").height === css("selected").height));
    }
    sample();
    document.getElementById("green").click(); sample();
    document.getElementById("light").click(); sample();
    document.title = JSON.stringify(samples);
    </script>"""
    navy, red, orange = "rgb(0, 0, 128)", "rgb(255, 0, 0)", "rgb(255, 165, 0)"
    blue, green, teal = "rgb(0, 0, 255)", "rgb(0, 128, 0)", "rgb(0, 128, 128)"
    brown = "rgb(165, 42, 42)"
    purple, pink = "rgb(128, 0, 128)", "rgb(255, 192, 203)"
    assert json.loads(chromium_title(html.replace("</body>", probe + "</body>"))) == [
        [navy, orange, red, blue, purple, teal, brown, orange, "41px", False],
        [navy, green, green, blue, purple, teal, brown, green, "42px", False],
        [navy, green, green, blue, pink, teal, brown, green, "42px", False],
    ]
