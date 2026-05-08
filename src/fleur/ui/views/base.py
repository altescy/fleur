from __future__ import annotations

from typing import Generic

from fleur.core.types import ModelT_co, MsgGroupT_co
from fleur.core.view import View, ViewChild, ViewProps


class Element(View[ModelT_co, MsgGroupT_co], Generic[ModelT_co, MsgGroupT_co]):
    def __init__(
        self,
        *children: ViewChild,
        tag: str,
        props: ViewProps,
    ) -> None:
        super().__init__(*children, tag=tag, props=props)
