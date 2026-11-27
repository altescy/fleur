from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Generic, TypeAlias, Union

from fleur.core.model import Model, ModelState
from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeExpression,
    ESTreeFunctionBody,
    ESTreeFunctionExpression,
    ESTreeReturnStatement,
)
from fleur.js.builder import call, concat, ident, json_expr, literal, member, member_expr, object_expr
from fleur.types import ICompilable, JsonValue

from .dom import DomEffect, EventBinding
from .expr import Expr
from .msg import GroupedMsg
from .runtime import MODEL_IDENT, RUNTIME_H, RUNTIME_HTML, RUNTIME_MAP, runtime_call, runtime_ref
from .types import ModelT, ModelT_co, MsgGroupT, MsgGroupT_co

_ViewChild = Union[JsonValue, Model, Sequence["_ViewChild"]]
_ViewProp = Union[JsonValue, GroupedMsg[Any, Any, Any], Mapping[str, "_ViewProp"], Sequence["_ViewProp"]]
_ViewProps = Mapping[str, _ViewProp]
ViewChild: TypeAlias = Union[_ViewChild, Expr[_ViewChild]]
ViewProp: TypeAlias = Union[
    _ViewProp,
    Expr[_ViewProp],
    DomEffect,
    EventBinding[Any, Any, Any],
    Mapping[str, "ViewProp"],
    Sequence["ViewProp"],
]
ViewProps: TypeAlias = Union[Mapping[str, ViewProp], Expr[_ViewProps]]


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


def _compile_prop_value(value: ViewProp) -> ESTreeExpression:
    if isinstance(value, (Expr, GroupedMsg, DomEffect, EventBinding)):
        return value.__compile__()
    if isinstance(value, Mapping):
        return object_expr((k, _compile_prop_value(v)) for k, v in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return ESTreeArrayExpression(elements=[_compile_prop_value(item) for item in value])
    return json_expr(value)


def _compile_child(child: ViewChild) -> ESTreeExpression:
    if isinstance(child, ICompilable):
        return child.__compile__()
    if isinstance(child, str):
        return _compile_text_expr(child)
    if isinstance(child, Sequence):
        return ESTreeArrayExpression(elements=[_compile_child(item) for item in child])
    return json_expr(child)


class View(Model, Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        tag: str,
        props: ViewProps,
    ) -> None:
        self._tag = tag
        self._props = props
        self._children = children

    def __compile__(self) -> ESTreeExpression:
        if isinstance(self._props, Expr):
            compiled_props = self._props.__compile__()
        else:
            compiled_props = object_expr((k, _compile_prop_value(v)) for k, v in self._props.items())
        return call(
            runtime_ref(RUNTIME_H),
            literal(self._tag),
            compiled_props,
            *(_compile_child(child) for child in self._children),
        )

    @staticmethod
    def dom_effect(*effects: DomEffect) -> Mapping[str, ViewProp]:
        """Attach effects by key. Merging props preserves effects with distinct keys."""
        return {f"domEffect:{effect.key}": effect for effect in effects}

    @staticmethod
    def extend_props(props: ViewProps, extra: ViewProps) -> ViewProps:
        """Add or replace view props, evaluating dynamic inputs once."""
        if isinstance(extra, Mapping) and not extra:
            return props
        if isinstance(props, Mapping) and isinstance(extra, Mapping):
            return {**props, **extra}
        return Expr(
            call(
                member_expr(ident("Object"), "assign"),
                object_expr([]),
                _compile_prop_value(props),
                _compile_prop_value(extra),
            )
        )

    @staticmethod
    def merge_styles(
        props: ViewProps, defaults: Mapping[str, ViewProp], overrides: Mapping[str, ViewProp]
    ) -> ViewProps:
        """Layer CSS defaults, supplied properties, and overrides in CSS declaration order."""
        if not defaults and not overrides:
            return props
        if isinstance(props, Expr) or isinstance(props.get("style"), Expr):
            return Expr(
                runtime_call(
                    ("mergeStyleProps",),
                    _compile_prop_value(props),
                    _compile_prop_value(defaults),
                    _compile_prop_value(overrides),
                )
            )
        supplied = props.get("style")
        style: dict[str, ViewProp] = {}
        for layer in (defaults, supplied if isinstance(supplied, Mapping) else {}, overrides):
            for key, value in layer.items():
                style.pop(key, None)
                style[key] = value
        return {**props, "style": style}

    @staticmethod
    def map(
        tagger: "GroupedMsg[MsgGroupT, Any, Any]",
        view: "View[ModelT_co, MsgGroupT_co]",
    ) -> "MappedView[ModelT_co, MsgGroupT_co, MsgGroupT]":
        return MappedView(tagger, view)

    @staticmethod
    def forward(
        field: ModelState[ModelT, ModelT_co] | str,
        view: "View[ModelT_co, MsgGroupT_co]",
        tagger: "GroupedMsg[MsgGroupT, Any, Any]",
    ) -> "ForwardedView[ModelT, ModelT_co, MsgGroupT_co, MsgGroupT]":
        field_name = field if isinstance(field, str) else field._field_name
        return ForwardedView(field_name, tagger, view)


class MappedView(View[ModelT_co, MsgGroupT], Generic[ModelT_co, MsgGroupT_co, MsgGroupT]):
    def __init__(self, tagger: "GroupedMsg[MsgGroupT, Any, Any]", view: View[ModelT_co, MsgGroupT_co]) -> None:
        self._tagger = tagger
        self._view = view

    def __compile__(self) -> ESTreeExpression:
        return runtime_call((RUNTIME_HTML, RUNTIME_MAP), self._tagger.__compile__(), self._view.__compile__())


class ForwardedView(View[ModelT, MsgGroupT], Generic[ModelT, ModelT_co, MsgGroupT_co, MsgGroupT]):
    def __init__(
        self, field_name: str, tagger: "GroupedMsg[MsgGroupT, Any, Any]", view: View[ModelT_co, MsgGroupT_co]
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
