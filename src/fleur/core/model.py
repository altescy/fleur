from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import Any, Generic, Type, TypeVar, cast, get_origin, overload

from typing_extensions import Format, dataclass_transform

from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, json_expr, member, member_expr, object_expr

from .expr import Expr, ValueRef, ensure_expr
from .runtime import MODEL_IDENT
from .types import FleurValue, FleurValueT, FleurValueU, ModelT, ModelT_co

ModelU = TypeVar("ModelU", bound="Model")


def _model_annotations(namespace: dict[str, Any]) -> dict[str, object]:
    annotations = namespace.get("__annotations__")
    if annotations is not None:
        return annotations
    if sys.version_info >= (3, 14):
        from annotationlib import call_annotate_function, get_annotate_from_class_namespace

        annotate = get_annotate_from_class_namespace(namespace)
        if annotate is not None:
            return call_annotate_function(annotate, Format.FORWARDREF)
    return {}


@dataclass_transform(kw_only_default=True)
class ModelMeta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        state_fields: list[str] = []

        for field_name, annotation in _model_annotations(namespace).items():
            origin = get_origin(annotation)
            annotation_name = getattr(annotation, "__name__", "")
            origin_name = getattr(origin, "__name__", "")
            if "State" not in (annotation_name, origin_name):
                continue

            state_fields.append(field_name)
            if not hasattr(namespace.get(field_name), "__set_name__"):
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
    """Declare a field of a model.

    Read through the class, `Board.count` is a `Field`: a reference saying which field, for
    `State.set` and `forward`. It is not a value; a view or an update reads values from the model
    it receives, as `model.count`.
    """

    def __init__(self) -> None:
        self._name: str | None = None

    def __set_name__(self, owner: type[Model], name: str) -> None:
        self._name = name

    @overload
    def __get__(self, instance: None, owner: Type[ModelT]) -> "Field[ModelT, FleurValueT]": ...

    @overload
    def __get__(self: "State[ModelU]", instance: ModelT, owner: Type[ModelT]) -> ModelU: ...

    @overload
    def __get__(self, instance: ModelT, owner: Type[ModelT]) -> Expr[FleurValueT]: ...

    def __get__(
        self, instance: ModelT | None, owner: Type[ModelT]
    ) -> "Field[ModelT, FleurValueT] | Expr[FleurValueT] | Model":
        if self._name is None:
            raise AttributeError("State descriptor is not initialized")
        if instance is None:
            return Field[ModelT, FleurValueT](owner, (self._name,))

        values = cast(dict[str, Expr[FleurValueT]], instance.__dict__)
        try:
            return values[self._name]
        except KeyError as exc:
            raise AttributeError(f"State '{self._name}' is not initialized") from exc

    def __set__(self, instance: Model, value: FleurValueT | Expr[FleurValueT]) -> None:
        if self._name is None:
            raise AttributeError("State descriptor is not initialized")
        values = cast(dict[str, Expr[FleurValueT]], instance.__dict__)
        values[self._name] = value if isinstance(value, Expr) else Expr(ensure_expr(value))

    @staticmethod
    def unchanged() -> "ModelUpdate[Any]":
        """Keep the model as it is, for a message that needs no state change."""
        return ModelUpdate()

    @staticmethod
    def set(field: "Field[ModelT, FleurValueU]", value: FleurValueU | Expr[FleurValueU]) -> "ModelUpdate[ModelT]":
        """Set a field, or a field of a nested model such as `Board.todo[Todo.title]`."""
        name, *nested_path = field.path
        if not nested_path:
            return ModelUpdate((name, value))

        next_value = _assign_path(member(MODEL_IDENT, name), nested_path, ensure_expr(value))
        return ModelUpdate((name, Expr(next_value)))


class ModelUpdate(Generic[ModelT_co]):
    def __init__(self, *updates: tuple[str, FleurValue | Expr[FleurValue]]) -> None:
        self.updates = updates

    def __and__(self, other: "ModelUpdate[ModelT_co]") -> "ModelUpdate[ModelT_co]":
        return ModelUpdate(*self.updates, *other.updates)

    def __compile__(self) -> ESTreeExpression:
        return call(
            member("Object", "assign"),
            json_expr({}),
            ident(MODEL_IDENT),
            object_expr([(field_name, ensure_expr(value)) for field_name, value in self.updates]),
        )


class Field(Generic[ModelT_co, FleurValueT]):
    """A reference to a field of a model, such as `Board.count`, naming what to set or forward.

    It is not an expression, so it cannot be read as a value. Invariant in the value type, as a
    write target: a field of `int` does not accept the `str` that a wider type would allow.
    """

    def __init__(self, model_type: type[ModelT_co], path: tuple[str, ...]) -> None:
        self._model_type = model_type
        self._path = path

    @property
    def path(self) -> tuple[str, ...]:
        """The field names from the model to the referenced field."""
        return self._path

    def __getitem__(
        self: "Field[ModelT_co, ModelU]", key: "Field[ModelU, FleurValueU]"
    ) -> "Field[ModelT_co, FleurValueU]":
        """Refer to a field of the nested model held here, as in `Board.todo[Todo.title]`."""
        return Field(self._model_type, self._path + key.path)

    def __repr__(self) -> str:
        return f"Field({self._model_type.__name__}.{'.'.join(self._path)})"


def top_level_name(field: Field[Any, Any]) -> str:
    """The name of a field of the model itself, where a forwarded child's model is stored."""
    if len(field.path) != 1:
        raise ValueError(f"forward() takes a field of the model itself, not the nested {field!r}")
    return field.path[0]


def model_ref(model_type: type[ModelT], expr: ESTreeExpression) -> ModelT:
    """The value of a `model_type` model at `expr`, whose fields read as attributes, as in `model.count`.

    Seen by the checker as an instance of the model, and at runtime a `ValueRef`; the model type
    is taken so that the reference can later check field names.
    """
    del model_type
    return cast(ModelT, ValueRef(expr))


def _assign_path(base: ESTreeExpression, path: Sequence[str], value: ESTreeExpression) -> ESTreeExpression:
    if not path:
        return value
    key, *rest = path
    nested = _assign_path(member_expr(base, key), rest, value)
    return call(member("Object", "assign"), json_expr({}), base, object_expr([(key, nested)]))
