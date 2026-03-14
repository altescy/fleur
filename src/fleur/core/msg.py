from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Type, overload

from typing_extensions import Self

from fleur.js.ast import ESTreeExpression, ESTreeFunctionBody, ESTreeFunctionExpression, ESTreeReturnStatement
from fleur.js.builder import json_expr

from .runtime import MESSAGE_TYPE
from .types import MsgGroupT, OptionalEventT

if TYPE_CHECKING:
    from .cmd import Cmd
    from .model import ModelOperation, ModelT
    from .update import Update


class MsgGroup:
    @classmethod
    def caseof(
        cls,
        *cases: tuple[
            "GroupedMsg[Self, Any]",
            ModelOperation["ModelT"] | tuple[ModelOperation["ModelT"], "Cmd[ModelT, Self]"],
        ],
    ) -> "Update[ModelT, Self]":
        from .update import Update

        return Update(list(cases))


class GroupedMsg(Generic[MsgGroupT, OptionalEventT]):
    def __init__(self, group: type[MsgGroupT], name: str, event: OptionalEventT | None = None) -> None:
        self.group = group
        self.name = name
        self.event = event

    def __compile__(self) -> ESTreeExpression:

        return ESTreeFunctionExpression(
            id=None,
            params=[],
            body=ESTreeFunctionBody(
                body=[ESTreeReturnStatement(argument=json_expr({MESSAGE_TYPE: self.name}))],
            ),
        )


class Msg(Generic[OptionalEventT]):
    event: OptionalEventT | None

    def __set_name__(self, owner: type[MsgGroup], name: str) -> None:
        self._name = name

    @overload
    def __new__(cls) -> "Msg[None]": ...
    @overload
    def __new__(cls, event: None) -> "Msg[None]": ...
    @overload
    def __new__(cls, event: OptionalEventT) -> "Msg[OptionalEventT]": ...

    def __new__(cls, event: OptionalEventT | None = None) -> "Msg[OptionalEventT]" | "Msg[None]":
        return super().__new__(cls)

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
