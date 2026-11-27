from __future__ import annotations

import operator
from functools import reduce
from typing import TYPE_CHECKING, Any, Generic, Type, cast

from typing_extensions import Self, TypeVar

from fleur.js.ast import ESTreeExpression, ESTreeFunctionBody, ESTreeFunctionExpression, ESTreeReturnStatement
from fleur.js.builder import ident, json_expr, member_expr, object_expr

from .expr import Expr, ValueRef, ensure_expr
from .model import Model
from .runtime import MESSAGE_CONTEXT, MESSAGE_EVENT, MESSAGE_IDENT, MESSAGE_TYPE
from .types import ModelT, MsgGroupT, OptionalContextT, OptionalEventT

BoundContextT = TypeVar("BoundContextT")

if TYPE_CHECKING:
    from .update import CaseValue, Update


class MsgGroup:
    @classmethod
    def cases(
        cls,
        *cases: tuple["GroupedMsg[Self, Any, Any]", "CaseValue[ModelT, Self]"],
    ) -> "Update[ModelT, Self]":
        """Handle every message of the group, like an exhaustive Elm `case`."""
        from .update import Update

        declared = {name for base in cls.__mro__ for name, value in vars(base).items() if isinstance(value, Msg)}
        missing = sorted(declared - {message.name for message, _ in cases})
        if missing:
            raise ValueError(f"{cls.__name__}.cases() does not handle: {', '.join(missing)}")
        return Update(list(cases))


class MessageEventRef(ValueRef, Generic[OptionalEventT]):
    """The payload of the message being handled, `message.event`, with fields read as attributes.

    It is an expression, so operators such as `+` work on it and its fields at runtime.
    """

    def __init__(self, path: tuple[str, ...] = ()) -> None:
        expr: ESTreeExpression = member_expr(ident(MESSAGE_IDENT), MESSAGE_EVENT)
        for part in path:
            expr = member_expr(expr, part)
        super().__init__(expr)
        self._path = path

    def __getattr__(self, name: str) -> "MessageEventRef[Any]":
        if name.startswith("_"):
            raise AttributeError(name)
        return MessageEventRef((*self._path, name))


class MessageContextRef(ValueRef, Generic[OptionalContextT]):
    """The context bound to the message being handled, `message.context`."""

    def __init__(self, path: tuple[str, ...] = ()) -> None:
        expr: ESTreeExpression = member_expr(ident(MESSAGE_IDENT), MESSAGE_CONTEXT)
        for part in path:
            expr = member_expr(expr, part)
        super().__init__(expr)
        self._path = path

    def __getattr__(self, name: str) -> "MessageContextRef[Any]":
        if name.startswith("_"):
            raise AttributeError(name)
        return MessageContextRef((*self._path, name))


class GroupedMsg(Model, Generic[MsgGroupT, OptionalEventT, OptionalContextT]):
    group: type[MsgGroupT]
    name: str

    def __init__(
        self,
        group: type[MsgGroupT],
        name: str,
        context_payload: OptionalContextT | Expr[OptionalContextT] | None = None,
    ) -> None:
        self.group = group
        self.name = name
        self._context_payload = context_payload

    def __hash__(self) -> int:
        return hash((self.group, self.name))

    @property
    def event(self) -> OptionalEventT:
        return cast(OptionalEventT, MessageEventRef())

    @property
    def context(self) -> OptionalContextT:
        return cast(OptionalContextT, MessageContextRef())

    def bind(self, context: OptionalContextT | Expr[OptionalContextT]) -> "GroupedMsg[MsgGroupT, OptionalEventT, None]":
        """Supply the context, giving a message that an event handler can dispatch as is.

        The context type of a `GroupedMsg` is what a dispatcher still has to provide, so a bound
        message has `None`; the update reads the value through the unbound `Msg.context`.
        """
        return cast(
            "GroupedMsg[MsgGroupT, OptionalEventT, None]",
            GroupedMsg(self.group, self.name, context),
        )

    def then(
        self,
        update: "CaseValue[ModelT, MsgGroupT]",
        *updates: "CaseValue[ModelT, MsgGroupT]",
    ) -> tuple[Self, "CaseValue[ModelT, MsgGroupT]"]:
        return self, reduce(operator.and_, updates, update)

    def __compile__(self) -> ESTreeExpression:
        context_expr: ESTreeExpression = json_expr(None)
        if self._context_payload is not None:
            context_expr = ensure_expr(self._context_payload)

        return ESTreeFunctionExpression(
            id=None,
            params=[ident(MESSAGE_EVENT)],
            body=ESTreeFunctionBody(
                body=[
                    ESTreeReturnStatement(
                        argument=object_expr(
                            [
                                (MESSAGE_TYPE, json_expr(self.name)),
                                (MESSAGE_EVENT, ident(MESSAGE_EVENT)),
                                (MESSAGE_CONTEXT, context_expr),
                            ]
                        )
                    )
                ],
            ),
        )


class Msg(Generic[OptionalEventT, OptionalContextT]):
    """Declare a message of a `MsgGroup` with its event and context types."""

    def __set_name__(self, owner: type[MsgGroup], name: str) -> None:
        self._name = name

    def __init__(self) -> None:
        self._name: str | None = None

    def __get__(
        self, instance: None, owner: Type[MsgGroupT]
    ) -> GroupedMsg[MsgGroupT, OptionalEventT, OptionalContextT]:
        del instance
        if self._name is None:
            raise AttributeError("Msg descriptor is not initialized")
        return GroupedMsg(owner, self._name)
