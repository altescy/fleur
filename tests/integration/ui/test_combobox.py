from collections.abc import Callable, Mapping
from pathlib import Path

from fleur import Component, Model, Msg, MsgGroup, State, String, bloom
from fleur.core import PointerEvent, SubmitEvent
from fleur.ui import Button, Combobox, Form, Text, VStack


class Screen(Model):
    options: State[Mapping[str, str]]
    selected: State[str | None]


class Actions(MsgGroup):
    SELECT: Msg[PointerEvent, str] = Msg()
    REORDER: Msg[PointerEvent] = Msg()
    REMOVE: Msg[PointerEvent] = Msg()
    ADD: Msg[PointerEvent] = Msg()
    CLEAR: Msg[PointerEvent] = Msg()


def test_combobox_keeps_editing_when_selection_and_options_change(
    overlay_focus_page: Callable[[str, Path], str],
) -> None:
    app = Component(
        init=Screen(options={"jane": "Jane Eyre", "emma": "Emma", "persuasion": "Persuasion"}, selected="emma"),
        update=lambda _: Actions.cases(
            Actions.SELECT.then(lambda _, context: State.set(Screen.selected, context)),
            Actions.REORDER.then(
                State.set(Screen.options, {"persuasion": "Persuasion", "emma": "Emma (1815)", "jane": "Jane Eyre"})
            ),
            Actions.REMOVE.then(State.set(Screen.options, {"persuasion": "Persuasion", "emma": "Emma (1815)"})),
            Actions.ADD.then(
                State.set(Screen.options, {"persuasion": "Persuasion", "emma": "Emma (1815)", "jamaica": "Jamaica Inn"})
            ),
            Actions.CLEAR.then(State.set(Screen.selected, None)),
        ),
        view=lambda model: VStack(
            Combobox(
                model.options,
                id="book",
                label="Book",
                value=model.selected,
                onselect=Actions.SELECT,
            ),
            Button("Reorder", onclick=Actions.REORDER),
            Button("Select Jane Eyre", onclick=Actions.SELECT.bind("jane")),
            Button("Remove Jane Eyre", onclick=Actions.REMOVE),
            Button("Add Jamaica Inn", onclick=Actions.ADD),
            Button("Clear selection", onclick=Actions.CLEAR),
            Text(String.or_empty(model.selected), props={"id": "selection"}),
        ),
    )
    overlay_focus_page(bloom(app), Path(__file__).with_name("combobox.cjs"))


class Search(Model):
    submitted: State[int]
    selected: State[str | None]


class SearchActions(MsgGroup):
    SUBMIT: Msg[SubmitEvent] = Msg()
    SELECT: Msg[PointerEvent, str] = Msg()


def test_enter_submits_the_form_unless_an_option_is_active(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        init=Search(submitted=0, selected=None),
        update=lambda model: SearchActions.cases(
            SearchActions.SUBMIT.then(State.set(Search.submitted, model.submitted + 1)),
            SearchActions.SELECT.then(lambda _, context: State.set(Search.selected, context)),
        ),
        view=lambda model: Form(
            Combobox(
                {"emma": "Emma", "persuasion": "Persuasion"},
                id="book",
                label="Book",
                value=model.selected,
                onselect=SearchActions.SELECT,
            ),
            Text(String.from_number(model.submitted), props={"id": "submitted"}),
            onsubmit=SearchActions.SUBMIT,
            prevent_default=True,
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("combobox_form.cjs"))
