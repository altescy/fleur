from __future__ import annotations

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
from fleur.js.builder import object_expr

from .cmd import Cmd
from .model import Model
from .runtime import COMPONENT_INIT, COMPONENT_SUBSCRIPTIONS, COMPONENT_UPDATE, COMPONENT_VIEW, MODEL_IDENT
from .sub import Sub
from .types import ModelT, MsgGroupT
from .update import Update
from .view import View


@dataclass(slots=True)
class _Init(Generic[ModelT, MsgGroupT]):
    model: ModelT
    cmd: Cmd[ModelT, MsgGroupT] = field(default_factory=Cmd.none)


class Component(Model, Generic[ModelT, MsgGroupT]):
    def __init__(
        self,
        init: ModelT | tuple[ModelT, Cmd[ModelT, MsgGroupT]],
        update: Update[ModelT, MsgGroupT],
        view: View[ModelT, MsgGroupT],
        subscriptions: Sub[ModelT, MsgGroupT] | None = None,
    ) -> None:
        """Start from a model, or from a model and a command to run first."""
        self.init: _Init[ModelT, MsgGroupT] = _Init(*init) if isinstance(init, tuple) else _Init(init)
        self.update: Update[ModelT, MsgGroupT] = update
        self.view: View[ModelT, MsgGroupT] = view
        self.subscriptions: Sub[ModelT, MsgGroupT] = subscriptions or Sub.none()

    def __compile__(self) -> ESTreeExpression:
        init_model, init_cmd = self.init.model, self.init.cmd

        update = self.update
        view = self.view
        subscriptions = getattr(self, COMPONENT_SUBSCRIPTIONS, Sub.none())

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
                (COMPONENT_UPDATE, update.__compile__()),
                (
                    COMPONENT_VIEW,
                    ESTreeFunctionExpression(
                        id=None,
                        params=[ESTreeIdentifier(name=MODEL_IDENT)],
                        body=ESTreeFunctionBody(
                            body=[ESTreeReturnStatement(argument=view.__compile__())],
                        ),
                    ),
                ),
                (
                    COMPONENT_SUBSCRIPTIONS,
                    ESTreeFunctionExpression(
                        id=None,
                        params=[ESTreeIdentifier(name=MODEL_IDENT)],
                        body=ESTreeFunctionBody(
                            body=[ESTreeReturnStatement(argument=subscriptions.__compile__())],
                        ),
                    ),
                ),
            ]
        )
