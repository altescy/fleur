from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

from typing_extensions import TypeAlias

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
from .expr import Expr
from .model import ModelState, ModelUpdate
from .runtime import MESSAGE_EVENT, MESSAGE_IDENT, MESSAGE_TYPE, MODEL_IDENT, RUNTIME_CMD, RUNTIME_NONE, runtime_call
from .types import ModelT, ModelT_co, MsgGroupT, MsgGroupT_co

if TYPE_CHECKING:
    from .component import Component
    from .model import Model
    from .msg import GroupedMsg, MsgGroup


# Method-scoped: class-level variables of `Update` are not solved in its staticmethods.
_ParentModelT = TypeVar("_ParentModelT", bound="Model")
_ParentMsgGroupT = TypeVar("_ParentMsgGroupT", bound="MsgGroup")
_ChildModelT = TypeVar("_ChildModelT", bound="Model")
_ChildMsgGroupT = TypeVar("_ChildMsgGroupT", bound="MsgGroup")


class ForwardedUpdate(Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        field_name: str,
        component: "Component[Any, Any]",
        tagger: "GroupedMsg[MsgGroupT_co, Any, None]",
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

        model_expr = ModelUpdate((self.field_name, Expr(index_expr(result_ident, 0)))).__compile__()
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


# What a case produces. Every form carries the group of the messages it may dispatch, so a
# command or a forwarded child tagged with another group does not match the update.
CaseValue: TypeAlias = Union[
    ModelUpdate[ModelT],
    tuple[ModelUpdate[ModelT], Cmd[ModelT, MsgGroupT]],
    ForwardedUpdate[ModelT, MsgGroupT],
]


def _compile_case_result(value: CaseValue[Any, Any]) -> ESTreeExpression:
    if isinstance(value, tuple):
        operation, cmd = value
        return ESTreeArrayExpression(elements=[operation.__compile__(), cmd.__compile__()])

    if isinstance(value, ModelUpdate):
        return ESTreeArrayExpression(elements=[value.__compile__(), Cmd.none().__compile__()])

    if isinstance(value, ForwardedUpdate):
        return value.__compile_update_result__()

    raise TypeError("Update case must return ModelState.set(...), (ModelUpdate, Cmd), or Update.forward(...)")


class Update(Generic[ModelT, MsgGroupT]):
    """Handle the messages of one group, reading and writing one model type.

    Invariant in both, so that a component takes its model and message group from its update
    and checks the view, commands and subscriptions against them. A covariant parameter would
    let the checker widen the component to a union, and a contravariant group would let a view
    without typed messages erase the group.
    """

    @staticmethod
    def forward(
        field: ModelState[_ParentModelT, _ChildModelT],
        component: "Component[_ChildModelT, _ChildMsgGroupT]",
        tagger: "GroupedMsg[_ParentMsgGroupT, _ChildMsgGroupT, None]",
    ) -> ForwardedUpdate[_ParentModelT, _ParentMsgGroupT]:
        """Delegate a message to a child component stored in `field`.

        The field must hold the child's model type, and the tagger must carry the child's message
        group as its event, as in `CHILD: Msg[ChildMsg] = Msg()`.
        """
        return ForwardedUpdate(field._field_name, component, tagger)

    def __init__(
        self,
        cases: list[
            tuple[
                "GroupedMsg[MsgGroupT, Any, Any]",
                CaseValue[ModelT, MsgGroupT],
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

        params = [
            ESTreeIdentifier(name=MODEL_IDENT),
            ESTreeIdentifier(name=MESSAGE_IDENT),
        ]
        return ESTreeFunctionExpression(
            id=None,
            params=params,
            body=ESTreeFunctionBody(body=[switch_stmt]),
        )
