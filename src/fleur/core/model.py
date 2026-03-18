from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Generic, Type, TypeVar, cast, get_origin, overload

from typing_extensions import dataclass_transform

from fleur.js.ast import ESTreeExpression, ESTreeMemberExpression
from fleur.js.builder import call, ident, json_expr, member, member_expr, object_expr

from .expr import Expr, ensure_expr
from .runtime import MODEL_IDENT
from .types import FleurValue, FleurValueT, FleurValueT_co, FleurValueU

ModelT = TypeVar("ModelT", bound="Model")
ModelT_co = TypeVar("ModelT_co", bound="Model", covariant=True)
ModelU = TypeVar("ModelU", bound="Model")
NestedModelT = TypeVar("NestedModelT", bound="Model")


@dataclass_transform(kw_only_default=True)
class ModelMeta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        annotations = namespace.get("__annotations__", {})
        state_fields: list[str] = []

        for field_name, annotation in annotations.items():
            origin = get_origin(annotation)
            annotation_name = getattr(annotation, "__name__", "")
            origin_name = getattr(origin, "__name__", "")
            if "State" not in (annotation_name, origin_name):
                continue

            state_fields.append(field_name)
            if not isinstance(namespace.get(field_name), object) or not hasattr(
                namespace.get(field_name), "__set_name__"
            ):
                namespace[field_name] = State()

        cls = super().__new__(mcls, name, bases, namespace)

        inherited_fields: list[str] = []
        for base in bases:
            inherited_fields.extend(getattr(base, "__state_fields__", ()))

        merged_fields = tuple(dict.fromkeys([*inherited_fields, *state_fields]))
        setattr(cls, "__state_fields__", merged_fields)
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
        return object_expr((name, ensure_expr(getattr(self, name))) for name in self.__state_fields__)


class State(Generic[FleurValueT]):
    def __init__(self) -> None:
        self._name: str | None = None

    def __set_name__(self, owner: type[Model], name: str) -> None:
        del owner
        self._name = name

    @overload
    def __get__(self, instance: None, owner: Type[ModelT]) -> "ModelState[ModelT, FleurValueT]": ...

    @overload
    def __get__(self, instance: ModelT, owner: Type[ModelT]) -> Expr[FleurValueT]: ...

    def __get__(
        self, instance: ModelT | None, owner: Type[ModelT]
    ) -> "ModelState[ModelT, FleurValueT] | Expr[FleurValueT]":
        if self._name is None:
            raise AttributeError("State descriptor is not initialized")
        if instance is None:
            return ModelState[ModelT, FleurValueT](owner, self._name)

        values = cast(dict[str, Expr[FleurValueT]], instance.__dict__)
        try:
            return values[self._name]
        except KeyError as exc:
            raise AttributeError(f"State '{self._name}' is not initialized") from exc

    def __set__(self, instance: Model, value: FleurValueT) -> None:
        if self._name is None:
            raise AttributeError("State descriptor is not initialized")
        values = cast(dict[str, Expr[FleurValueT]], instance.__dict__)
        values[self._name] = value if isinstance(value, Expr) else Expr(ensure_expr(value))

    @staticmethod
    def set(state: "ModelState[ModelT, FleurValueU]", value: FleurValueU | Expr[FleurValueU]) -> ModelUpdate[ModelT]:
        nested_path = state._path[1:]
        if not nested_path:
            return ModelUpdate(state._field_name, value)

        model_field_expr = member(MODEL_IDENT, state._field_name)
        next_value = _assign_path(model_field_expr, nested_path, ensure_expr(value))
        return ModelUpdate(state._field_name, Expr(next_value))


class ModelUpdate(Generic[ModelT_co]):
    def __init__(self, field_name: str, value: FleurValue | Expr) -> None:
        self.field_name = field_name
        self.value = value

    def __compile__(self) -> ESTreeExpression:
        return call(
            member("Object", "assign"),
            json_expr({}),
            ident(MODEL_IDENT),
            object_expr([(self.field_name, ensure_expr(self.value))]),
        )


class ModelState(Expr[FleurValueT_co], Generic[ModelT_co, FleurValueT_co]):
    def __init__(self, model_type: type[ModelT_co], field_name: str, *, path: tuple[str, ...] | None = None) -> None:
        self._model_type = model_type
        self._field_name = field_name
        self._path = path or (field_name,)

        expr: ESTreeExpression = ident(MODEL_IDENT)
        for part in self._path:
            expr = member_expr(expr, part)
        super().__init__(expr)

    def __str__(self) -> str:
        return f"{MODEL_IDENT}.{'.'.join(self._path)}"

    def __format__(self, format_spec: str) -> str:
        if format_spec:
            raise ValueError("ModelState does not support format specifications")
        return "${" + str(self) + "}"

    @overload
    def __getitem__(
        self: "ModelState[ModelT_co, Sequence[FleurValueT]]",
        key: "int | Expr[int]",
    ) -> "Expr[FleurValueT]": ...
    @overload
    def __getitem__(
        self: "ModelState[ModelT_co, Mapping[str, FleurValueT]]",
        key: "str | Expr[str]",
    ) -> "Expr[FleurValueT]": ...
    @overload
    def __getitem__(
        self: "ModelState[ModelT_co, ModelU]",
        key: "str | Expr[str] | ModelState[ModelU, FleurValueU]",
    ) -> "ModelState[ModelU, FleurValueU]": ...
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: "ModelState[ModelT_co, Sequence[FleurValueT] | Mapping[str, FleurValueT] | ModelU]",
        key: "int | str | Expr[int | str] | ModelState[ModelU, FleurValueU]",
    ) -> "Expr[FleurValueT]" | "ModelState[ModelU, FleurValueU]":
        if isinstance(key, ModelState):
            return ModelState(self._model_type, self._field_name, path=self._path + (key._field_name,))

        return Expr[FleurValueT](
            ESTreeMemberExpression(
                object=self.__compile__(),
                property=ensure_expr(key),
                computed=True,
            )
        )


def _assign_path(base: ESTreeExpression, path: Sequence[str], value: ESTreeExpression) -> ESTreeExpression:
    if not path:
        return value
    key, *rest = path
    nested = _assign_path(member_expr(base, key), rest, value)
    return call(member("Object", "assign"), json_expr({}), base, object_expr([(key, nested)]))
