from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Generic, Type, cast

from typing_extensions import Self, TypeVar

from fleur.js.ast import ESTreeExpression, ESTreeFunctionBody, ESTreeFunctionExpression, ESTreeReturnStatement
from fleur.js.builder import ident, json_expr, member_expr, object_expr
from fleur.types import ICompilable

from .expr import Expr
from .runtime import MESSAGE_CONTEXT, MESSAGE_EVENT, MESSAGE_IDENT, MESSAGE_TYPE
from .types import ModelT, MsgGroupT, OptionalContextT, OptionalEventT

BoundContextT = TypeVar("BoundContextT")

if TYPE_CHECKING:
    from .update import CaseValue, Update


class MsgGroup:
    @classmethod
    def caseof(
        cls,
        *cases: tuple[
            "GroupedMsg[Self, Any, Any]",
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


class MessageContextRef(Generic[OptionalContextT], ICompilable[ESTreeExpression]):
    def __init__(self, path: tuple[str, ...] = ()) -> None:
        self._path = path

    def __getattr__(self, item: str) -> "MessageContextRef[Any]":
        return MessageContextRef((*self._path, item))

    def __getitem__(self, item: str) -> "MessageContextRef[Any]":
        return MessageContextRef((*self._path, item))

    def __compile__(self) -> ESTreeExpression:
        expr: ESTreeExpression = member_expr(ident(MESSAGE_IDENT), MESSAGE_CONTEXT)
        for part in self._path:
            expr = member_expr(expr, part)
        return expr


class GroupedMsg(Expr[Mapping[str, Any]], Generic[MsgGroupT, OptionalEventT, OptionalContextT]):
    def __init__(
        self,
        group: type[MsgGroupT],
        name: str,
        event_payload: OptionalEventT | None = None,
        context_payload: OptionalContextT | None = None,
    ) -> None:
        self.group = group
        self.name = name
        self._event_payload = event_payload
        self._context_payload = context_payload

    @property
    def event(self) -> OptionalEventT:
        return cast(OptionalEventT, MessageEventRef())

    @property
    def context(self) -> OptionalContextT:
        return cast(OptionalContextT, MessageContextRef())

    def bind(self, context: OptionalContextT) -> Self:
        return self.__class__(self.group, self.name, self._event_payload, context)

    def then(
        self,
        update: "CaseValue[ModelT, MsgGroupT]",
    ) -> tuple[Self, "CaseValue[ModelT, MsgGroupT]"]:
        return self, update

    def __compile__(self) -> ESTreeExpression:
        event_expr: ESTreeExpression = ident(MESSAGE_EVENT)
        context_expr: ESTreeExpression = json_expr(None)

        if self._event_payload is not None:
            if isinstance(self._event_payload, ICompilable):
                event_expr = self._event_payload.__compile__()
            else:
                event_expr = json_expr(cast(Any, self._event_payload))

        if self._context_payload is not None:
            if isinstance(self._context_payload, ICompilable):
                context_expr = self._context_payload.__compile__()
            else:
                context_expr = json_expr(cast(Any, self._context_payload))

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
                                (MESSAGE_CONTEXT, context_expr),
                            ]
                        )
                    )
                ],
            ),
        )


class Msg(Generic[OptionalEventT, OptionalContextT]):
    event: OptionalEventT | None

    def __set_name__(self, owner: type[MsgGroup], name: str) -> None:
        self._name = name

    def __init__(self, event: OptionalEventT | None = None) -> None:
        self.event = event
        self._name: str | None = None

    def __get__(
        self, instance: None, owner: Type[MsgGroupT]
    ) -> GroupedMsg[MsgGroupT, OptionalEventT, OptionalContextT]:
        del instance
        if self._name is None:
            raise AttributeError("Msg descriptor is not initialized")
        return GroupedMsg(owner, self._name, self.event)

    def __compile__(self) -> ESTreeExpression:
        if self._name is None:
            raise AttributeError("Msg descriptor is not initialized")
        return json_expr({MESSAGE_TYPE: self._name})
