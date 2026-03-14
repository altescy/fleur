from typing import TYPE_CHECKING, Any, Generic, cast

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeExpression,
    ESTreeFunctionBody,
    ESTreeFunctionExpression,
    ESTreeIdentifier,
    ESTreeReturnStatement,
    ESTreeSwitchCase,
    ESTreeSwitchStatement,
)
from fleur.js.builder import literal, member

from .cmd import Cmd
from .model import ModelOperation
from .names import MESSAGE_IDENT, MESSAGE_TYPE, MODEL_IDENT, RUNTIME_CMD, RUNTIME_NONE
from .runtime import runtime_call
from .types import ModelT_co, MsgGroupT_co

if TYPE_CHECKING:
    from .msg import GroupedMsg


class Update(Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        cases: list[
            tuple[
                "GroupedMsg[MsgGroupT_co, object]",
                ModelOperation["ModelT_co"] | tuple[ModelOperation["ModelT_co"], Cmd["ModelT_co", "MsgGroupT_co"]],
            ]
        ],
    ) -> None:
        self._cases = cases

    def __compile__(self) -> ESTreeExpression:
        switch_cases: list[ESTreeSwitchCase] = []

        for grouped_msg, operation_or_pair in self._cases:
            if isinstance(operation_or_pair, tuple):
                operation, cmd = operation_or_pair
            else:
                operation = operation_or_pair
                cmd = Cmd.none()

            model_expr = operation.__compile__()
            cmd_expr = cmd.__compile__()

            return_stmt = ESTreeReturnStatement(
                argument=ESTreeArrayExpression(elements=[model_expr, cmd_expr]),
            )

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
