from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

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
from .component import Component, Init
from .runtime import COMPONENT_INIT, COMPONENT_SUBSCRIPTIONS, COMPONENT_UPDATE, COMPONENT_VIEW, MODEL_IDENT
from .sub import Sub

if TYPE_CHECKING:
    from .cmd import Cmd
    from .sub import Sub


ComponentInput = Component[Any, Any] | type[Any] | Callable[[], Component[Any, Any]]


def _resolve_component(component: ComponentInput) -> Component[Any, Any] | type[Any]:
    if isinstance(component, Component):
        return component

    if callable(component) and not hasattr(component, COMPONENT_UPDATE):
        resolved = component()
        if isinstance(resolved, Component):
            return resolved
        raise TypeError("Component factory must return Component")

    return cast(type[Any], component)


def compile_component(component: ComponentInput) -> ESTreeExpression:
    c = cast(Any, _resolve_component(component))
    init = c.init
    if isinstance(init, Init):
        init_model, init_cmd = init.model, init.cmd
    elif isinstance(init, tuple):
        init_model, init_cmd = init
    else:
        init_model, init_cmd = init, Cmd.none()

    update = c.update
    view = c.view
    subscriptions = getattr(c, COMPONENT_SUBSCRIPTIONS, Sub.none())

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
                    params=cast(Any, [ESTreeIdentifier(name=MODEL_IDENT)]),
                    body=ESTreeFunctionBody(
                        body=[ESTreeReturnStatement(argument=view.__compile__())],
                    ),
                ),
            ),
            (
                COMPONENT_SUBSCRIPTIONS,
                ESTreeFunctionExpression(
                    id=None,
                    params=cast(Any, [ESTreeIdentifier(name=MODEL_IDENT)]),
                    body=ESTreeFunctionBody(
                        body=[ESTreeReturnStatement(argument=subscriptions.__compile__())],
                    ),
                ),
            ),
        ]
    )
