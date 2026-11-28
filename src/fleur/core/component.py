from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeExpression,
    ESTreeFunctionBody,
    ESTreeFunctionExpression,
    ESTreeIdentifier,
    ESTreeReturnStatement,
)
from fleur.js.builder import ident, object_expr

from .cmd import Cmd
from .model import Model, model_ref
from .runtime import COMPONENT_INIT, COMPONENT_SUBSCRIPTIONS, COMPONENT_UPDATE, COMPONENT_VIEW, MODEL_IDENT
from .sub import Sub
from .types import ModelT, MsgGroupT
from .update import Update
from .view import View


@dataclass(slots=True)
class _Init(Generic[ModelT, MsgGroupT]):
    model: ModelT
    cmd: Cmd[ModelT, MsgGroupT] = field(default_factory=Cmd.none)


def _model_function(body: ESTreeExpression) -> ESTreeFunctionExpression:
    return ESTreeFunctionExpression(
        id=None,
        params=[ESTreeIdentifier(name=MODEL_IDENT)],
        body=ESTreeFunctionBody(body=[ESTreeReturnStatement(argument=body)]),
    )


class Component(Model, Generic[ModelT, MsgGroupT]):
    """A program part: a model to start from, and functions of the current model, as in Elm.

    `update`, `view` and `subscriptions` receive the model and read its values from it, as in
    `view=lambda model: Text(model.title)`. Fields named through the class, such as
    `Board.title`, are references for `State.set` and `forward`, not values.
    """

    def __init__(
        self,
        init: ModelT | tuple[ModelT, Cmd[ModelT, MsgGroupT]],
        update: Callable[[ModelT], Update[ModelT, MsgGroupT]],
        view: Callable[[ModelT], View[ModelT, MsgGroupT]],
        subscriptions: Callable[[ModelT], Sub[ModelT, MsgGroupT]] | None = None,
    ) -> None:
        """Start from a model, or from a model and a command to run first."""
        self.init: _Init[ModelT, MsgGroupT] = _Init(*init) if isinstance(init, tuple) else _Init(init)
        self.update: Callable[[ModelT], Update[ModelT, MsgGroupT]] = update
        self.view: Callable[[ModelT], View[ModelT, MsgGroupT]] = view
        self.subscriptions: Callable[[ModelT], Sub[ModelT, MsgGroupT]] | None = subscriptions

    @property
    def model_type(self) -> type[ModelT]:
        """The model type, taken from the initial model."""
        return type(self.init.model)

    def _model(self) -> ModelT:
        return model_ref(self.model_type, ident(MODEL_IDENT))

    def compile_update(self) -> ESTreeExpression:
        """The update as a JavaScript function of the model and the message."""
        return self.update(self._model()).__compile__()

    def __compile__(self) -> ESTreeExpression:
        init_model, init_cmd = self.init.model, self.init.cmd
        subscriptions = Sub.none() if self.subscriptions is None else self.subscriptions(self._model())

        init_fn = ESTreeFunctionExpression(
            id=None,
            params=[],
            body=ESTreeFunctionBody(
                body=[
                    ESTreeReturnStatement(
                        argument=ESTreeArrayExpression(
                            elements=[init_model.__compile__(), init_cmd.__compile__()],
                        ),
                    )
                ],
            ),
        )

        return object_expr(
            [
                (COMPONENT_INIT, init_fn),
                (COMPONENT_UPDATE, self.compile_update()),
                (COMPONENT_VIEW, _model_function(self.view(self._model()).__compile__())),
                (COMPONENT_SUBSCRIPTIONS, _model_function(subscriptions.__compile__())),
            ]
        )
