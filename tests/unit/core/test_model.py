from collections.abc import Mapping, Sequence
from typing import Any, cast

import pytest

from fleur import Array, Boolean, Cond, Expr, Field, Model, Msg, MsgGroup, Number, Object, State, String, emit
from fleur.core.component import Component
from fleur.core.model import model_ref
from fleur.js.builder import ident
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
    index: State[int]


class NestedListModel(Model):
    list_model: State[ListModel]
    index: State[int]


class NumericModel(Model):
    value: State[int]


class BoolModel(Model):
    enabled: State[bool]


class RecordModel(Model):
    mapping: State[Mapping[str, int]]
    key: State[str]


class ReadOnlyListModel(Model):
    flags: State[Sequence[bool]]
    index: State[int]


class CounterMsg(MsgGroup):
    INC = Msg()


class TestModel:
    def test_model_field_math_compiles_as_expression(self) -> None:
        model = model_ref(CounterModel, ident("model"))
        source = emit((model.count + 1).__compile__())

        assert source == "(model.count+1)"

    def test_model_instance_compiles_with_initialized_values(self) -> None:
        source = emit(ChildModel(name="Fleur").__compile__())

        assert source == '{name: "Fleur"}'

    def test_expr_when_compiles_to_conditional_expression(self) -> None:
        model = model_ref(CounterModel, ident("model"))
        source = emit(Cond.when(model.count > 10, model.count - 1, model.count + 1).__compile__())

        assert "?" in source
        assert "model.count>10" in source

    def test_expr_some_and_every_compile_to_logical_expressions(self) -> None:
        model = model_ref(CounterModel, ident("model"))
        some_source = emit(Cond.some(model.count > 10, model.count < 0).__compile__())
        every_source = emit(Cond.every(model.count > 10, model.count < 20).__compile__())

        assert "||" in some_source
        assert "&&" in every_source

    def test_cond_some_without_conditions_compiles_to_false(self) -> None:
        assert emit(Cond.some().__compile__()) == "false"

    def test_cond_every_without_conditions_compiles_to_true(self) -> None:
        assert emit(Cond.every().__compile__()) == "true"

    def test_case_must_return_a_state_update(self) -> None:
        component = Component(
            CounterModel(count=0),
            lambda model: CounterMsg.cases(CounterMsg.INC.then(cast(Any, 1))),
            lambda model: Text("count"),
        )

        with pytest.raises(TypeError, match=r"State\.set"):
            emit(component.__compile__())

    def test_string_state_exposes_js_like_operations(self) -> None:
        model = model_ref(TextModel, ident("model"))
        source = emit(String.includes(model.title, "Fleur").__compile__())

        assert 'model.title.includes("Fleur")' in source

    def test_nested_model_state_compiles_property_access_and_update(self) -> None:
        model = model_ref(ParentModel, ident("model"))
        access_source = emit(model.child.name.__compile__())
        update_source = emit(State.set(ParentModel.child[ChildModel.name], "next").__compile__())

        assert access_source == "model.child.name"
        assert update_source == 'Object.assign({},model,{child: Object.assign({},model.child,{name: "next"})})'

    def test_array_state_update_at_compiles_map_expression(self) -> None:
        model = model_ref(ListModel, ident("model"))
        source = emit(Array.update_at(model.flags, 1, True).__compile__())

        assert source == "model.flags.with(1,true)"

    def test_collection_index_can_come_from_model_state(self) -> None:
        list_model = model_ref(ListModel, ident("model"))
        readonly_model = model_ref(ReadOnlyListModel, ident("model"))
        record_model = model_ref(RecordModel, ident("model"))

        assert emit(list_model.flags[list_model.index].__compile__()) == "model.flags[model.index]"
        assert emit(readonly_model.flags[readonly_model.index].__compile__()) == "model.flags[model.index]"
        assert emit(record_model.mapping[record_model.key].__compile__()) == "model.mapping[model.key]"

    def test_nested_collection_accepts_a_dynamic_index(self) -> None:
        model = model_ref(NestedListModel, ident("model"))
        assert emit(model.list_model.flags[model.index].__compile__()) == "model.list_model.flags[model.index]"

    def test_number_state_exposes_abs(self) -> None:
        model = model_ref(NumericModel, ident("model"))
        abs_source = emit(Number.abs(model.value).__compile__())
        assert "Math.abs(model.value)" in abs_source

    def test_boolean_state_exposes_not_operator(self) -> None:
        model = model_ref(BoolModel, ident("model"))
        source = emit(Boolean.negate(model.enabled).__compile__())

        assert source == "(!model.enabled)"

    def test_record_state_exposes_get_and_has(self) -> None:
        model = model_ref(RecordModel, ident("model"))
        get_source = emit(model.mapping["count"].__compile__())
        has_source = emit(Object.has(model.mapping, "count").__compile__())

        assert get_source == 'model.mapping["count"]'
        assert has_source == 'model.mapping.hasOwnProperty("count")'


class TestField:
    def test_field_is_a_reference_and_not_an_expression(self) -> None:
        assert isinstance(CounterModel.count, Field)
        assert not isinstance(CounterModel.count, Expr)

    def test_nested_field_path_lists_names_from_the_model(self) -> None:
        field = ParentModel.child[ChildModel.name]

        assert isinstance(field, Field)
        assert field.path == ("child", "name")

    def test_field_cannot_be_rendered_as_a_value(self) -> None:
        with pytest.raises(TypeError):
            emit(Text(CounterModel.count).__compile__())  # pyright: ignore[reportArgumentType]

    def test_model_value_reads_fields_as_attributes_of_the_model(self) -> None:
        model = model_ref(ParentModel, ident("model"))

        assert emit(model.child.name.__compile__()) == "model.child.name"


class TestExprFormatting:
    def test_formatting_an_expr_into_a_string_raises(self) -> None:
        model = model_ref(CounterModel, ident("model"))

        with pytest.raises(TypeError, match="join text with"):
            _ = f"Count: {model.count}"

    def test_string_plus_expr_compiles_to_concatenation(self) -> None:
        model = model_ref(CounterModel, ident("model"))
        source = emit(("Count: " + model.count).__compile__())

        assert source == '("Count: "+model.count)'
