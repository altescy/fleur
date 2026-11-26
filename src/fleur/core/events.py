from typing import Literal, Protocol


class PointerEvent(Protocol):
    type: str
    pointer_id: int
    client_x: int | float
    client_y: int | float
    button: int
    alt: bool
    ctrl: bool
    shift: bool
    meta: bool


class KeyboardEvent(Protocol):
    type: str
    key: str
    code: str
    repeat: bool
    alt: bool
    ctrl: bool
    shift: bool
    meta: bool


class InputEvent(Protocol):
    type: str
    value: str
    checked: bool


class FocusEvent(Protocol):
    type: str


class SubmitEvent(Protocol):
    type: str


class DialogCloseEvent(Protocol):
    type: str


class ToggleEvent(Protocol):
    type: str
    open: bool


class ToastCloseEvent(Protocol):
    type: str
    reason: Literal["timeout", "dismiss"]
