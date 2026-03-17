from typing import Any, cast

import pytest

from fleur import Expr, Model, Msg, MsgGroup, State, compile_component, emit
from fleur.core.component import Component
from fleur.ui import Text


class CounterModel(Model):
    count: State[int]


class CounterMsg(MsgGroup):
    INC = Msg()


def test_model_state_math_compiles_as_expression() -> None:
    source = emit((CounterModel.count + 1).__compile__())

    assert source == "(model.count+1)"


def test_expr_when_compiles_to_conditional_expression() -> None:
    source = emit(Expr.when(CounterModel.count > 10, CounterModel.count - 1, CounterModel.count + 1).__compile__())

    assert "?" in source
    assert "model.count>10" in source


def test_expr_some_and_every_compile_to_logical_expressions() -> None:
    some_source = emit(Expr.some(CounterModel.count > 10, CounterModel.count < 0).__compile__())
    every_source = emit(Expr.every(CounterModel.count > 10, CounterModel.count < 20).__compile__())

    assert "||" in some_source
    assert "&&" in every_source


def test_update_requires_explicit_set() -> None:
    component = Component(
        CounterModel(count=0),
        CounterMsg.caseof(
            CounterMsg.INC(cast(Any, CounterModel.count + 1)),
        ),
        Text("count"),
    )

    with pytest.raises(TypeError, match=r"ModelState\.set"):
        emit(compile_component(component))
