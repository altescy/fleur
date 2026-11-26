from collections.abc import Callable
from pathlib import Path
from typing import Unpack

from fleur import Component, Model, MsgGroup, Page, View, bloom, emit
from fleur.core import record
from fleur.core.view import ViewProps
from fleur.ui import Box, Button, Divider, HStack, Input, Text, Theme, ThemeScope, VStack
from fleur.ui.views.types import ViewStyleArgs


def _row(name: str, classes: str = "", **styles: Unpack[ViewStyleArgs]) -> View[Model, MsgGroup]:
    def attrs(kind: str) -> ViewProps:
        # Exercise expression-valued props on the class + shorthand + style case.
        props = {"id": f"{name}-{kind}", "className": classes}
        return record(props) if name == "explicit" else props

    return Box(
        Box("Box", props=attrs("box"), **styles),
        Text("Text", props=attrs("text"), **styles),
        Input(props=attrs("input"), **styles),
        Button("Button", props=attrs("button"), **styles),
    )


def test_element_defaults_do_not_generate_inline_styles() -> None:
    for element, kind in [
        (Box(), "box"),
        (Text("Text"), "text"),
        (Input(), "input"),
        (Button("OK"), "button"),
        (HStack(), "hstack"),
        (VStack(), "vstack"),
    ]:
        source = emit(element.__compile__())
        assert f'"data-fleur-ui": "{kind}"' in source
        assert "style:" not in source


def test_element_cascade_with_pointer_and_keyboard(playwright_page: Callable[[str, Path], str]) -> None:
    theme = Theme(
        colors={"primary": "#102030", "card": "#fefefe"},
        components={
            "button": {"focus-ring": "0 0 0 4px var(--fleur-color-ring)"},
            "input": {"focus-ring": "0 0 0 2px var(--fleur-color-ring)"},
        },
    )
    view = Box(
        _row("page"),
        HStack(Text("Horizontal"), props={"id": "desktop-stack", "className": "desktop-only"}),
        VStack(Text("Vertical"), props={"id": "responsive-stack", "className": "responsive-stack"}),
        VStack(
            Text("Explicit layout"),
            props={"id": "explicit-stack", "className": "desktop-only"},
            style={"display": "grid"},
        ),
        ThemeScope(
            _row("scope"),
            _row("short", bg="primary", p="lg"),
            _row("class", "paint"),
            _row("both", "paint", bg="primary", p="lg"),
            _row("explicit", "paint", bg="primary", p="lg", style={"background": "#654321", "padding": "3px"}),
            Box(Text("Nested", props={"id": "nested-text"}), bg="primary", fg="secondary"),
            Button("Disabled", props={"id": "disabled", "disabled": True}),
            Box("Focusable box", props={"id": "tab-box", "tabindex": 0}),
            Text("Focusable text", props={"id": "tab-text", "tabindex": 0}),
            Divider(color="ring", props={"id": "divider", "style": {"width": "37px"}}),
            colors={
                "primary": "#306090",
                "card": "#e0f0f8",
                "foreground": "#263747",
                "ring": "#008855",
                "secondary": "#ff0011",
            },
            space={"xs": 2, "sm": 4, "md": 8, "lg": 19},
            button_bg="#904020",
        ),
    )
    page = Page(
        extra_head_html=[
            """<style>
      * { transition: none !important; }
      .paint { background: #246824; padding: 7px; border: 3px solid #172635; border-radius: 13px; }
      .paint:focus-visible { outline: 5px dotted #123456; }
      @media (max-width: 600px) {
        .desktop-only { display: none; }
        .responsive-stack { flex-direction: row; }
      }
    </style>"""
        ]
    )
    playwright_page(
        bloom(Component(Model(), MsgGroup.cases(), view), theme=theme, page=page),
        Path(__file__).with_name("element_styles.cjs"),
    )
