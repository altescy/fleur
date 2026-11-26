from typing import Final, Literal, TypeAlias

from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, member_expr

# Runtime object namespace.
RuntimeNamespaceName: TypeAlias = Literal["__fleur"]

# Top-level runtime API members (__fleur.<member>).
RuntimeTopLevelName: TypeAlias = Literal[
    "h", "lazy", "Cmd", "Sub", "Html", "Http", "program", "mergeStyleProps", "sortBy"
]

# Nested runtime API members (__fleur.<object>.<member>).
RuntimeNestedName: TypeAlias = Literal["none", "map", "batch", "task", "interval", "request"]

# Any member reachable from runtime_ref/runtime_call.
RuntimeMemberName: TypeAlias = RuntimeTopLevelName | RuntimeNestedName

# Component object fields.
ComponentFieldName: TypeAlias = Literal["init", "update", "view", "subscriptions"]

# Message object fields.
MessageFieldName: TypeAlias = Literal["type", "event", "context"]

# Local identifier names used inside generated program code.
ModelIdentName: TypeAlias = Literal["model"]
MessageIdentName: TypeAlias = Literal["message"]

RUNTIME_NAMESPACE: Final[RuntimeNamespaceName] = "__fleur"

RUNTIME_H: Final[Literal["h"]] = "h"
RUNTIME_LAZY: Final[Literal["lazy"]] = "lazy"
RUNTIME_CMD: Final[Literal["Cmd"]] = "Cmd"
RUNTIME_SUB: Final[Literal["Sub"]] = "Sub"
RUNTIME_HTML: Final[Literal["Html"]] = "Html"
RUNTIME_HTTP: Final[Literal["Http"]] = "Http"
RUNTIME_PROGRAM: Final[Literal["program"]] = "program"

RUNTIME_NONE: Final[Literal["none"]] = "none"
RUNTIME_MAP: Final[Literal["map"]] = "map"
RUNTIME_BATCH: Final[Literal["batch"]] = "batch"
RUNTIME_TASK: Final[Literal["task"]] = "task"
RUNTIME_INTERVAL: Final[Literal["interval"]] = "interval"
RUNTIME_REQUEST: Final[Literal["request"]] = "request"

COMPONENT_INIT: Final[Literal["init"]] = "init"
COMPONENT_UPDATE: Final[Literal["update"]] = "update"
COMPONENT_VIEW: Final[Literal["view"]] = "view"
COMPONENT_SUBSCRIPTIONS: Final[Literal["subscriptions"]] = "subscriptions"

MESSAGE_TYPE: Final[Literal["type"]] = "type"
MESSAGE_EVENT: Final[Literal["event"]] = "event"
MESSAGE_CONTEXT: Final[Literal["context"]] = "context"

MODEL_IDENT: Final[ModelIdentName] = "model"
MESSAGE_IDENT: Final[MessageIdentName] = "message"


def runtime_root() -> ESTreeExpression:
    return ident(RUNTIME_NAMESPACE)


def runtime_ref(*path: RuntimeMemberName) -> ESTreeExpression:
    if not path:
        return runtime_root()

    expr: ESTreeExpression = runtime_root()
    for part in path:
        expr = member_expr(expr, part)
    return expr


def runtime_call(path: tuple[RuntimeMemberName, ...], *args: ESTreeExpression) -> ESTreeExpression:
    return call(runtime_ref(*path), *args)
