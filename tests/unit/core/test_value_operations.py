import json
from collections.abc import Mapping
import shutil
import subprocess

import pytest

from fleur import Array, Cond, Expr, Model, Number, Object, State, String, Url, emit
from fleur.core import array, record
from fleur.js.builder import ident


class Values(Model):
    amounts: State[list[int]]
    parts: State[list[str]]
    separator: State[str]
    text: State[str]


def _increment(amount: Expr[int]) -> Expr[int]:
    return amount + 1


def test_value_operations_evaluate_in_javascript() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")

    operations = {
        "length": Array.length(Values.amounts),
        "sum": Array.sum(Values.amounts),
        "empty_sum": Array.sum(array([])),
        "decimal_sum": Array.sum(array([1.25, 2])),
        "mapped": Array.map(Values.amounts, _increment),
        "mapped_again": Array.map(Values.amounts, _increment),
        "joined": Array.join(Values.parts, Values.separator),
        "number": Number.from_string(Values.text),
        "empty_number": Number.from_string(""),
        "invalid_number": Number.is_finite(Number.from_string("12xyz")),
        "formatted": Number.format(1234.5, locale="ja-JP"),
        "plain": String.from_number(1234.5),
        "escaped": String.replace_all(Array.join(Values.parts), '"', '""'),
        "encoded": Url.encode_component("€ & ="),
    }
    program = {name: emit(value.__compile__()) for name, value in operations.items()}
    script = """
    const expressions = JSON.parse(require("node:fs").readFileSync(0, "utf8"));
    const model = { amounts: [42, 100], parts: ['a"b', '"c"'], separator: " / ", text: " 12.5 " };
    const actual = Object.fromEntries(Object.entries(expressions).map(([name, source]) => [
      name, new Function("model", "return (" + source + ")")(model),
    ]));
    console.log(JSON.stringify(actual));
    """
    result = subprocess.run(
        [runner, "-e", script], input=json.dumps(program), text=True, capture_output=True, check=True
    )
    assert json.loads(result.stdout) == {
        "length": 2,
        "sum": 142,
        "empty_sum": 0,
        "decimal_sum": 3.25,
        "mapped": [43, 101],
        "mapped_again": [43, 101],
        "joined": 'a"b / "c"',
        "number": 12.5,
        "empty_number": 0,
        "invalid_number": False,
        "formatted": "1,234.5",
        "plain": "1234.5",
        "escaped": 'a""b,""c""',
        "encoded": "%E2%82%AC%20%26%20%3D",
    }


def test_comparisons_with_none_also_match_missing_values() -> None:
    value = Expr[str | None](ident("value"))

    assert emit(Cond.equal(value, None).__compile__()) == "(value==null)"
    assert emit(Cond.not_equal(None, value).__compile__()) == "(null!=value)"
    assert emit(Cond.equal(value, "").__compile__()) == '(value==="")'
    assert emit(String.or_empty(value).__compile__()) == '((value==null)?"":value)'


class Lookups(Model):
    scores: State[Mapping[str, int | None]]
    names: State[list[str]]


def test_optional_lookups_return_none_for_missing_values() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")

    operations = {
        "present": Object.get(Lookups.scores, "zero"),
        "null": Object.get(Lookups.scores, "empty"),
        "missing": Object.get(Lookups.scores, "missing"),
        "inherited": Object.get(Lookups.scores, "constructor"),
        "missing_is_none": Cond.equal(Object.get(Lookups.scores, "missing"), None),
        "first": Array.get(Lookups.names, 0),
        "last": Array.get(Lookups.names, -1),
        "outside": Array.get(Lookups.names, 5),
    }
    program = {name: emit(value.__compile__()) for name, value in operations.items()}
    script = """
    const expressions = JSON.parse(require("node:fs").readFileSync(0, "utf8"));
    const model = { scores: { zero: 0, empty: null }, names: ["Emma", "Persuasion"] };
    const actual = Object.fromEntries(Object.entries(expressions).map(([name, source]) => [
      name, new Function("model", "return (" + source + ")")(model),
    ]));
    console.log(JSON.stringify(actual));
    """
    result = subprocess.run(
        [runner, "-e", script], input=json.dumps(program), text=True, capture_output=True, check=True
    )
    assert json.loads(result.stdout) == {
        "present": 0,
        "null": None,
        "missing": None,
        "inherited": None,
        "missing_is_none": True,
        "first": "Emma",
        "last": "Persuasion",
        "outside": None,
    }


class Owner(Model):
    name: State[str]


class Book(Model):
    title: State[str]
    owner: State[Owner]


class Shelf(Model):
    books: State[list[Book]]
    selected: State[str]


def test_model_items_read_fields_as_attributes_and_brackets_stay_a_key_lookup() -> None:
    first = Shelf.books[0]
    assert emit(first.title.__compile__()) == "model.books[0].title"
    assert emit(first.owner.name.__compile__()) == "model.books[0].owner.name"
    titles = Array.map(Shelf.books, lambda book: book.title + "!")
    assert emit(titles.__compile__()) == 'model.books.map(function($fleur0) {return ($fleur0.title+"!");})'
    # A model state used as a key reads the entry for its current value.
    assert emit(record({"a": "A"})[Shelf.selected].__compile__()) == '{a: "A"}[model.selected]'


class Picker(Model):
    books: State[list[Book]]
    current: State[Book | None]
    count: State[int | None]
    flag: State[bool]


def test_when_some_uses_present_values_once_in_javascript() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")

    operations = {
        "present": Cond.when_some(Picker.current, lambda book: book.owner.name, otherwise="nobody"),
        "missing_item": Cond.when_some(Array.get(Picker.books, 5), lambda book: book.title, otherwise="none"),
        "zero": Cond.when_some(Picker.count, lambda count: count + 1, otherwise=-1),
        "chosen": Cond.when(Picker.flag, Picker.books[0], Picker.books[1]).title,
    }
    program = {name: emit(value.__compile__()) for name, value in operations.items()}
    script = """
    const expressions = JSON.parse(require("node:fs").readFileSync(0, "utf8"));
    let reads = 0;
    const model = {
      books: [{ title: "Emma", owner: { name: "Jane" } }, { title: "Persuasion", owner: { name: "Anne" } }],
      get current() { reads++; return this.books[0]; },
      count: 0,
      flag: false,
    };
    const actual = Object.fromEntries(Object.entries(expressions).map(([name, source]) => [
      name, new Function("model", "return (" + source + ")")(model),
    ]));
    console.log(JSON.stringify({ ...actual, reads }));
    """
    result = subprocess.run(
        [runner, "-e", script], input=json.dumps(program), text=True, capture_output=True, check=True
    )
    assert json.loads(result.stdout) == {
        "present": "Jane",
        "missing_item": "none",
        "zero": 1,
        "chosen": "Persuasion",
        "reads": 1,
    }
