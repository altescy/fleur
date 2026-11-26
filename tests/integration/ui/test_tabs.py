import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Literal

from fleur import Component, Cond, Model, Msg, MsgGroup, Page, State, View, bloom, emit
from fleur.core import PointerEvent, record
from fleur.ui import Box, Button, Input, Text, Theme, ThemeMode, ThemeScope, tabs

Tab = Literal["One", "Two"]


class Screen(Model):
    selected: State[Tab]
    mode: State[ThemeMode]


class Actions(MsgGroup):
    SELECT: Msg[PointerEvent, Tab] = Msg()
    MODE: Msg[PointerEvent, ThemeMode] = Msg()


def test_default_tabs_compile_state_without_inline_styles() -> None:
    contents: Mapping[str, View[Screen, Actions]] = {"One": Text("Panel One")}
    source = emit(tabs(record(contents), "One").__compile__())
    assert "style:" not in source
    assert '"aria-pressed":' in source
    assert "hidden:" in source


def test_tabs_cascade_and_activation(playwright_page: Callable[[str, Path], str]) -> None:
    panels: Mapping[Tab, View[Screen, Actions]] = {"One": Text("Panel One"), "Two": Text("Panel Two")}
    dark = Cond.equal(Screen.mode, "dark")
    root = Box(
        tabs(panels, Screen.selected, Actions.SELECT, props={"id": "page"}),
        ThemeScope(
            tabs(panels, Screen.selected, Actions.SELECT, props={"id": "scoped"}),
            tabs(panels, Screen.selected, Actions.SELECT, props={"id": "tinted"}, tab_class="tint"),
            tabs(panels, Screen.selected, Actions.SELECT, props={"id": "classed"}, tab_class="paint"),
            tabs(
                panels,
                Screen.selected,
                Actions.SELECT,
                props=record({"id": "styled", "className": "wrapper"}),
                style={"padding": "11px"},
                tab_class=Cond.when(dark, "paint night", "paint"),
                tab_style={"background": Cond.when(dark, "#663322", "#884433"), "padding": "5px"},
            ),
            colors={"primary": "#aa3344", "ring": "#117755", "muted-foreground": "#557788", "border": "#7e8da8"},
            mode=Screen.mode,
        ),
        Button("Dark", props={"id": "dark"}, onclick=Actions.MODE.bind("dark")),
        Button("Light", props={"id": "light"}, onclick=Actions.MODE.bind("light")),
    )
    app = Component(
        Screen(selected="One", mode="light"),
        Actions.cases(
            Actions.SELECT.then(State.set(Screen.selected, Actions.SELECT.context)),
            Actions.MODE.then(State.set(Screen.mode, Actions.MODE.context)),
        ),
        root,
    )
    theme = Theme(
        light={"card": "#e0efff", "foreground": "#112233", "border": "#98a5b8", "muted": "#ddeeff"},
        dark={"card": "#253545", "foreground": "#f0f4f8", "muted": "#152535"},
        components={"button": {"focus_ring": "0 0 0 3px var(--fleur-color-ring)"}},
    )
    page = Page(
        extra_head_html=[
            """<style>
      * { transition: none !important }
      .tint[aria-pressed="true"] { --fleur-local-bg: var(--fleur-color-primary) }
      .paint { background: #316931; padding: 7px }
      .paint:hover { color: #feefaa }
      .paint:focus-visible { outline: 3px dashed #ee9933 }
      .wrapper > div { display: flex }
    </style>"""
        ]
    )
    playwright_page(bloom(app, theme=theme, page=page), Path(__file__).with_name("tabs.cjs"))


def test_reordering_tabs_keeps_uncontrolled_input_values(chromium_title: Callable[[str], str]) -> None:
    first = Input[Screen, Actions](props={"id": "first-input"})
    second = Input[Screen, Actions](props={"id": "second-input"})
    contents = Cond.when(
        Cond.equal(Screen.mode, "dark"), record({"Two": second, "One": first}), record({"One": first, "Two": second})
    )
    app = Component(
        Screen(selected="One", mode="light"),
        Actions.cases(Actions.MODE.then(State.set(Screen.mode, Actions.MODE.context))),
        Box(
            Button("Reverse", props={"id": "reverse"}, onclick=Actions.MODE.bind("dark")),
            tabs(contents, Screen.selected, props={"id": "tabs"}),
        ),
    )
    probe = """<script>
    const byId = id => document.getElementById(id);
    const triggers = () => Array.from(byId("tabs").querySelectorAll("button"));
    const [one, two] = triggers();
    byId("first-input").value = "Draft for One";
    byId("second-input").value = "Draft for Two";
    one.focus();
    byId("reverse").click();
    const [first, second] = triggers();
    document.title = JSON.stringify([
      first === two,
      second === one,
      document.activeElement === one,
      byId("first-input").value,
      byId("second-input").value,
    ]);
    </script>"""
    html = bloom(app).replace("</body>", probe + "</body>")
    assert json.loads(chromium_title(html)) == [True, True, True, "Draft for One", "Draft for Two"]
