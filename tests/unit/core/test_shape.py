from collections.abc import Mapping
from typing import Literal

import pytest

from fleur import Model, State
from fleur.core._shape import shape_of


class Tag(Model):
    label: State[str]


class Todo(Model):
    id: State[int]
    title: State[str]
    done: State[bool]
    score: State[float]
    state: State[Literal["open", "done"]]
    note: State[str | None]
    tags: State[list[Tag]]
    counts: State[Mapping[str, int]]


class Node(Model):
    children: State[list["Node"]]


def test_model_shape_lists_each_field() -> None:
    schema = shape_of(list[Todo])
    todo, tag = f"{__name__}.Todo", f"{__name__}.Tag"

    assert schema["root"] == {"kind": "list", "item": {"kind": "ref", "name": todo}}
    assert schema["defs"] == {
        todo: {
            "kind": "object",
            "fields": {
                "id": {"kind": "integer"},
                "title": {"kind": "string"},
                "done": {"kind": "boolean"},
                "score": {"kind": "number"},
                "state": {"kind": "literal", "values": ["open", "done"]},
                "note": {"kind": "union", "options": [{"kind": "string"}, {"kind": "null"}]},
                "tags": {"kind": "list", "item": {"kind": "ref", "name": tag}},
                "counts": {"kind": "dict", "value": {"kind": "integer"}},
            },
        },
        tag: {"kind": "object", "fields": {"label": {"kind": "string"}}},
    }


def test_recursive_model_refers_to_itself() -> None:
    node = f"{__name__}.Node"
    assert shape_of(Node)["defs"] == {
        node: {"kind": "object", "fields": {"children": {"kind": "list", "item": {"kind": "ref", "name": node}}}}
    }


def test_unsupported_types_fail_when_the_request_is_built() -> None:
    with pytest.raises(TypeError, match="Cannot describe the JSON shape"):
        shape_of(set[int])
