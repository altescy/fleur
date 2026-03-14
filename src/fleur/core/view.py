import re
from typing import TYPE_CHECKING, Any, Generic

from fleur.js.ast import (
    ESTreeExpression,
    ESTreeFunctionBody,
    ESTreeFunctionExpression,
    ESTreeReturnStatement,
)
from fleur.js.builder import call, concat, literal, member, object_expr

from .names import MODEL_IDENT, RUNTIME_H
from .runtime import runtime_ref
from .types import ModelT_co, MsgGroupT, MsgGroupT_co

if TYPE_CHECKING:
    from .msg import GroupedMsg


class View(Generic[ModelT_co, MsgGroupT_co]):
    def __compile__(self) -> ESTreeExpression:
        raise NotImplementedError


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


class Text(View[ModelT_co, MsgGroupT_co]):
    def __init__(self, text: str) -> None:
        self.text = text

    def __compile__(self) -> ESTreeExpression:
        return call(
            runtime_ref(RUNTIME_H),
            literal("span"),
            object_expr([]),
            _compile_text_expr(self.text),
        )


class VStack(View[ModelT_co, MsgGroupT_co]):
    def __init__(self, *children: View[ModelT_co, MsgGroupT_co]) -> None:
        self.children = children

    def __compile__(self) -> ESTreeExpression:
        args = [literal("div"), object_expr([])]
        args.extend(child.__compile__() for child in self.children)
        return call(runtime_ref(RUNTIME_H), *args)


class Button(View[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: str | View[ModelT_co, MsgGroupT],
        onclick: "GroupedMsg[MsgGroupT, Any]",
    ) -> None:
        self.children = children
        self.onclick = onclick

    def __compile__(self) -> ESTreeExpression:
        onclick_handler = ESTreeFunctionExpression(
            id=None,
            params=[],
            body=ESTreeFunctionBody(
                body=[ESTreeReturnStatement(argument=self.onclick.__compile__())],
            ),
        )
        props = object_expr([("onclick", onclick_handler)])
        child_exprs = [literal(c) if isinstance(c, str) else c.__compile__() for c in self.children]
        return call(runtime_ref(RUNTIME_H), literal("button"), props, *child_exprs)
