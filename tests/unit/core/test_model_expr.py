from typing import Any, cast

import pytest

from fleur import Cond, Model, Msg, MsgGroup, State, emit
from fleur.core.component import Component
from fleur.ui import Text


class CounterModel(Model):
    count: State[int]


class TextModel(Model):
    title: State[str]


class ChildModel(Model):
    name: State[str]


class ParentModel(Model):
    child: State[ChildModel]


class ListModel(Model):
    flags: State[list[bool]]


class NumericModel(Model):
    value: State[int]


class BoolModel(Model):
    enabled: State[bool]


class RecordModel(Model):
    mapping: State[dict[str, int]]


class CounterMsg(MsgGroup):
    INC = Msg()


def test_model_state_math_compiles_as_expression() -> None:
    source = emit((CounterModel.count + 1).__compile__())

    assert source == "(model.count+1)"


def test_model_instance_compiles_with_initialized_values() -> None:
    source = emit(ChildModel(name="Fleur").__compile__())

    assert source == '{name: "Fleur"}'


def test_expr_when_compiles_to_conditional_expression() -> None:
    source = emit(Cond.when(CounterModel.count > 10, CounterModel.count - 1, CounterModel.count + 1).__compile__())

    assert "?" in source
    assert "model.count>10" in source


def test_expr_some_and_every_compile_to_logical_expressions() -> None:
    some_source = emit(Cond.some(CounterModel.count > 10, CounterModel.count < 0).__compile__())
    every_source = emit(Cond.every(CounterModel.count > 10, CounterModel.count < 20).__compile__())

    assert "||" in some_source
    assert "&&" in every_source


def test_update_requires_explicit_set() -> None:
    component = Component(
        CounterModel(count=0),
        CounterMsg.caseof(
            CounterMsg.INC.then(cast(Any, CounterModel.count + 1)),
        ),
        Text("count"),
    )

    with pytest.raises(TypeError, match=r"ModelState\.set"):
        emit(component.__compile__())


def test_string_state_exposes_js_like_operations() -> None:
    source = emit(TextModel.title.includes("Fleur").__compile__())

    assert 'model.title.includes("Fleur")' in source


def test_nested_model_state_compiles_property_access_and_update() -> None:
    access_source = emit(ParentModel.child[ChildModel.name].__compile__())
    update_source = emit(State.set(ParentModel.child[ChildModel.name], "next").__compile__())

    assert access_source == "model.child.name"
    assert update_source == 'Object.assign({},model,{child: Object.assign({},model.child,{name: "next"})})'


def test_array_state_update_at_compiles_map_expression() -> None:
    source = emit(ListModel.flags.update_at(1, True).__compile__())

    assert source == "model.flags.with(1,true)"


def test_number_state_exposes_abs() -> None:
    abs_source = emit(NumericModel.value.abs().__compile__())
    assert "Math.abs(model.value)" in abs_source


def test_boolean_state_exposes_not_operator() -> None:
    source = emit(BoolModel.enabled.neg().__compile__())

    assert source == "(!model.enabled)"


def test_record_state_exposes_get_and_has() -> None:
    get_source = emit(RecordModel.mapping["count"].__compile__())
    has_source = emit(RecordModel.mapping.has("count").__compile__())

    assert get_source == 'model.mapping["count"]'
    assert has_source == 'model.mapping.hasOwnProperty("count")'
