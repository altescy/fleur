from typing import TYPE_CHECKING, Protocol

from .cmd import Cmd
from .sub import Sub
from .types import ModelT, MsgGroupT

if TYPE_CHECKING:
    from .cmd import Cmd
    from .sub import Sub
    from .update import Update
    from .view import View


class Component(Protocol[ModelT, MsgGroupT]):
    init: "ModelT | tuple[ModelT, Cmd[ModelT, MsgGroupT]]"
    update: "Update[ModelT, MsgGroupT]"
    view: "View[ModelT, MsgGroupT]"
    subscriptions: "Sub[ModelT]"
