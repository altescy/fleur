import json
from collections.abc import Callable
from pathlib import Path

from fleur import Cmd, Component, Model, Msg, MsgGroup, State, String, Sub, bloom
from fleur.core import Dom, DomFocusError, PointerEvent
from fleur.ui import Button, Input, Text, VStack


class Counts(Model):
    fast: State[int]
    slow: State[int]
    focused: State[int]
    failed: State[int]


class Actions(MsgGroup):
    FAST: Msg[None] = Msg()
    SLOW: Msg[None] = Msg()
    START: Msg[PointerEvent] = Msg()
    FOCUSED: Msg[None] = Msg()
    FAILED: Msg[DomFocusError] = Msg()


def test_batched_commands_and_subscriptions_all_run(playwright_page: Callable[[str, Path], str]) -> None:
    both_tasks = Cmd.batch(
        Cmd.task(Dom.focus("editor"), Actions.FOCUSED, Actions.FAILED),
        Cmd.task(Dom.focus("missing"), Actions.FOCUSED, Actions.FAILED),
    )
    app = Component(
        init=Counts(fast=0, slow=0, focused=0, failed=0),
        update=lambda model: Actions.cases(
            Actions.FAST.then(State.set(Counts.fast, model.fast + 1)),
            Actions.SLOW.then(State.set(Counts.slow, model.slow + 1)),
            Actions.START.then((State.unchanged(), both_tasks)),
            Actions.FOCUSED.then(State.set(Counts.focused, model.focused + 1)),
            Actions.FAILED.then(State.set(Counts.failed, model.failed + 1)),
        ),
        view=lambda model: VStack(
            Input(props={"id": "editor", "aria-label": "Editor"}),
            Button("Start", onclick=Actions.START, props={"id": "start"}),
            Text(String.from_number(model.fast), props={"id": "fast"}),
            Text(String.from_number(model.slow), props={"id": "slow"}),
            Text(String.from_number(model.focused), props={"id": "focused"}),
            Text(String.from_number(model.failed), props={"id": "failed"}),
        ),
        subscriptions=lambda _: Sub.batch(
            Sub.interval("fast", 10, Actions.FAST), Sub.interval("slow", 15, Actions.SLOW)
        ),
    )
    probe = """<script>
    setTimeout(() => {
        document.querySelector("#start").click();
        setTimeout(() => {
            const read = id => Number(document.querySelector("#" + id).textContent);
            document.title = JSON.stringify({
                fast: read("fast") > 0,
                slow: read("slow") > 0,
                focused: read("focused"),
                failed: read("failed"),
                editor: document.activeElement?.id,
            });
        }, 150);
    }, 0);
    </script>"""
    html = bloom(app).replace("</body>", probe + "</body>")
    result = json.loads(playwright_page(html, Path(__file__).with_name("batched_effects.cjs")))
    assert result == {"fast": True, "slow": True, "focused": 1, "failed": 1, "editor": "editor"}
