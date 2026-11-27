from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Union

from typing_extensions import TypeAlias, TypeVar

if TYPE_CHECKING:
    from fleur.types import JsonValue

    from .function import Function
    from .model import Model
    from .msg import MsgGroup


KeyT = TypeVar("KeyT", bound=str)
FleurValue: TypeAlias = Union[
    "JsonValue",
    "Function",
    "Model",
    list["FleurValue[KeyT]"],
    dict[KeyT, "FleurValue[KeyT]"],
    Sequence["FleurValue[KeyT]"],
    Mapping[KeyT, "FleurValue[KeyT]"],
]
FleurValueT = TypeVar("FleurValueT", bound=FleurValue)
FleurValueT_co = TypeVar("FleurValueT_co", bound=FleurValue, covariant=True)
FleurValueU = TypeVar("FleurValueU", bound=FleurValue)

ModelT = TypeVar("ModelT", bound="Model")
ModelT_co = TypeVar("ModelT_co", bound="Model", covariant=True)
MsgGroupT = TypeVar("MsgGroupT", bound="MsgGroup")
MsgGroupT_co = TypeVar("MsgGroupT_co", bound="MsgGroup", covariant=True)
# A message receives this payload and exposes it through its event property.
OptionalEventT = TypeVar("OptionalEventT", default=None)
OptionalContextT = TypeVar("OptionalContextT", bound=FleurValue, default=None)
