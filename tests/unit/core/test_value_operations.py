import json
from collections.abc import Mapping
import shutil
import subprocess

import pytest

from fleur import Array, Cond, Expr, Model, Number, Object, State, String, Url, emit
from fleur.core import array, record
from fleur.core.model import model_ref
from fleur.js.builder import ident


class Values(Model):
    amounts: State[list[int]]
    parts: State[list[str]]
    separator: State[str]
    text: State[str]


values = model_ref(Values, ident("model"))


def _increment(amount: Expr[int]) -> Expr[int]:
    return amount + 1


def test_value_operations_evaluate_in_javascript() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")

    operations = {
        "length": Array.length(values.amounts),
        "sum": Array.sum(values.amounts),
        "empty_sum": Array.sum(array([])),
        "decimal_sum": Array.sum(array([1.25, 2])),
        "mapped": Array.map(values.amounts, _increment),
        "mapped_again": Array.map(values.amounts, _increment),
        "joined": Array.join(values.parts, values.separator),
        "number": Number.from_string(values.text),
        "empty_number": Number.from_string(""),
        "invalid_number": Number.is_finite(Number.from_string("12xyz")),
        "formatted": Number.format(1234.5, locale="ja-JP"),
        "plain": String.from_number(1234.5),
        "escaped": String.replace_all(Array.join(values.parts), '"', '""'),
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


lookups = model_ref(Lookups, ident("model"))


def test_optional_lookups_return_none_for_missing_values() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")

    operations = {
        "present": Object.get(lookups.scores, "zero"),
        "null": Object.get(lookups.scores, "empty"),
        "missing": Object.get(lookups.scores, "missing"),
        "inherited": Object.get(lookups.scores, "constructor"),
        "missing_is_none": Cond.equal(Object.get(lookups.scores, "missing"), None),
        "first": Array.get(lookups.names, 0),
        "last": Array.get(lookups.names, -1),
        "outside": Array.get(lookups.names, 5),
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


shelf = model_ref(Shelf, ident("model"))


def test_model_items_read_fields_as_attributes_and_brackets_stay_a_key_lookup() -> None:
    first = shelf.books[0]
    assert emit(first.title.__compile__()) == "model.books[0].title"
    assert emit(first.owner.name.__compile__()) == "model.books[0].owner.name"
    titles = Array.map(shelf.books, lambda book: book.title + "!")
    assert emit(titles.__compile__()) == 'model.books.map(function($fleur0) {return ($fleur0.title+"!");})'
    # A model state used as a key reads the entry for its current value.
    assert emit(record({"a": "A"})[shelf.selected].__compile__()) == '{a: "A"}[model.selected]'


class Picker(Model):
    books: State[list[Book]]
    current: State[Book | None]
    count: State[int | None]
    flag: State[bool]


picker = model_ref(Picker, ident("model"))


def test_maybe_uses_present_values_once_in_javascript() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")

    operations = {
        "present": Cond.maybe(picker.current, lambda book: book.owner.name, otherwise="nobody"),
        "missing_item": Cond.maybe(Array.get(picker.books, 5), lambda book: book.title, otherwise="none"),
        "zero": Cond.maybe(picker.count, lambda count: count + 1, otherwise=-1),
        "chosen": Cond.when(picker.flag, picker.books[0], picker.books[1]).title,
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
