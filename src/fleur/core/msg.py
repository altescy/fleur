from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, Type, cast, overload

from typing_extensions import Self, TypeVar

from fleur.js.ast import ESTreeExpression, ESTreeFunctionBody, ESTreeFunctionExpression, ESTreeReturnStatement
from fleur.js.builder import ident, json_expr, member_expr, object_expr

from .expr import Expr, ValueRef, ensure_expr
from .model import Model
from .runtime import MESSAGE_CONTEXT, MESSAGE_EVENT, MESSAGE_IDENT, MESSAGE_TYPE, MessageFieldName
from .types import ModelT, MsgGroupT, OptionalContextT, OptionalEventT

BoundContextT = TypeVar("BoundContextT")

if TYPE_CHECKING:
    from .update import CaseValue, Update


def _message_ref(part: MessageFieldName) -> ValueRef:
    """The event or context of the message being handled, whose fields read as attributes."""
    return ValueRef(member_expr(ident(MESSAGE_IDENT), part))


def _checked_case(name: str, value: object) -> "CaseValue[Any, Any]":
    from .update import is_case_value

    if not is_case_value(value):
        raise TypeError(
            f"The case of {name} must return State.set(...), (ModelUpdate, Cmd), or Update.forward(...), "
            f"not {type(value).__name__}"
        )
    return cast("CaseValue[Any, Any]", value)


def _positional_arity(function: Callable[..., object]) -> int:
    """How many arguments `then` passes, matching the overload the checker picks.

    The checker tries `(event)` first, which also fits a function whose further parameters have
    defaults, so only a second required parameter receives the context.
    """
    parameters = inspect.signature(function).parameters.values()
    if any(parameter.kind is inspect.Parameter.VAR_POSITIONAL for parameter in parameters):
        raise TypeError("then() takes a function of (event) or (event, context), not of *args")
    positional = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    required = [p for p in parameters if p.kind in positional and p.default is inspect.Parameter.empty]
    total = [p for p in parameters if p.kind in positional]
    return 1 if len(required) <= 1 and total else len(required)


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

    def bind(self, context: OptionalContextT | Expr[OptionalContextT]) -> "GroupedMsg[MsgGroupT, OptionalEventT, None]":
        """Supply the context, giving a message that an event handler can dispatch as is.

        The context type of a `GroupedMsg` is what a dispatcher still has to provide, so a bound
        message has `None`; its case receives the value as the second argument of `then`.
        """
        return cast(
            "GroupedMsg[MsgGroupT, OptionalEventT, None]",
            GroupedMsg(self.group, self.name, context),
        )

    @overload
    def then(self, case: "CaseValue[ModelT, MsgGroupT]") -> tuple[Self, "CaseValue[ModelT, MsgGroupT]"]: ...
    @overload
    def then(
        self, case: "Callable[[OptionalEventT], CaseValue[ModelT, MsgGroupT]]"
    ) -> tuple[Self, "CaseValue[ModelT, MsgGroupT]"]: ...
    @overload
    def then(
        self, case: "Callable[[OptionalEventT, OptionalContextT], CaseValue[ModelT, MsgGroupT]]"
    ) -> tuple[Self, "CaseValue[ModelT, MsgGroupT]"]: ...
    def then(
        self,
        case: "CaseValue[ModelT, MsgGroupT] | Callable[..., CaseValue[ModelT, MsgGroupT]]",
    ) -> tuple[Self, "CaseValue[ModelT, MsgGroupT]"]:
        """Handle this message, with what to do or a function of its event and context.

        `then(lambda event: ...)` receives the event, and `then(lambda event, context: ...)` also
        the context given to `bind`. Each case sees only its own message, as in an Elm `case`.
        """
        from .update import is_case_value

        if is_case_value(case):
            return self, cast("CaseValue[ModelT, MsgGroupT]", case)
        if not callable(case) or isinstance(case, Expr):
            raise TypeError(
                f"{self.name}.then() takes State.set(...), (ModelUpdate, Cmd), Update.forward(...), or a function "
                f"of (event) or (event, context) returning one, not {type(case).__name__}"
            )
        arity = _positional_arity(case)
        if arity == 1:
            return self, _checked_case(self.name, case(_message_ref(MESSAGE_EVENT)))
        if arity == 2:
            return self, _checked_case(self.name, case(_message_ref(MESSAGE_EVENT), _message_ref(MESSAGE_CONTEXT)))
        raise TypeError(f"{self.name}.then() takes a function of (event) or (event, context), not {arity} arguments")

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
