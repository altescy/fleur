from typing import Any, cast

import pytest

from fleur import Model, ModelUpdate, Msg, MsgGroup, State, emit
from fleur.core.model import model_ref
from fleur.js.builder import ident


class Payload(Model):
    title: State[str]


class Page(Model):
    title: State[str]
    picked: State[int]
    flag: State[bool]


class Replies(MsgGroup):
    LOADED: Msg[Payload] = Msg()
    PICKED: Msg[Payload, int] = Msg()
    TOGGLED: Msg[None] = Msg()


class SampleMsg(MsgGroup):
    LOADED = Msg[dict[str, object]]()


class TestMsg:
    def test_grouped_msg_compiles_to_message_builder_function(self) -> None:
        source = emit(SampleMsg.LOADED.__compile__())

        assert 'type: "LOADED"' in source
        assert "event" in source

    def test_bound_context_compiles_into_the_message(self) -> None:
        source = emit(Replies.PICKED.bind(3).__compile__())

        assert "context: 3" in source


class TestThenArity:
    def test_one_argument_case_receives_the_event(self) -> None:
        update = Replies.cases(
            Replies.LOADED.then(lambda event: State.set(Page.title, event.title)),
            Replies.PICKED.then(State.unchanged()),
            Replies.TOGGLED.then(State.unchanged()),
        )

        source = emit(update.__compile__())

        assert "message.event.title" in source

    def test_event_fields_support_operators_in_javascript(self) -> None:
        # The event is an expression, so `+` builds JavaScript instead of failing.
        update = Replies.cases(
            Replies.LOADED.then(lambda event: State.set(Page.title, event.title + "!")),
            Replies.PICKED.then(State.unchanged()),
            Replies.TOGGLED.then(State.unchanged()),
        )

        assert '(message.event.title+"!")' in emit(update.__compile__())

    def test_two_argument_case_receives_the_event_and_context(self) -> None:
        update = Replies.cases(
            Replies.LOADED.then(State.unchanged()),
            Replies.PICKED.then(
                lambda event, context: State.set(Page.picked, context) & State.set(Page.title, event.title)
            ),
            Replies.TOGGLED.then(State.unchanged()),
        )

        source = emit(update.__compile__())

        assert "message.context" in source
        assert "message.event" in source

    def test_defaulted_second_parameter_receives_only_the_event(self) -> None:
        default = object()
        received: list[bool] = []

        def case(event: Payload, extra: object = default) -> ModelUpdate[Page]:
            received.append(extra is default)
            return State.set(Page.title, event.title)

        update = Replies.cases(
            Replies.LOADED.then(case),
            Replies.PICKED.then(State.unchanged()),
            Replies.TOGGLED.then(State.unchanged()),
        )
        emit(update.__compile__())

        assert received == [True]

    def test_varargs_case_is_rejected(self) -> None:
        def case(*args: Any) -> ModelUpdate[Page]:
            return State.unchanged()

        with pytest.raises(TypeError, match=r"not of \*args"):
            Replies.LOADED.then(case)

    def test_expression_is_rejected_as_a_case(self) -> None:
        # An expression is callable as a JavaScript function, but it is not a case.
        page = model_ref(Page, ident("model"))

        with pytest.raises(TypeError, match=r"PICKED\.then\(\) takes State\.set.*not Expr"):
            Replies.PICKED.then(cast(Any, page.picked + 1))

    def test_function_must_return_a_case(self) -> None:
        with pytest.raises(TypeError, match=r"The case of LOADED must return State\.set.*not ValueRef"):
            Replies.LOADED.then(cast(Any, lambda event: event.title))


class Toggles(MsgGroup):
    OPEN: Msg[None] = Msg()
    CLOSE: Msg[None] = Msg()


class Flags(Model):
    open: State[bool]


def test_cases_must_handle_every_message_of_the_group() -> None:
    with pytest.raises(ValueError, match=r"Toggles.cases\(\) does not handle: CLOSE"):
        Toggles.cases(Toggles.OPEN.then(State.set(Flags.open, True)))


def test_unchanged_handles_a_message_without_a_state_change() -> None:
    update = Toggles.cases(Toggles.OPEN.then(State.set(Flags.open, True)), Toggles.CLOSE.then(State.unchanged()))
    assert '"CLOSE"' in emit(update.__compile__())
