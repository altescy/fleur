from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Union

from typing_extensions import TypeVar

if TYPE_CHECKING:
    from fleur.types import JsonValue

    from .model import Model
    from .msg import MsgGroup


FleurValue = Union[
    "JsonValue",
    "Model",
    list["FleurValue"],
    dict[str, "FleurValue"],
    Sequence["FleurValue"],
    Mapping[str, "FleurValue"],
]
FleurValueT = TypeVar("FleurValueT", bound=FleurValue)
FleurValueT_co = TypeVar("FleurValueT_co", bound=FleurValue, covariant=True)
FleurValueU = TypeVar("FleurValueU", bound=FleurValue)

ModelT = TypeVar("ModelT", bound="Model")
ModelT_co = TypeVar("ModelT_co", bound="Model", covariant=True)
MsgGroupT = TypeVar("MsgGroupT", bound="MsgGroup")
MsgGroupT_co = TypeVar("MsgGroupT_co", bound="MsgGroup", covariant=True)
OptionalEventT = TypeVar("OptionalEventT", default=None, covariant=True)
OptionalContextT = TypeVar("OptionalContextT", default=None)
