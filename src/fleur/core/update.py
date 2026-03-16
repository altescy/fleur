from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Protocol, cast

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeExpression,
    ESTreeFunctionBody,
    ESTreeFunctionExpression,
    ESTreeIdentifier,
    ESTreeReturnStatement,
    ESTreeSwitchCase,
    ESTreeSwitchStatement,
    ESTreeVariableDeclaration,
    ESTreeVariableDeclarator,
)
from fleur.js.builder import call, ident, index_expr, literal, member

from .cmd import Cmd
from .model import ModelOperation, ModelState
from .runtime import MESSAGE_EVENT, MESSAGE_IDENT, MESSAGE_TYPE, MODEL_IDENT, RUNTIME_CMD, RUNTIME_NONE, runtime_call
from .types import ModelT, ModelT_co, MsgGroupT, MsgGroupT_co

if TYPE_CHECKING:
    from .component import Component
    from .msg import GroupedMsg


class CompiledUpdateResult(Protocol):
    def __compile_update_result__(self) -> ESTreeExpression: ...


CaseValue = (
    ModelOperation["ModelT_co"]
    | tuple[ModelOperation["ModelT_co"], Cmd["ModelT_co", "MsgGroupT_co"]]
    | CompiledUpdateResult
)


class ForwardedUpdate(Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        field_name: str,
        component: "Component[Any, Any]",
        tagger: "GroupedMsg[MsgGroupT_co, Any]",
    ) -> None:
        self.field_name = field_name
        self.component = component
        self.tagger = tagger

    def __compile_update_result__(self) -> ESTreeExpression:
        result_ident = ident("_result")
        child_update = self.component.update.__compile__()

        result_value = call(child_update, member(MODEL_IDENT, self.field_name), member(MESSAGE_IDENT, MESSAGE_EVENT))
        result_decl = ESTreeVariableDeclaration(
            declarations=[ESTreeVariableDeclarator(id=result_ident, init=result_value)],
            kind="var",
        )

        model_expr = ModelOperation(self.field_name, "=", index_expr(result_ident, 0)).__compile__()
        cmd_expr = Cmd.map(self.tagger, Cmd(index_expr(result_ident, 1))).__compile__()
        result_pair = ESTreeArrayExpression(elements=[model_expr, cmd_expr])

        return call(
            ESTreeFunctionExpression(
                id=None,
                params=[],
                body=ESTreeFunctionBody(
                    body=[
                        result_decl,
                        ESTreeReturnStatement(argument=result_pair),
                    ]
                ),
            )
        )


def _compile_case_result(value: CaseValue) -> ESTreeExpression:
    if isinstance(value, tuple):
        operation, cmd = value
        return ESTreeArrayExpression(elements=[operation.__compile__(), cmd.__compile__()])

    if isinstance(value, ModelOperation):
        return ESTreeArrayExpression(elements=[value.__compile__(), Cmd.none().__compile__()])

    return value.__compile_update_result__()


class Update(Generic[ModelT_co, MsgGroupT_co]):
    @staticmethod
    def forward(
        field: ModelState[ModelT, Any] | str,
        component: "Component[Any, Any]",
        tagger: "GroupedMsg[MsgGroupT, Any]",
    ) -> ForwardedUpdate[ModelT, MsgGroupT]:
        field_name = field if isinstance(field, str) else field.field_name
        return cast(ForwardedUpdate[ModelT, MsgGroupT], ForwardedUpdate(field_name, component, tagger))

    def __init__(
        self,
        cases: list[
            tuple[
                "GroupedMsg[MsgGroupT_co, Any]",
                CaseValue[ModelT_co, MsgGroupT_co],
            ]
        ],
    ) -> None:
        self._cases = cases

    def __compile__(self) -> ESTreeExpression:
        switch_cases: list[ESTreeSwitchCase] = []

        for grouped_msg, value in self._cases:
            return_stmt = ESTreeReturnStatement(argument=_compile_case_result(value))

            switch_cases.append(ESTreeSwitchCase(test=literal(grouped_msg.name), consequent=[return_stmt]))

        default_stmt = ESTreeReturnStatement(
            argument=ESTreeArrayExpression(
                elements=[ESTreeIdentifier(name=MODEL_IDENT), runtime_call((RUNTIME_CMD, RUNTIME_NONE))],
            ),
        )

        switch_cases.append(ESTreeSwitchCase(test=None, consequent=[default_stmt]))

        switch_stmt = ESTreeSwitchStatement(
            discriminant=member(MESSAGE_IDENT, MESSAGE_TYPE),
            cases=switch_cases,
        )

        params = cast(
            list[Any],
            [
                ESTreeIdentifier(name=MODEL_IDENT),
                ESTreeIdentifier(name=MESSAGE_IDENT),
            ],
        )

        return ESTreeFunctionExpression(
            id=None,
            params=params,
            body=ESTreeFunctionBody(body=[switch_stmt]),
        )
