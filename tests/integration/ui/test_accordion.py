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
    def group(model: Screen, label: str) -> View[Screen, Actions]:
        return Accordion(
            AccordionItem("First", "First panel", initial_open=True),
            AccordionItem("Second", "Second panel"),
            Cond.when(model.extra, AccordionItem("Third", "Third panel"), None),
            props={"role": "group", "aria-label": label},
        )

    app = Component(
        init=Screen(extra=False),
        update=lambda _: Actions.cases(Actions.ADD.then(State.set(Screen.extra, True))),
        view=lambda model: VStack(
            group(model, "Left"), group(model, "Right"), Button("Add a section", onclick=Actions.ADD)
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("accordion.cjs"))
