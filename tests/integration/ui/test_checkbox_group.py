from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from fleur import Array, Component, Model, Msg, MsgGroup, State, bloom
from fleur.core import InputEvent, PointerEvent
from fleur.ui import Button, CheckboxGroup, Form, Text, VStack


class Screen(Model):
    options: State[Mapping[str, str]]
    selection: State[Sequence[str]]
    disabled: State[bool]


class Actions(MsgGroup):
    CHANGE: Msg[InputEvent, Sequence[str]] = Msg()
    REFRESH: Msg[PointerEvent] = Msg()
    DISABLE: Msg[PointerEvent] = Msg()


def test_checkbox_group_keeps_native_form_values_and_model_in_sync(
    playwright_page: Callable[[str, Path], str],
) -> None:
    app = Component(
        Screen(options={"reading": "Reading", "finished": "Finished"}, selection=["reading"], disabled=False),
        Actions.cases(
            Actions.CHANGE.then(State.set(Screen.selection, Actions.CHANGE.context)),
            Actions.REFRESH.then(
                State.set(Screen.options, {"finished": "Finished", "reading": "Reading", "to-read": "To read"})
            ),
            Actions.DISABLE.then(State.set(Screen.disabled, True)),
        ),
        VStack(
            Form(
                CheckboxGroup(
                    Screen.options,
                    label="Shelves",
                    name="shelf",
                    value=Screen.selection,
                    onchange=Actions.CHANGE,
                    disabled=Screen.disabled,
                ),
                props={"aria-label": "Filters"},
            ),
            Button("Refresh", onclick=Actions.REFRESH),
            Button("Disable", onclick=Actions.DISABLE),
            Text(Array.join(Screen.selection), props={"role": "status"}),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("checkbox_group.cjs"))
