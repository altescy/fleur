from typing import TYPE_CHECKING

from typing_extensions import TypeVar

if TYPE_CHECKING:
    from fleur.types import JsonValue

    from .model import Model
    from .msg import MsgGroup

ValueT = TypeVar("ValueT", bound="JsonValue")
ValueT_contra = TypeVar("ValueT_contra", bound="JsonValue", contravariant=True)
StateValueT = TypeVar("StateValueT", bound="JsonValue")
StateValueT_contra = TypeVar("StateValueT_contra", bound="JsonValue", contravariant=True)

ModelT = TypeVar("ModelT", bound="Model")
ModelT_co = TypeVar("ModelT_co", bound="Model", covariant=True)
MsgGroupT = TypeVar("MsgGroupT", bound="MsgGroup")
MsgGroupT_co = TypeVar("MsgGroupT_co", bound="MsgGroup", covariant=True)
OptionalEventT = TypeVar("OptionalEventT", default=None, covariant=True)
