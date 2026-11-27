from typing import Unpack

from fleur.core.boolean import Boolean
from fleur.core.cond import Cond
from fleur.core.events import PointerEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT
from fleur.core.view import ViewProp

from ._utils import extend_props
from .base import ViewChild, ViewProps
from .button import Button
from .types import ViewStyleArgs


class Toggle(Button[ModelT_co, MsgGroupT]):
    """A two-state button whose change message carries the next pressed state."""

    def __init__(
        self,
        *children: ViewChild[ModelT_co, MsgGroupT],
        pressed: bool | Expr[bool],
        onchange: GroupedMsg[MsgGroupT, PointerEvent, bool],
        disabled: bool | Expr[bool] | None = None,
        props: ViewProps[MsgGroupT] | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        attrs: dict[str, ViewProp[MsgGroupT]] = {
            "type": "button",
            "aria-pressed": Cond.when(pressed, "true", "false"),
            "data-fleur-part": "toggle",
        }
        if disabled is not None:
            attrs["disabled"] = disabled
        super().__init__(
            *children,
            variant="secondary",
            onclick=onchange.bind(Boolean.negate(pressed)),
            props=extend_props({} if props is None else props, attrs),
            **style_args,
        )
