from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Generic, TypeAlias, TypeVar, Union

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

if TYPE_CHECKING:
    from .component import Component
    from .msg import MsgGroup

# Method-scoped (class-level variables are not solved in staticmethods) and invariant, so that
# a forwarded component must have exactly the model type of its field.
_ChildModelT = TypeVar("_ChildModelT", bound=Model)
_ChildMsgGroupT = TypeVar("_ChildMsgGroupT", bound="MsgGroup")

# Props carry the message group of the messages they dispatch. A message must have its
# context bound, because the runtime dispatches it as is.
_ViewProp: TypeAlias = Union[
    JsonValue,
    GroupedMsg[MsgGroupT, Any, None],
    Mapping[str, "_ViewProp[MsgGroupT]"],
    Sequence["_ViewProp[MsgGroupT]"],
]
_ViewProps: TypeAlias = Mapping[str, _ViewProp[MsgGroupT]]
ViewProp: TypeAlias = Union[
    _ViewProp[MsgGroupT],
    Expr[_ViewProp[MsgGroupT]],
    DomEffect,
    EventBinding[MsgGroupT, Any],
    Mapping[str, "ViewProp[MsgGroupT]"],
    Sequence["ViewProp[MsgGroupT]"],
]
ViewProps: TypeAlias = Union[Mapping[str, ViewProp[MsgGroupT]], Expr[_ViewProps[MsgGroupT]]]


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


def _compile_prop_value(value: ViewProp[Any]) -> ESTreeExpression:
    if isinstance(value, (Expr, GroupedMsg, DomEffect, EventBinding)):
        return value.__compile__()
    if isinstance(value, Mapping):
        return object_expr((k, _compile_prop_value(v)) for k, v in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return ESTreeArrayExpression(elements=[_compile_prop_value(item) for item in value])
    return json_expr(value)


def _compile_child(child: ViewChild[Any, Any]) -> ESTreeExpression:
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
        *children: ViewChild[ModelT_co, MsgGroupT_co],
        tag: str,
        props: ViewProps[MsgGroupT_co],
    ) -> None:
        self._tag = tag
        self._props: ViewProps[Any] = props
        self._children: tuple[ViewChild[Any, Any], ...] = children

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
    def dom_effect(*effects: DomEffect) -> Mapping[str, DomEffect]:
        """Attach effects by key. Merging props preserves effects with distinct keys."""
        return {f"domEffect:{effect.key}": effect for effect in effects}

    @staticmethod
    def extend_props(props: ViewProps[MsgGroupT], extra: ViewProps[MsgGroupT]) -> ViewProps[MsgGroupT]:
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
        props: ViewProps[MsgGroupT],
        defaults: Mapping[str, ViewProp[MsgGroupT]],
        overrides: Mapping[str, ViewProp[MsgGroupT]],
    ) -> ViewProps[MsgGroupT]:
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
        style: dict[str, ViewProp[MsgGroupT]] = {}
        for layer in (defaults, supplied if isinstance(supplied, Mapping) else {}, overrides):
            for key, value in layer.items():
                style.pop(key, None)
                style[key] = value
        return {**props, "style": style}

    @staticmethod
    def map(
        tagger: "GroupedMsg[MsgGroupT, _ChildMsgGroupT, None]",
        view: "View[_ChildModelT, _ChildMsgGroupT]",
    ) -> "MappedView[_ChildModelT, _ChildMsgGroupT, MsgGroupT]":
        """Wrap each message of a child view in the tagger, whose event is the child's group."""
        return MappedView(tagger, view)

    @staticmethod
    def forward(
        field: ModelState[ModelT, _ChildModelT],
        component: Component[_ChildModelT, _ChildMsgGroupT],
        tagger: "GroupedMsg[MsgGroupT, _ChildMsgGroupT, None]",
    ) -> "ForwardedView[ModelT, _ChildModelT, _ChildMsgGroupT, MsgGroupT]":
        """Render a child component stored in `field`, whose model type must match."""
        return ForwardedView(field._field_name, tagger, component.view)


# A child carries the model and message group of the views it contains, so that a parent view,
# and in the end the component, sees every message its subtree can dispatch. Defined after `View`,
# which it refers to at runtime.
_ViewNode: TypeAlias = Union[JsonValue, View[ModelT_co, MsgGroupT_co], Sequence["_ViewNode[ModelT_co, MsgGroupT_co]"]]
ViewChild: TypeAlias = Union[_ViewNode[ModelT_co, MsgGroupT_co], Expr[_ViewNode[ModelT_co, MsgGroupT_co]]]


class MappedView(View[ModelT_co, MsgGroupT], Generic[ModelT_co, MsgGroupT_co, MsgGroupT]):
    def __init__(self, tagger: "GroupedMsg[MsgGroupT, Any, None]", view: View[ModelT_co, MsgGroupT_co]) -> None:
        self._tagger = tagger
        self._view = view

    def __compile__(self) -> ESTreeExpression:
        return runtime_call((RUNTIME_HTML, RUNTIME_MAP), self._tagger.__compile__(), self._view.__compile__())


class ForwardedView(View[ModelT, MsgGroupT], Generic[ModelT, ModelT_co, MsgGroupT_co, MsgGroupT]):
    def __init__(
        self, field_name: str, tagger: "GroupedMsg[MsgGroupT, Any, None]", view: View[ModelT_co, MsgGroupT_co]
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
