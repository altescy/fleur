from typing import Final, Literal, TypeAlias

from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, member_expr

RuntimeNamespace: TypeAlias = Literal["__fleur"]

RuntimeHName: TypeAlias = Literal["h"]
RuntimeLazyName: TypeAlias = Literal["lazy"]
RuntimeCmdName: TypeAlias = Literal["Cmd"]
RuntimeSubName: TypeAlias = Literal["Sub"]
RuntimeHtmlName: TypeAlias = Literal["Html"]
RuntimeProgramName: TypeAlias = Literal["program"]
RuntimeFunctionName: TypeAlias = (
    RuntimeHName | RuntimeLazyName | RuntimeCmdName | RuntimeSubName | RuntimeHtmlName | RuntimeProgramName
)

RuntimeNoneName: TypeAlias = Literal["none"]
RuntimeMethodName: TypeAlias = RuntimeNoneName
RuntimeMemberName: TypeAlias = RuntimeFunctionName | RuntimeMethodName

ComponentInitName: TypeAlias = Literal["init"]
ComponentUpdateName: TypeAlias = Literal["update"]
ComponentViewName: TypeAlias = Literal["view"]
ComponentSubscriptionsName: TypeAlias = Literal["subscriptions"]
ComponentFieldName: TypeAlias = ComponentInitName | ComponentUpdateName | ComponentViewName | ComponentSubscriptionsName

MessageTypeName: TypeAlias = Literal["type"]
MessageFieldName: TypeAlias = MessageTypeName

ModelIdentName: TypeAlias = Literal["model"]
MessageIdentName: TypeAlias = Literal["message"]

RUNTIME_NAMESPACE: Final[RuntimeNamespace] = "__fleur"

RUNTIME_H: Final[RuntimeHName] = "h"
RUNTIME_LAZY: Final[RuntimeLazyName] = "lazy"
RUNTIME_CMD: Final[RuntimeCmdName] = "Cmd"
RUNTIME_SUB: Final[RuntimeSubName] = "Sub"
RUNTIME_HTML: Final[RuntimeHtmlName] = "Html"
RUNTIME_PROGRAM: Final[RuntimeProgramName] = "program"

RUNTIME_NONE: Final[RuntimeNoneName] = "none"

COMPONENT_INIT: Final[ComponentInitName] = "init"
COMPONENT_UPDATE: Final[ComponentUpdateName] = "update"
COMPONENT_VIEW: Final[ComponentViewName] = "view"
COMPONENT_SUBSCRIPTIONS: Final[ComponentSubscriptionsName] = "subscriptions"

MESSAGE_TYPE: Final[MessageTypeName] = "type"

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
