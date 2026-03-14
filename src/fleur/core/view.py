from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Generic

from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, concat, json_expr, literal, member, object_expr
from fleur.types import ICompilable, JsonValue

from .runtime import MODEL_IDENT, RUNTIME_H, runtime_ref
from .types import ModelT_co, MsgGroupT_co


def _compile_text_expr(text: str) -> ESTreeExpression:
    pattern = re.compile(rf"\$\{{{MODEL_IDENT}\.([a-zA-Z_][a-zA-Z0-9_]*)\}}")
    parts: list[ESTreeExpression] = []
    cursor = 0

    for match in pattern.finditer(text):
        if cursor < match.start():
            parts.append(literal(text[cursor : match.start()]))
        parts.append(member(MODEL_IDENT, match.group(1)))
        cursor = match.end()

    if cursor < len(text):
        parts.append(literal(text[cursor:]))

    if not parts:
        return literal("")

    expr = parts[0]
    for next_expr in parts[1:]:
        expr = concat(expr, next_expr)
    return expr


def _compile_prop_value(value: ICompilable[ESTreeExpression] | JsonValue) -> ESTreeExpression:
    if isinstance(value, ICompilable):
        return value.__compile__()
    return json_expr(value)


def _compile_child(child: JsonValue | View[ModelT_co, MsgGroupT_co]) -> ESTreeExpression:
    if isinstance(child, View):
        return child.__compile__()
    if isinstance(child, str):
        return _compile_text_expr(child)
    return json_expr(child)


class View(Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: JsonValue | "View[ModelT_co, MsgGroupT_co]",
        tag: str,
        props: Mapping[str, ICompilable[ESTreeExpression] | JsonValue],
    ) -> None:
        self._tag = tag
        self._props = props
        self._children = children

    def __compile__(self) -> ESTreeExpression:
        return call(
            runtime_ref(RUNTIME_H),
            literal(self._tag),
            object_expr((k, _compile_prop_value(v)) for k, v in self._props.items()),
            *(_compile_child(child) for child in self._children),
        )
