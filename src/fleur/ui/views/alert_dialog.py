from typing import Unpack

from fleur.core.events import DialogCloseEvent, SubmitEvent
from fleur.core.expr import Expr
from fleur.core.msg import GroupedMsg
from fleur.core.types import ModelT_co, MsgGroupT, OptionalContextT

from ._utils import extend_props
from .base import Element, ViewProps
from .button import Button
from .dialog import Dialog
from .form import Form
from .heading import Heading
from .hstack import HStack
from .types import String, ViewStyleArgs
from .vstack import VStack


class AlertDialog(Dialog[ModelT_co, MsgGroupT]):
    """A modal confirmation that focuses Cancel when it opens."""

    def __init__(
        self,
        *,
        id: String,
        title: String,
        description: String,
        open: bool | Expr[bool],
        onclose: GroupedMsg[MsgGroupT, DialogCloseEvent, OptionalContextT],
        onconfirm: GroupedMsg[MsgGroupT, SubmitEvent, OptionalContextT],
        cancel_label: String = "Cancel",
        confirm_label: String = "Confirm",
        props: ViewProps | None = None,
        **style_args: Unpack[ViewStyleArgs],
    ) -> None:
        title_id = id + "-title"
        description_id = id + "-description"
        super().__init__(
            VStack(
                Heading(title, level=2, props={"id": title_id}),
                Element(description, tag="p", props={"id": description_id}),
                HStack(
                    Form(
                        Button(cancel_label, variant="secondary", props={"type": "submit", "autofocus": True}),
                        props={"method": "dialog"},
                    ),
                    Form(
                        Button(confirm_label, props={"type": "submit"}),
                        onsubmit=onconfirm,
                        props={"method": "dialog"},
                    ),
                    gap="sm",
                    justify="flex-end",
                    flex_wrap="wrap",
                ),
                gap="md",
            ),
            open=open,
            onclose=onclose,
            props=extend_props(
                {} if props is None else props,
                {
                    "id": id,
                    "role": "alertdialog",
                    "aria-modal": "true",
                    "aria-labelledby": title_id,
                    "aria-describedby": description_id,
                },
            ),
            **style_args,
        )
