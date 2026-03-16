from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, cast

from fleur.core.task import TaskExpr, TaskLike, TaskValueT
from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, literal, member_expr
from fleur.js.combinators import Promise, TaskValueRef
from fleur.types import JsonValue


class HttpError:
    pass


@dataclass(frozen=True, slots=True)
class _HttpTask(Generic[TaskValueT], TaskLike[TaskValueT, HttpError]):
    expr: ESTreeExpression

    def __compile__(self) -> ESTreeExpression:
        return self.expr


@dataclass(frozen=True, slots=True)
class _FetchResponse(TaskExpr[object]):
    expr: ESTreeExpression

    def __compile__(self) -> ESTreeExpression:
        return self.expr

    def json(self) -> TaskValueRef[JsonValue]:
        return TaskValueRef(call(member_expr(self.expr, "json")))


@dataclass(frozen=True, slots=True)
class _Expect(Generic[TaskValueT]):
    _mapper: Callable[[_FetchResponse], TaskExpr[TaskValueT]] = field(repr=False)

    def map(self, response: _FetchResponse) -> TaskExpr[TaskValueT]:
        return self._mapper(response)


class Http:
    @staticmethod
    def expectJson() -> _Expect[JsonValue]:
        return _Expect(lambda response: response.json())

    @staticmethod
    def get(url: str, *, expect: _Expect[TaskValueT]) -> TaskLike[TaskValueT, HttpError]:
        compiled = (
            Promise[_FetchResponse, HttpError, _FetchResponse](
                call(ident("fetch"), literal(url)),
                value_ref_factory=_FetchResponse,
            )
            .then(expect.map)
            .__compile__()
        )
        return cast(TaskLike[TaskValueT, HttpError], _HttpTask(compiled))
