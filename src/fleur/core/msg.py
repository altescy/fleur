from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Type, cast

from typing_extensions import Self

from fleur.js.ast import ESTreeExpression, ESTreeFunctionBody, ESTreeFunctionExpression, ESTreeReturnStatement
from fleur.js.builder import ident, json_expr, member_expr, object_expr
from fleur.types import ICompilable

from .runtime import MESSAGE_EVENT, MESSAGE_IDENT, MESSAGE_TYPE
from .types import MsgGroupT, OptionalEventT

if TYPE_CHECKING:
    from .model import ModelT
    from .update import CaseValue, Update


class MsgGroup:
    @classmethod
    def caseof(
        cls,
        *cases: tuple[
            "GroupedMsg[Self, Any]",
            "CaseValue[ModelT, Self]",
        ],
    ) -> "Update[ModelT, Self]":
        from .update import Update

        return Update(list(cases))


class MessageEventRef(Generic[OptionalEventT], ICompilable[ESTreeExpression]):
    def __init__(self, path: tuple[str, ...] = ()) -> None:
        self._path = path

    def __getattr__(self, item: str) -> "MessageEventRef[Any]":
        return MessageEventRef((*self._path, item))

    def __getitem__(self, item: str) -> "MessageEventRef[Any]":
        return MessageEventRef((*self._path, item))

    def __compile__(self) -> ESTreeExpression:
        expr: ESTreeExpression = member_expr(ident(MESSAGE_IDENT), MESSAGE_EVENT)
        for part in self._path:
            expr = member_expr(expr, part)
        return expr


class GroupedMsg(Generic[MsgGroupT, OptionalEventT]):
    def __init__(self, group: type[MsgGroupT], name: str, event_payload: OptionalEventT | None = None) -> None:
        self.group = group
        self.name = name
        self._event_payload = event_payload

    @property
    def event(self) -> OptionalEventT:
        return cast(OptionalEventT, MessageEventRef())

    def __call__(
        self,
        update: "CaseValue[ModelT, MsgGroupT]",
    ) -> tuple[Self, "CaseValue[ModelT, MsgGroupT]"]:
        return self, update

    def __compile__(self) -> ESTreeExpression:
        event_expr: ESTreeExpression = ident(MESSAGE_EVENT)
        if self._event_payload is not None:
            if isinstance(self._event_payload, ICompilable):
                event_expr = self._event_payload.__compile__()
            else:
                event_expr = json_expr(cast(Any, self._event_payload))

        return ESTreeFunctionExpression(
            id=None,
            params=[ident(MESSAGE_EVENT)],
            body=ESTreeFunctionBody(
                body=[
                    ESTreeReturnStatement(
                        argument=object_expr(
                            [
                                (MESSAGE_TYPE, json_expr(self.name)),
                                (MESSAGE_EVENT, event_expr),
                            ]
                        )
                    )
                ],
            ),
        )


class Msg(Generic[OptionalEventT]):
    event: OptionalEventT | None

    def __set_name__(self, owner: type[MsgGroup], name: str) -> None:
        self._name = name

    def __init__(self, event: OptionalEventT | None = None) -> None:
        self.event = event
        self._name: str | None = None

    def __get__(self, instance: object, owner: Type[MsgGroupT]) -> GroupedMsg[MsgGroupT, OptionalEventT]:
        if self._name is None:
            raise AttributeError("Msg descriptor is not initialized")
        return GroupedMsg(owner, self._name, self.event)

    def __compile__(self) -> ESTreeExpression:
        if self._name is None:
            raise AttributeError("Msg descriptor is not initialized")
        return json_expr({MESSAGE_TYPE: self._name})
