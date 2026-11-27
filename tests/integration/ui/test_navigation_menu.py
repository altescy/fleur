from collections.abc import Callable
from pathlib import Path

from fleur import Component, Model, MsgGroup, bloom
from fleur.ui import Button, Link, NavigationMenu, NavigationMenuGroup, VStack


def test_trigger_closes_its_group_while_focus_is_inside(overlay_focus_page: Callable[[str, Path], str]) -> None:
    app = Component(
        Model(),
        MsgGroup.cases(),
        VStack(
            NavigationMenu(
                NavigationMenuGroup("Books", Link("Emma", href="#emma"), Link("Persuasion", href="#p"), id="books"),
                NavigationMenuGroup("Authors", Link("Austen", href="#austen"), id="authors"),
                label="Site",
            ),
            Button("Outside"),
        ),
    )
    overlay_focus_page(bloom(app), Path(__file__).with_name("navigation_menu.cjs"))
