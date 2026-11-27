"""Describe the JSON shape of a Fleur value type, for the runtime to validate decoded data."""

import types
from collections.abc import Mapping, Sequence
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

from fleur.types import JsonValue

from .model import Model, State

Shape = dict[str, JsonValue]


def shape_of(value_type: object) -> Shape:
    """Return `{"root": shape, "defs": {...}}`, with each model described once under `defs`."""
    defs: dict[str, JsonValue] = {}
    return {"root": _shape(value_type, defs), "defs": defs}


def _shape(value_type: object, defs: dict[str, JsonValue]) -> JsonValue:
    if value_type is None or value_type is type(None):
        return {"kind": "null"}
    if value_type is Any:
        return {"kind": "any"}
    if value_type is bool:
        return {"kind": "boolean"}
    if value_type is int:
        return {"kind": "integer"}
    if value_type is float:
        return {"kind": "number"}
    if value_type is str:
        return {"kind": "string"}
    if isinstance(value_type, type) and issubclass(value_type, Model):
        return _model_shape(value_type, defs)

    origin, args = get_origin(value_type), get_args(value_type)
    if origin is Literal:
        return {"kind": "literal", "values": [_literal(value) for value in args]}
    if origin is Union or origin is types.UnionType:
        return {"kind": "union", "options": [_shape(option, defs) for option in args]}
    if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
        return {"kind": "list", "item": _shape(args[0], defs)}
    if isinstance(origin, type) and issubclass(origin, Mapping) and len(args) == 2:
        return {"kind": "dict", "value": _shape(args[1], defs)}
    if isinstance(origin, type) and issubclass(origin, Sequence) and origin is not tuple and len(args) == 1:
        return {"kind": "list", "item": _shape(args[0], defs)}
    raise TypeError(f"Cannot describe the JSON shape of {value_type!r}")


def _literal(value: object) -> JsonValue:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"Literal value {value!r} is not JSON")


def _model_shape(model: type[Model], defs: dict[str, JsonValue]) -> JsonValue:
    name = f"{model.__module__}.{model.__qualname__}"
    if name not in defs:
        defs[name] = None  # Reserve the name first, so that a recursive model refers to itself.
        hints = get_type_hints(model)
        fields: dict[str, JsonValue] = {}
        for field in model.__state_fields__:
            annotation = hints[field]
            if get_origin(annotation) is not State:
                raise TypeError(f"{model.__qualname__}.{field} is not declared as State[...]")
            fields[field] = _shape(get_args(annotation)[0], defs)
        defs[name] = {"kind": "object", "fields": fields}
    return {"kind": "ref", "name": name}
