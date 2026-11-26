import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Literal

import pytest

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
    assert '"aria-selected":' in source
    assert "hidden:" in source


def test_tabs_cascade_and_activation(playwright_page: Callable[[str, Path], str]) -> None:
    panels: Mapping[Tab, View[Screen, Actions]] = {"One": Text("Panel One"), "Two": Text("Panel Two")}
    dark = Cond.equal(Screen.mode, "dark")
    root = Box(
        tabs(panels, Screen.selected, Actions.SELECT, label="Page sections", props={"id": "page"}),
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
      .tint[aria-selected="true"] { --fleur-local-bg: var(--fleur-color-primary) }
      .paint { background: #316931; padding: 7px }
      .paint:hover { color: #feefaa }
      .paint:focus-visible { outline: 3px dashed #ee9933 }
      .wrapper > div { display: flex }
    </style>"""
        ]
    )
    playwright_page(bloom(app, theme=theme, page=page), Path(__file__).with_name("tabs.cjs"))


@pytest.mark.parametrize("legacy_move", [False, True], ids=["browser-default", "insert-before-fallback"])
def test_reordering_tabs_keeps_input_focus_and_values(chromium_title: Callable[[str], str], legacy_move: bool) -> None:
    first = Input[Screen, Actions](props={"id": "first-input"})
    second = Input[Screen, Actions](props={"id": "second-input"})
    contents = Cond.when(
        Cond.equal(Screen.mode, "dark"),
        record({"Two": second, "One": first, "More options": Text("More")}),
        record({"One": first, "Two": second}),
    )
    app = Component(
        Screen(selected="Two", mode="light"),
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
    const originalPanel = two.getAttribute("aria-controls");
    const input = byId("second-input");
    byId("first-input").value = "Draft for One";
    input.value = "Draft for Two";
    input.focus();
    input.setSelectionRange(2, 5);
    const focusedBefore = document.activeElement === input;
    let blurred = false;
    input.addEventListener("blur", () => { blurred = true; });
    byId("reverse").click();
    const [first, second, third] = triggers();
    document.title = JSON.stringify({
      keptTriggers: first === two && second === one,
      keptAssociation: first.getAttribute("aria-controls") === originalPanel && byId(originalPanel).contains(input),
      linkedNewTab: byId(third.getAttribute("aria-controls")).getAttribute("aria-labelledby") === third.id,
      keptInput: byId("second-input") === input,
      focusedBefore,
      focusedAfter: document.activeElement === input,
      blurred,
      selection: [input.selectionStart, input.selectionEnd],
      drafts: [byId("first-input").value, byId("second-input").value],
    });
    </script>"""
    if legacy_move:
        probe = '<script>document.getElementById("tabs").moveBefore = undefined;</script>' + probe
    html = bloom(app).replace("</body>", probe + "</body>")
    assert json.loads(chromium_title(html)) == {
        "keptTriggers": True,
        "keptAssociation": True,
        "linkedNewTab": True,
        "keptInput": True,
        "focusedBefore": True,
        "focusedAfter": True,
        "blurred": False,
        "selection": [2, 5],
        "drafts": ["Draft for One", "Draft for Two"],
    }
