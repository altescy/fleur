from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Type, TypeAlias, TypeVar, cast, get_origin, overload

from typing_extensions import dataclass_transform

from fleur.js.ast import ESTreeBinaryExpression, ESTreeExpression
from fleur.js.builder import call, ident, json_expr, member, object_expr
from fleur.types import ICompilable, JsonValue

from .runtime import MODEL_IDENT

if TYPE_CHECKING:
    from fleur.js.ast import ESTreeExpression

ValueT = TypeVar("ValueT", bound=object)
ValueT_contra = TypeVar("ValueT_contra", bound=object, contravariant=True)

StateValueT = TypeVar("StateValueT", bound=object)
StateValueT_contra = TypeVar("StateValueT_contra", bound=object, contravariant=True)

ModelT = TypeVar("ModelT", bound="Model")
ModelT_co = TypeVar("ModelT_co", bound="Model", covariant=True)


@dataclass_transform(kw_only_default=True)
class ModelMeta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        annotations = namespace.get("__annotations__", {})
        state_fields: list[str] = []

        for field_name, annotation in annotations.items():
            origin = get_origin(annotation)
            annotation_name = getattr(annotation, "__name__", "")
            origin_name = getattr(origin, "__name__", "")
            if "State" in (annotation_name, origin_name):
                state_fields.append(field_name)
                if not isinstance(namespace.get(field_name), object) or not hasattr(
                    namespace.get(field_name), "__set_name__"
                ):
                    namespace[field_name] = State()

        cls = super().__new__(mcls, name, bases, namespace)
        inherited: list[str] = []
        for base in bases:
            inherited.extend(getattr(base, "__state_fields__", ()))
        setattr(cls, "__state_fields__", tuple(dict.fromkeys([*inherited, *state_fields])))
        return cls


class Model(metaclass=ModelMeta):
    __state_fields__: tuple[str, ...] = ()

    def __init__(self, **kwargs: Any) -> None:
        unknown = sorted(set(kwargs) - set(self.__state_fields__))
        if unknown:
            names = ", ".join(unknown)
            raise TypeError(f"Unknown model fields: {names}")

        missing = [name for name in self.__state_fields__ if name not in kwargs]
        if missing:
            names = ", ".join(missing)
            raise TypeError(f"Missing model fields: {names}")

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __compile__(self) -> ESTreeExpression:
        return object_expr((name, _compile_operand(getattr(self, name))) for name in self.__state_fields__)


class State(Generic[StateValueT]):
    def __init__(self) -> None:
        self._name: str | None = None

    def __set_name__(self, owner: type[Model], name: str) -> None:
        self._name = name

    @overload
    def __get__(self, instance: None, owner: Type[ModelT]) -> "ModelState[ModelT, StateValueT]": ...

    @overload
    def __get__(self, instance: ModelT, owner: Type[ModelT]) -> StateValueT: ...

    def __get__(self, instance: ModelT | None, owner: Type[ModelT]) -> StateValueT | "ModelState[ModelT, StateValueT]":
        if self._name is None:
            raise AttributeError("State descriptor is not initialized")
        if instance is None:
            return ModelState(owner, self._name)
        values = cast(dict[str, StateValueT], instance.__dict__)
        return values[self._name]

    def __set__(self, instance: Model, value: StateValueT) -> None:
        if self._name is None:
            raise AttributeError("State descriptor is not initialized")
        values = cast(dict[str, StateValueT], instance.__dict__)
        values[self._name] = value


OperandValue: TypeAlias = Any


def _compile_operand(operand: OperandValue) -> ESTreeExpression:
    if isinstance(operand, ESTreeExpression):
        return operand
    if isinstance(operand, ICompilable):
        return operand.__compile__()
    return json_expr(operand)


class ModelOperation(Generic[ModelT_co]):
    def __init__(self, field_name: str, operator: str, operand: OperandValue) -> None:
        self.field_name = field_name
        self.operator = operator
        self.operand = operand

    def __compile__(self) -> ESTreeExpression:
        left = member(MODEL_IDENT, self.field_name)
        right = _compile_operand(self.operand)

        value_expr: ESTreeExpression
        if self.operator == "+":
            value_expr = ESTreeBinaryExpression(operator="+", left=left, right=right)
        elif self.operator == "-":
            value_expr = ESTreeBinaryExpression(operator="-", left=left, right=right)
        elif self.operator == "=":
            value_expr = right
        else:
            raise ValueError(f"Unsupported model operation: {self.operator}")

        return call(
            member("Object", "assign"),
            json_expr({}),
            ident(MODEL_IDENT),
            object_expr([(self.field_name, value_expr)]),
        )


class ModelState(Generic[ModelT, StateValueT_contra]):
    def __init__(self, model_type: type[ModelT], field_name: str) -> None:
        self.model_type = model_type
        self.field_name = field_name

    def __set__(self, instance: ModelT, value: StateValueT_contra) -> None:
        setattr(instance, self.field_name, value)

    def __add__(self, other: StateValueT_contra) -> ModelOperation[ModelT]:
        return ModelOperation(self.field_name, "+", cast(JsonValue, other))

    def __sub__(self, other: StateValueT_contra) -> ModelOperation[ModelT]:
        return ModelOperation(self.field_name, "-", cast(JsonValue, other))

    def set(self, value: OperandValue) -> ModelOperation[ModelT]:
        return ModelOperation(self.field_name, "=", value)

    def __str__(self) -> str:
        return f"{MODEL_IDENT}.{self.field_name}"

    def __format__(self, format_spec: str) -> str:
        if format_spec:
            raise ValueError("ModelState does not support format specifications")
        return "${" + str(self) + "}"
