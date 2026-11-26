import json
import shutil
import subprocess

import pytest

from fleur import Array, Model, Number, State, String, Url, emit
from fleur.core import array


class Values(Model):
    amounts: State[list[int]]
    parts: State[list[str]]
    separator: State[str]
    text: State[str]


def test_value_operations_evaluate_in_javascript() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")

    operations = {
        "length": Array.length(Values.amounts),
        "sum": Array.sum(Values.amounts),
        "empty_sum": Array.sum(array([])),
        "decimal_sum": Array.sum(array([1.25, 2])),
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
        "joined": 'a"b / "c"',
        "number": 12.5,
        "empty_number": 0,
        "invalid_number": False,
        "formatted": "1,234.5",
        "plain": "1234.5",
        "escaped": 'a""b,""c""',
        "encoded": "%E2%82%AC%20%26%20%3D",
    }
