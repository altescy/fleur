import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from fleur import Array, Cmd, Component, Cond, Model, Msg, MsgGroup, Page, State, View, bloom
from fleur.core import (
    DialogCloseEvent,
    Dom,
    DomAction,
    DomEffect,
    DomElement,
    DomEvents,
    DomFocusError,
    DomLifecycle,
    DomScope,
    EventBinding,
    Expr,
    KeyboardEvent,
    PointerEvent,
    String,
    ToastCloseEvent,
)
from fleur.ui import Dialog, Form, Toast


def test_inline_script_preserves_markup_in_text_and_mount_id(chromium_title: Callable[[str], str]) -> None:
    label = "Print </ScRiPt> as text"
    app = Component(init=Model(), update=lambda _: MsgGroup.cases(), view=lambda _: View(label, tag="output", props={}))
    html = bloom(app, page=Page(mount_id="preview</script>"))
    probe = '<script>document.title = document.querySelector("output").textContent;</script>'

    assert chromium_title(html.replace("</body>", probe + "</body>")) == label


class Settings(Model):
    status: State[str]
    visible: State[bool]


class Actions(MsgGroup):
    CHANGE: Msg[PointerEvent] = Msg()
    REMOVE: Msg[PointerEvent] = Msg()


class ScopedInputs(Model):
    enabled: State[bool]
    duration: State[int | None]
    visible: State[bool]


class ScopedInputActions(MsgGroup):
    CHANGE: Msg[PointerEvent] = Msg()
    REMOVE: Msg[PointerEvent] = Msg()


def setup_scoped_inputs(model: ScopedInputs, root: DomElement, scope: DomScope) -> DomLifecycle:
    enabled = scope.input(model.enabled)
    duration = scope.input(model.duration)
    calls = scope.value(0)

    def record() -> DomAction:
        return DomAction.batch(
            calls.set(calls.value + 1),
            root.set_attribute("data-calls", String.from_number(calls.value)),
            root.set_attribute("data-enabled", Cond.when(enabled, "yes", "no")),
            DomAction.maybe(
                duration,
                lambda milliseconds: root.set_attribute("data-duration", String.from_number(milliseconds)),
                otherwise=root.set_attribute("data-duration", "none"),
            ),
        )

    return DomLifecycle(
        mount=DomAction.batch(record(), scope.listen(root, "record", lambda _: record())),
        dispose=root.set_attribute("data-disposed", "yes"),
    )


def test_scoped_inputs_refresh_existing_listeners(chromium_title: Callable[[str], str]) -> None:
    app = Component(
        init=ScopedInputs(enabled=False, duration=None, visible=True),
        update=lambda _: ScopedInputActions.cases(
            ScopedInputActions.CHANGE.then(State.set(ScopedInputs.enabled, True) & State.set(ScopedInputs.duration, 0)),
            ScopedInputActions.REMOVE.then(State.set(ScopedInputs.visible, False)),
        ),
        view=lambda model: View(
            View("Change", tag="button", props={"id": "change", "onclick": ScopedInputActions.CHANGE}),
            View("Remove", tag="button", props={"id": "remove", "onclick": ScopedInputActions.REMOVE}),
            Cond.when(
                model.visible,
                View(
                    tag="output",
                    props={
                        "id": "probe",
                        **View.dom_effect(
                            DomEffect.scoped("inputs", lambda root, scope: setup_scoped_inputs(model, root, scope))
                        ),
                    },
                ),
                None,
            ),
            tag="div",
            props={},
        ),
    )
    probe = """<script>
    queueMicrotask(async () => {
        const element = document.querySelector("#probe");
        const read = () => [element.dataset.calls, element.dataset.enabled, element.dataset.duration];
        const initial = read();
        document.querySelector("#change").click();
        await Promise.resolve();
        element.dispatchEvent(new Event("record"));
        const updated = read();
        const reused = document.querySelector("#probe") === element;
        document.querySelector("#remove").click();
        element.dispatchEvent(new Event("record"));
        document.title = JSON.stringify([initial, updated, reused, read(), element.dataset.disposed]);
    });
    </script>"""
    assert json.loads(chromium_title(bloom(app).replace("</body>", probe + "</body>"))) == [
        ["1", "no", "none"],
        ["2", "yes", "0"],
        True,
        ["2", "yes", "0"],
        "yes",
    ]


class OptionalDurations(Model):
    durations: State[Mapping[str, int | None]]


def setup_optional_durations(model: OptionalDurations, root: DomElement, scope: DomScope) -> DomLifecycle:
    durations = scope.input(model.durations)

    def describe(key: str) -> DomAction:
        return DomAction.maybe(
            durations[key],
            lambda value: root.set_attribute(f"data-{key}", String.from_number(value)),
            otherwise=root.set_attribute(f"data-{key}", "none"),
        )

    return DomLifecycle(mount=DomAction.batch(describe("zero"), describe("empty"), describe("missing")))


def test_maybe_treats_missing_keys_like_none(chromium_title: Callable[[str], str]) -> None:
    app = Component(
        init=OptionalDurations(durations={"zero": 0, "empty": None}),
        update=lambda _: MsgGroup.cases(),
        view=lambda model: View(
            tag="output",
            props={
                "id": "probe",
                **View.dom_effect(
                    DomEffect.scoped("durations", lambda root, scope: setup_optional_durations(model, root, scope))
                ),
            },
        ),
    )
    probe = """<script>
    queueMicrotask(() => {
        const { zero, empty, missing } = document.querySelector("#probe").dataset;
        document.title = JSON.stringify([zero, empty, missing]);
    });
    </script>"""
    assert json.loads(chromium_title(bloom(app).replace("</body>", probe + "</body>"))) == ["0", "none", "none"]


def test_public_dom_dsl_on_plain_view(chromium_title: Callable[[str], str]) -> None:
    def status_effect(model: Settings) -> DomEffect:
        return DomEffect(
            "status",
            lambda element: element.set_attribute("data-status", model.status),
            dependencies=[model.status],
            after_connect=False,
            mount=lambda element: element.set_attribute("data-mounted", "yes"),
            dispose=lambda element: element.set_attribute("data-disposed", model.status),
        )

    click = EventBinding(
        Actions.CHANGE,
        when=lambda event: Cond.equal(event.current_target.attribute("data-status"), "ready"),
        prevent_default=True,
        action=lambda event: DomAction.batch(
            event.current_target.set_attribute("data-handled", "yes"),
            event.current_target.focus(),
        ),
    )
    app = Component(
        init=Settings(status="ready", visible=True),
        update=lambda _: Actions.cases(
            Actions.CHANGE.then(State.set(Settings.status, "changed")),
            Actions.REMOVE.then(State.set(Settings.visible, False)),
        ),
        view=lambda model: View(
            Cond.when(
                model.visible,
                View(
                    "Run",
                    tag="button",
                    props={**View.dom_effect(status_effect(model)), **click.properties("click"), "id": "run"},
                ),
                None,
            ),
            View("Remove", tag="button", props={"id": "remove", "onclick": Actions.REMOVE}),
            tag="div",
            props={},
        ),
    )
    probe = """<script>
    const run = document.querySelector("#run");
    const initial = [run.dataset.mounted, run.dataset.status];
    run.dataset.mounted = "initial mount observed";
    const event = new MouseEvent("click", {bubbles: true, cancelable: true});
    run.dispatchEvent(event);
    const updated = [run.dataset.mounted, run.dataset.status, run.dataset.handled, document.activeElement === run];
    const ignored = new MouseEvent("click", {bubbles: true, cancelable: true});
    run.dispatchEvent(ignored);
    document.querySelector("#remove").click();
    document.title = JSON.stringify(
        [initial, updated, event.defaultPrevented, ignored.defaultPrevented, run.isConnected, run.dataset.disposed]
    );
    </script>"""
    assert json.loads(chromium_title(bloom(app).replace("</body>", probe + "</body>"))) == [
        ["yes", "ready"],
        ["initial mount observed", "changed", "yes", True],
        True,
        False,
        False,
        "changed",
    ]


class MappedState(Model):
    guards: State[Sequence[bool]]
    labels: State[Sequence[str]]
    choices: State[Sequence[str]]
    result: State[str]
    show_probe: State[bool]


class MappedActions(MsgGroup):
    DIALOG: Msg[DialogCloseEvent, str] = Msg()
    TOAST: Msg[ToastCloseEvent, str] = Msg()
    SELECT: Msg[PointerEvent, str] = Msg()
    REMOVE: Msg[PointerEvent] = Msg()


def test_callbacks_keep_values_from_nested_array_maps(playwright_page: Callable[[str, Path], str]) -> None:
    def form_row(form: Expr[bool]) -> View[MappedState, MappedActions]:
        return Form(prevent_default=form)

    def dialog_row(dialog: Expr[str]) -> View[MappedState, MappedActions]:
        return Dialog(open=True, onclose=MappedActions.DIALOG.bind(dialog), label=dialog)

    def toast_row(root: Expr[str]) -> View[MappedState, MappedActions]:
        return Toast(root, open=True, onclose=MappedActions.TOAST.bind(root), duration_ms=None)

    def buttons(choices: Expr[Sequence[str]], event: Expr[str]) -> View[MappedState, MappedActions]:
        label = event
        return View(
            Array.map(
                choices,
                lambda event: View(
                    label + " / " + event,
                    tag="button",
                    props={"onclick": MappedActions.SELECT.bind(label + " / " + event)},
                ),
            ),
            tag="div",
            props={},
        )

    def scoped_probe(root: DomElement, scope: DomScope) -> DomLifecycle:
        count = scope.value(0)
        timer = scope.timer()
        listener = scope.document_listener(
            root,
            "probe",
            lambda _: DomAction.batch(
                count.set(count.value + 1),
                root.set_attribute("data-count", String.from_number(count.value)),
                timer.start(0, root.set_attribute("data-fired", "yes")),
            ),
        )
        return DomLifecycle(mount=listener.attach())

    app = Component(
        init=MappedState(guards=[False, True], labels=["Book"], choices=["Essay"], result="", show_probe=True),
        update=lambda _: MappedActions.cases(
            MappedActions.DIALOG.then(lambda _, context: State.set(MappedState.result, context)),
            MappedActions.TOAST.then(lambda _, context: State.set(MappedState.result, context)),
            MappedActions.SELECT.then(lambda _, context: State.set(MappedState.result, context)),
            MappedActions.REMOVE.then(State.set(MappedState.show_probe, False)),
        ),
        view=lambda model: View(
            Array.map(model.guards, form_row),
            Array.map(model.labels, dialog_row),
            Array.map(model.labels, toast_row),
            Array.map(model.labels, lambda label: buttons(model.choices, label)),
            View(model.result, tag="output", props={}),
            Cond.when(
                model.show_probe,
                View(
                    tag="div",
                    props={"id": "probe", **View.dom_effect(DomEffect.scoped("probe", scoped_probe))},
                ),
                None,
            ),
            View("Remove probe", tag="button", props={"id": "remove-probe", "onclick": MappedActions.REMOVE}),
            tag="div",
            props={},
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("dom_dsl.cjs"))


class EffectState(Model):
    phase: State[str]


class EffectActions(MsgGroup):
    SWAP: Msg[PointerEvent] = Msg()
    REMOVE: Msg[PointerEvent] = Msg()


def test_effect_composition_preserves_a_focused_input(chromium_title: Callable[[str], str]) -> None:
    def effect(key: str) -> DomEffect:
        attribute = f"data-{key}"
        return DomEffect(
            key,
            lambda element: element.set_attribute(attribute, "active"),
            after_connect=False,
            dispose=lambda element: element.set_attribute(attribute, "disposed"),
        )

    base = View.dom_effect(effect("base"))

    def editor(*extra: DomEffect) -> View[EffectState, EffectActions]:
        props = View.extend_props(base, View.dom_effect(*extra))
        return View(tag="input", props=View.extend_props(props, {"id": "draft"}))

    app = Component(
        init=EffectState(phase="first"),
        update=lambda _: EffectActions.cases(
            EffectActions.SWAP.then(State.set(EffectState.phase, "second")),
            EffectActions.REMOVE.then(State.set(EffectState.phase, "plain")),
        ),
        view=lambda model: View(
            Cond.when(
                Cond.equal(model.phase, "first"),
                editor(effect("first")),
                Cond.when(Cond.equal(model.phase, "second"), editor(effect("second")), editor()),
            ),
            View("Swap", tag="button", props={"id": "swap", "onclick": EffectActions.SWAP}),
            View("Remove", tag="button", props={"id": "remove", "onclick": EffectActions.REMOVE}),
            tag="div",
            props={},
        ),
    )
    probe = """<script>
    const byId = id => document.getElementById(id);
    const node = byId("draft");
    const before = [node.dataset.base, node.dataset.first];
    node.focus();
    node.value = "Unsaved draft";
    node.setSelectionRange(1, 4);
    node.dataset.base = "retained";
    byId("swap").click();
    const swapped = [node.dataset.base, node.dataset.first, node.dataset.second];
    byId("remove").click();
    document.title = JSON.stringify([
        before, swapped, node.dataset.second, node === byId("draft"), node === document.activeElement,
        node.value, node.selectionStart, node.selectionEnd
    ]);
    </script>"""
    assert json.loads(chromium_title(bloom(app).replace("</body>", probe + "</body>"))) == [
        ["active", "active"],
        ["retained", "disposed", "active"],
        "disposed",
        True,
        True,
        "Unsaved draft",
        1,
        4,
    ]


class FocusState(Model):
    editing: State[bool]
    result: State[str]
    key: State[str]


class FocusActions(MsgGroup):
    EDIT: Msg[KeyboardEvent] = Msg()
    FOCUSED: Msg[None] = Msg()
    FAILED: Msg[DomFocusError] = Msg()
    MISSING: Msg[PointerEvent] = Msg()
    UNFOCUSABLE: Msg[PointerEvent] = Msg()


def test_typed_events_and_focus_commands(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        init=FocusState(editing=False, result="idle", key=""),
        update=lambda _: FocusActions.cases(
            FocusActions.EDIT.then(
                lambda event: (
                    State.set(FocusState.editing, True) & State.set(FocusState.key, event.key),
                    Cmd.task(Dom.focus("editor", prevent_scroll=True), FocusActions.FOCUSED, FocusActions.FAILED),
                )
            ),
            FocusActions.FOCUSED.then(State.set(FocusState.result, "focused")),
            FocusActions.FAILED.then(lambda event: State.set(FocusState.result, event)),
            FocusActions.MISSING.then(
                (
                    State.set(FocusState.result, "pending"),
                    Cmd.task(Dom.focus("missing"), FocusActions.FOCUSED, FocusActions.FAILED),
                )
            ),
            FocusActions.UNFOCUSABLE.then(
                (
                    State.set(FocusState.result, "pending"),
                    Cmd.task(Dom.focus("disabled"), FocusActions.FOCUSED, FocusActions.FAILED),
                )
            ),
        ),
        view=lambda model: View(
            View(
                "Edit",
                tag="button",
                props=EventBinding.on(
                    DomEvents.key_down,
                    FocusActions.EDIT,
                    when=lambda event: Cond.equal(event.code, "Enter"),
                    prevent_default=True,
                ),
            ),
            Cond.when(model.editing, View(tag="input", props={"id": "editor"}), None),
            View(model.result, tag="span", props={"id": "status"}),
            View(model.key, tag="span", props={"id": "key"}),
            View("Missing", tag="button", props={"onclick": FocusActions.MISSING}),
            View("Unfocusable", tag="button", props={"onclick": FocusActions.UNFOCUSABLE}),
            View(tag="input", props={"disabled": True, "id": "disabled"}),
            tag="div",
            props={},
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("dom_focus_command.cjs"))
