from __future__ import annotations

import re
from collections.abc import Iterable

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeBinaryExpression,
    ESTreeCallExpression,
    ESTreeExpression,
    ESTreeIdentifier,
    ESTreeLiteral,
    ESTreeMemberExpression,
    ESTreeObjectExpression,
    ESTreeObjectProperty,
)
from fleur.types import JsonValue

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")


def ident(name: str) -> ESTreeIdentifier:
    return ESTreeIdentifier(name=name)


def literal(value: JsonValue) -> ESTreeLiteral:
    return ESTreeLiteral(value=value)


def member(object_name: str, property_name: str) -> ESTreeMemberExpression:
    return member_expr(ident(object_name), property_name)


def member_expr(object_expr: ESTreeExpression, property_name: str) -> ESTreeMemberExpression:
    return ESTreeMemberExpression(
        object=object_expr,
        property=ident(property_name),
        computed=False,
    )


def index_expr(object_expr: ESTreeExpression, index: int) -> ESTreeMemberExpression:
    return ESTreeMemberExpression(
        object=object_expr,
        property=literal(index),
        computed=True,
    )


def call(callee: ESTreeExpression, *args: ESTreeExpression) -> ESTreeCallExpression:
    return ESTreeCallExpression(callee=callee, arguments=list(args))


def object_expr(properties: Iterable[tuple[str, ESTreeExpression]]) -> ESTreeObjectExpression:
    return ESTreeObjectExpression(
        properties=[
            ESTreeObjectProperty(
                key=ident(key) if _IDENTIFIER_RE.match(key) else literal(key),
                value=value,
                kind="init",
            )
            for key, value in properties
        ],
    )


def json_expr(value: JsonValue) -> ESTreeExpression:
    if isinstance(value, dict):
        return ESTreeObjectExpression(
            properties=[
                ESTreeObjectProperty(
                    key=ident(k) if _IDENTIFIER_RE.match(k) else literal(k),
                    value=json_expr(v),
                    kind="init",
                )
                for k, v in value.items()
            ],
        )

    if isinstance(value, list):
        return ESTreeArrayExpression(elements=[json_expr(v) for v in value])

    return literal(value)


def concat(left: ESTreeExpression, right: ESTreeExpression) -> ESTreeBinaryExpression:
    return ESTreeBinaryExpression(operator="+", left=left, right=right)
