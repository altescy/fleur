import json
import shutil
import subprocess

import pytest

from fleur import Model, State, Url, emit


class Route(Model):
    owner: State[str]
    number: State[int]


def test_path_encodes_each_parameter_in_javascript() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")
    path = Url.path("/users/{owner}/items/{number}/{owner}.json", owner=Route.owner, number=Route.number)
    script = f"const model = {{owner: 'a/b c?', number: 7}}; console.log(JSON.stringify({emit(path.__compile__())}))"
    result = subprocess.run([runner, "-e", script], text=True, capture_output=True, check=True)

    assert json.loads(result.stdout) == "/users/a%2Fb%20c%3F/items/7/a%2Fb%20c%3F.json"


def test_path_without_parameters_is_the_template() -> None:
    assert emit(Url.path("/status").__compile__()) == '"/status"'


@pytest.mark.parametrize(
    ("template", "params", "message"),
    [
        ("/todos/{id}", {}, "missing id"),
        ("/todos", {"id": 1}, "unused id"),
        ("/todos/{id}", {"todo": 1}, "missing id; unused todo"),
        ("/todos/{id", {"id": 1}, "brace outside"),
    ],
)
def test_path_rejects_mismatched_parameters(template: str, params: dict[str, int], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Url.path(template, **params)
