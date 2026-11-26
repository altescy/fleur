import json
from collections.abc import Callable
from pathlib import Path

from fleur import Boolean, Component, Model, Msg, MsgGroup, State, bloom
from fleur.cli.commands._loader import load_component
from fleur.core import SubmitEvent
from fleur.ui import Form, VStack


class Settings(Model):
    prevent: State[bool]


class Actions(MsgGroup):
    SUBMIT: Msg[SubmitEvent] = Msg()


def test_form_submit_cancellation_is_opt_in_and_reactive(chromium_title: Callable[[str], str]) -> None:
    app = Component(
        Settings(prevent=False),
        Actions.cases(Actions.SUBMIT.then(State.set(Settings.prevent, Boolean.negate(Settings.prevent)))),
        VStack(
            Form(onsubmit=Actions.SUBMIT, prevent_default=Settings.prevent, props={"id": "reactive"}),
            Form(onsubmit=Actions.SUBMIT, props={"id": "native"}),
        ),
    )
    probe = """<script>
    const submit = id => {
      const event = new SubmitEvent("submit", {bubbles: true, cancelable: true});
      document.getElementById(id).dispatchEvent(event);
      return event.defaultPrevented;
    };
    document.title = JSON.stringify([submit("reactive"), submit("reactive"), submit("reactive"), submit("native")]);
    </script>"""
    assert json.loads(chromium_title(bloom(app).replace("</body>", probe + "</body>"))) == [False, True, False, False]


def test_expense_report_submits_with_enter(playwright_page: Callable[[str, Path], str]) -> None:
    example = Path(__file__).resolve().parents[3] / "examples/expense_report.py"
    playwright_page(bloom(load_component(f"{example}:app")), Path(__file__).with_name("expense_form.cjs"))
