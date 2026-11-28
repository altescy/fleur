from collections.abc import Callable
from pathlib import Path

from fleur import Component, Cond, Model, Msg, MsgGroup, State, bloom
from fleur.core import PointerEvent
from fleur.ui import Button, Link, Menu, MenuItem, Toolbar, VStack


class Screen(Model):
    extra: State[bool]


class Actions(MsgGroup):
    ADD: Msg[PointerEvent] = Msg()


def test_toolbar_skips_inactive_controls_and_preserves_composite_focus(
    playwright_page: Callable[[str, Path], str],
) -> None:
    app = Component(
        init=Screen(extra=False),
        update=lambda _: Actions.cases(Actions.ADD.then(State.set(Screen.extra, True))),
        view=lambda model: VStack(
            Button("Before"),
            Toolbar(
                Button("Start"),
                Button("Disabled", props={"disabled": True}),
                Cond.when(model.extra, Button("Inserted"), None),
                Link("Help", href="#help"),
                Menu(
                    MenuItem("Apply", onclick=Actions.ADD),
                    MenuItem("Apply again", onclick=Actions.ADD),
                    id="more",
                    trigger=lambda attrs: Button("More", props=attrs),
                ),
                label="Horizontal",
                props={"dir": "rtl"},
            ),
            Button("Insert a control", onclick=Actions.ADD),
            Toolbar(
                Button("Top"),
                Button("Hidden", props={"hidden": True}),
                Button("Bottom"),
                label="Vertical",
                orientation="vertical",
            ),
            Button("After"),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("toolbar.cjs"))
