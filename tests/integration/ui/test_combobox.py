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
        Screen(options={"jane": "Jane Eyre", "emma": "Emma", "persuasion": "Persuasion"}, selected="emma"),
        Actions.cases(
            Actions.SELECT.then(State.set(Screen.selected, Actions.SELECT.context)),
            Actions.REORDER.then(
                State.set(Screen.options, {"persuasion": "Persuasion", "emma": "Emma (1815)", "jane": "Jane Eyre"})
            ),
            Actions.REMOVE.then(State.set(Screen.options, {"persuasion": "Persuasion", "emma": "Emma (1815)"})),
            Actions.ADD.then(
                State.set(Screen.options, {"persuasion": "Persuasion", "emma": "Emma (1815)", "jamaica": "Jamaica Inn"})
            ),
            Actions.CLEAR.then(State.set(Screen.selected, None)),
        ),
        VStack(
            Combobox(
                Screen.options,
                id="book",
                label="Book",
                value=Screen.selected,
                onselect=Actions.SELECT,
            ),
            Button("Reorder", onclick=Actions.REORDER),
            Button("Select Jane Eyre", onclick=Actions.SELECT.bind("jane")),
            Button("Remove Jane Eyre", onclick=Actions.REMOVE),
            Button("Add Jamaica Inn", onclick=Actions.ADD),
            Button("Clear selection", onclick=Actions.CLEAR),
            Text(String.or_empty(Screen.selected), props={"id": "selection"}),
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
        Search(submitted=0, selected=None),
        SearchActions.cases(
            SearchActions.SUBMIT.then(State.set(Search.submitted, Search.submitted + 1)),
            SearchActions.SELECT.then(State.set(Search.selected, SearchActions.SELECT.context)),
        ),
        Form(
            Combobox(
                {"emma": "Emma", "persuasion": "Persuasion"},
                id="book",
                label="Book",
                value=Search.selected,
                onselect=SearchActions.SELECT,
            ),
            Text(String.from_number(Search.submitted), props={"id": "submitted"}),
            onsubmit=SearchActions.SUBMIT,
            prevent_default=True,
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("combobox_form.cjs"))
