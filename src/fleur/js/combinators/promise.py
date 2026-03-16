from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, cast

from typing_extensions import TypeVar

from fleur.js.ast import ESTreeExpression, ESTreeFunctionBody, ESTreeFunctionExpression, ESTreeReturnStatement
from fleur.js.builder import call, ident, member_expr
from fleur.types import ICompilable

PromiseValueT = TypeVar("PromiseValueT", default=object, covariant=True)
PromiseErrorT = TypeVar("PromiseErrorT", default=object, covariant=True)
PromiseNextT = TypeVar("PromiseNextT", default=object, covariant=True)
PromiseRefT = TypeVar("PromiseRefT", bound=ICompilable[ESTreeExpression], default=ICompilable[ESTreeExpression])


@dataclass(frozen=True, slots=True)
class TaskValueRef(Generic[PromiseValueT], ICompilable[ESTreeExpression]):
    expr: ESTreeExpression

    def __compile__(self) -> ESTreeExpression:
        return self.expr


@dataclass(frozen=True, slots=True)
class Promise(Generic[PromiseValueT, PromiseErrorT, PromiseRefT], ICompilable[ESTreeExpression]):
    promise: ESTreeExpression
    value_ref_factory: Callable[[ESTreeExpression], PromiseRefT] = field(repr=False)

    def __compile__(self) -> ESTreeExpression:
        return self.promise

    def then(
        self, mapper: Callable[[PromiseRefT], ICompilable[ESTreeExpression]]
    ) -> Promise[PromiseNextT, PromiseErrorT, TaskValueRef[PromiseNextT]]:
        param = ident("value")
        mapped = mapper(self.value_ref_factory(param))

        then_mapper = ESTreeFunctionExpression(
            id=None,
            params=[param],
            body=ESTreeFunctionBody(
                body=[
                    ESTreeReturnStatement(
                        argument=mapped.__compile__(),
                    )
                ]
            ),
        )

        return Promise[PromiseNextT, PromiseErrorT, TaskValueRef[PromiseNextT]](
            call(member_expr(self.promise, "then"), then_mapper),
            value_ref_factory=cast(Callable[[ESTreeExpression], TaskValueRef[PromiseNextT]], TaskValueRef),
        )
