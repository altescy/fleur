from typing import TYPE_CHECKING, Any

from typing_extensions import TypeVar

if TYPE_CHECKING:
    from .model import Model
    from .msg import MsgGroup

ValueT = TypeVar("ValueT", bound=object)
ValueT_contra = TypeVar("ValueT_contra", bound=object, contravariant=True)
StateValueT = TypeVar("StateValueT", bound=object)
StateValueT_contra = TypeVar("StateValueT_contra", bound=object, contravariant=True)

ModelT = TypeVar("ModelT", bound="Model")
ModelT_co = TypeVar("ModelT_co", bound="Model", covariant=True)
MsgGroupT = TypeVar("MsgGroupT", bound="MsgGroup")
MsgGroupT_co = TypeVar("MsgGroupT_co", bound="MsgGroup", covariant=True)
OptionalEventT = TypeVar("OptionalEventT", default=Any, covariant=True)
