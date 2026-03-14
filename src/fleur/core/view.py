import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Generic

from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, concat, literal, member, object_expr
from fleur.types import ICompilable, JsonValue

from .runtime import MODEL_IDENT, RUNTIME_H, runtime_ref
from .types import ModelT_co, MsgGroupT, MsgGroupT_co

if TYPE_CHECKING:
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


class View(Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: "JsonValue | View[ModelT_co, MsgGroupT_co]",
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
            object_expr(
                [(k, v.__compile__() if isinstance(v, ICompilable) else literal(v)) for k, v in self._props.items()]
            ),
            *(
                child.__compile__()
                if isinstance(child, View)
                else (_compile_text_expr(child) if isinstance(child, str) else literal(child))
                for child in self._children
            ),
        )


class Text(View[ModelT_co, MsgGroupT_co]):
    def __init__(self, text: str) -> None:
        super().__init__(text, tag="span", props={})


class VStack(View[ModelT_co, MsgGroupT_co]):
    def __init__(self, *children: View[ModelT_co, MsgGroupT_co]) -> None:
        return super().__init__(*children, tag="div", props={})


class Button(View[ModelT_co, MsgGroupT]):
    def __init__(
        self,
        *children: str | View[ModelT_co, MsgGroupT],
        onclick: "GroupedMsg[MsgGroupT, Any]",
    ) -> None:
        super().__init__(*children, tag="button", props={"onclick": onclick})
