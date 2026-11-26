from collections.abc import Callable
from pathlib import Path

from fleur import Component, Cond, Model, Msg, MsgGroup, State, View, bloom
from fleur.core import PointerEvent
from fleur.ui import Accordion, AccordionItem, Button, VStack


class Screen(Model):
    extra: State[bool]


class Actions(MsgGroup):
    ADD: Msg[PointerEvent] = Msg()


def test_accordion_groups_are_independent_and_include_new_items(
    playwright_page: Callable[[str, Path], str],
) -> None:
    def group(label: str) -> View[Screen, Actions]:
        return Accordion(
            AccordionItem("First", "First panel", initial_open=True),
            AccordionItem("Second", "Second panel"),
            Cond.when(Screen.extra, AccordionItem("Third", "Third panel"), None),
            props={"role": "group", "aria-label": label},
        )

    app = Component(
        Screen(extra=False),
        Actions.cases(Actions.ADD.then(State.set(Screen.extra, True))),
        VStack(group("Left"), group("Right"), Button("Add a section", onclick=Actions.ADD)),
    )
    playwright_page(bloom(app), Path(__file__).with_name("accordion.cjs"))
