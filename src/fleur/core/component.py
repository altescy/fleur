from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic

from .cmd import Cmd
from .sub import Sub
from .types import ModelT, MsgGroupT
from .update import Update
from .view import View


@dataclass(slots=True)
class Init(Generic[ModelT, MsgGroupT]):
    model: ModelT
    cmd: Cmd[ModelT, MsgGroupT] = field(default_factory=Cmd.none)


class Component(Generic[ModelT, MsgGroupT]):
    init: Init[ModelT, MsgGroupT]
    update: Update[ModelT, MsgGroupT]
    view: View[ModelT, MsgGroupT]
    subscriptions: Sub[ModelT]

    def __init__(
        self,
        init: ModelT | tuple[ModelT, Cmd[ModelT, MsgGroupT]] | Init[ModelT, MsgGroupT],
        update: Update[ModelT, MsgGroupT],
        view: View[ModelT, MsgGroupT],
        subscriptions: Sub[ModelT] | None = None,
    ) -> None:
        if not isinstance(init, Init):
            init = Init(init) if not isinstance(init, tuple) else Init(*init)

        self.init = init
        self.update = update
        self.view = view
        self.subscriptions = subscriptions or Sub.none()
