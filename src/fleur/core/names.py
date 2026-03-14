from typing import Final, Literal, TypeAlias

RuntimeNamespace: TypeAlias = Literal["__fleur"]
RuntimeFunctionName: TypeAlias = Literal["h", "lazy", "Cmd", "Sub", "Html", "program"]
RuntimeMethodName: TypeAlias = Literal["none"]

ComponentFieldName: TypeAlias = Literal["init", "update", "view", "subscriptions"]
MessageFieldName: TypeAlias = Literal["type"]

MODEL_IDENT: Final[Literal["model"]] = "model"
MESSAGE_IDENT: Final[Literal["message"]] = "message"

RUNTIME_NAMESPACE: Final[RuntimeNamespace] = "__fleur"

RUNTIME_H: Final[Literal["h"]] = "h"
RUNTIME_LAZY: Final[Literal["lazy"]] = "lazy"
RUNTIME_CMD: Final[Literal["Cmd"]] = "Cmd"
RUNTIME_SUB: Final[Literal["Sub"]] = "Sub"
RUNTIME_HTML: Final[Literal["Html"]] = "Html"
RUNTIME_PROGRAM: Final[Literal["program"]] = "program"

RUNTIME_NONE: Final[Literal["none"]] = "none"

COMPONENT_INIT: Final[Literal["init"]] = "init"
COMPONENT_UPDATE: Final[Literal["update"]] = "update"
COMPONENT_VIEW: Final[Literal["view"]] = "view"
COMPONENT_SUBSCRIPTIONS: Final[Literal["subscriptions"]] = "subscriptions"

MESSAGE_TYPE: Final[Literal["type"]] = "type"
