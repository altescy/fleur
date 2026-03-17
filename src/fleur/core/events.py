from typing import TypedDict


class PointerEvent(TypedDict):
    type: str
    pointer_id: int
    client_x: int | float
    client_y: int | float
    button: int
    alt: bool
    ctrl: bool
    shift: bool
    meta: bool


class KeyboardEvent(TypedDict):
    type: str
    key: str
    code: str
    repeat: bool
    alt: bool
    ctrl: bool
    shift: bool
    meta: bool


class InputEvent(TypedDict):
    type: str
    value: object
    checked: bool


class FocusEvent(TypedDict):
    type: str


class SubmitEvent(TypedDict):
    type: str
