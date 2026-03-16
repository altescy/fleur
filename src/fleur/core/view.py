from __future__ import annotations

import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Generic, cast

from fleur.js.ast import ESTreeExpression, ESTreeFunctionBody, ESTreeFunctionExpression, ESTreeReturnStatement
from fleur.js.builder import call, concat, ident, json_expr, literal, member, object_expr
from fleur.types import ICompilable, JsonValue

from .runtime import MODEL_IDENT, RUNTIME_H, RUNTIME_HTML, RUNTIME_MAP, runtime_call, runtime_ref
from .types import ModelT, ModelT_co, MsgGroupT, MsgGroupT_co

if TYPE_CHECKING:
    from .model import ModelState
    from .msg import GroupedMsg


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

    @staticmethod
    def map(
        tagger: "GroupedMsg[MsgGroupT, Any]", view: "View[ModelT_co, MsgGroupT_co]"
    ) -> "MappedView[ModelT_co, MsgGroupT_co, MsgGroupT]":
        return cast(MappedView[ModelT_co, MsgGroupT_co, MsgGroupT], MappedView(tagger, view))

    @staticmethod
    def forward(
        field: "ModelState[ModelT, ModelT_co] | str",
        view: "View[ModelT_co, MsgGroupT_co]",
        tagger: "GroupedMsg[MsgGroupT, Any]",
    ) -> "ForwardedView[ModelT, ModelT_co, MsgGroupT_co, MsgGroupT]":
        field_name = field if isinstance(field, str) else cast("ModelState[ModelT, ModelT_co]", field).field_name
        return cast(
            ForwardedView[ModelT, ModelT_co, MsgGroupT_co, MsgGroupT],
            ForwardedView(field_name, tagger, view),
        )


class MappedView(View[ModelT_co, MsgGroupT], Generic[ModelT_co, MsgGroupT_co, MsgGroupT]):
    def __init__(self, tagger: "GroupedMsg[MsgGroupT, Any]", view: View[ModelT_co, MsgGroupT_co]) -> None:
        self._tagger = tagger
        self._view = view

    def __compile__(self) -> ESTreeExpression:
        return runtime_call((RUNTIME_HTML, RUNTIME_MAP), self._tagger.__compile__(), self._view.__compile__())


class ForwardedView(View[ModelT, MsgGroupT], Generic[ModelT, ModelT_co, MsgGroupT_co, MsgGroupT]):
    def __init__(
        self, field_name: str, tagger: "GroupedMsg[MsgGroupT, Any]", view: View[ModelT_co, MsgGroupT_co]
    ) -> None:
        self._field_name = field_name
        self._tagger = tagger
        self._view = view

    def __compile__(self) -> ESTreeExpression:
        mapped_child = runtime_call((RUNTIME_HTML, RUNTIME_MAP), self._tagger.__compile__(), self._view.__compile__())
        return call(
            ESTreeFunctionExpression(
                id=None,
                params=[ident(MODEL_IDENT)],
                body=ESTreeFunctionBody(body=[ESTreeReturnStatement(argument=mapped_child)]),
            ),
            member(MODEL_IDENT, self._field_name),
        )
