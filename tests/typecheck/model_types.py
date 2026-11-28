# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check that a component's initial model, update and view agree on one model type."""

from fleur import Component, Model, Msg, MsgGroup, State, Update, View
from fleur.core import PointerEvent
from fleur.ui import Button, Text


class Counter(Model):
    count: State[int]


class Profile(Model):
    name: State[str]


class Actions(MsgGroup):
    INC: Msg[PointerEvent] = Msg()


def counter_update(model: Counter) -> Update[Counter, Actions]:
    return Actions.cases(Actions.INC.then(State.set(Counter.count, model.count + 1)))


def profile_update(model: Profile) -> Update[Profile, Actions]:
    return Actions.cases(Actions.INC.then(State.set(Profile.name, "x")))


def counter_view(model: Counter) -> View[Counter, Actions]:
    return Button("+", onclick=Actions.INC)


def examples() -> None:
    Component(Counter(count=0), counter_update, counter_view)
    Component(Counter(count=0), counter_update, lambda model: Text("leaf views fit any model"))
    Component(init=Counter(count=0), update=counter_update, view=counter_view)
    Component(Profile(name=""), counter_update, lambda model: Text("x"))  # pyright: ignore[reportArgumentType]
    Component(Profile(name=""), profile_update, counter_view)  # pyright: ignore[reportArgumentType]


def inferred_types() -> None:
    """A component's model and message group come from its initial model and its update."""
    counter_app: Component[Counter, Actions] = Component(Counter(count=0), counter_update, counter_view)
    keyword_app: Component[Counter, Actions] = Component(
        init=Counter(count=0), update=counter_update, view=lambda model: Button("+", onclick=Actions.INC)
    )
    wrong_app: Component[Profile, Actions] = Component(Counter(count=0), counter_update, counter_view)  # pyright: ignore[reportAssignmentType]
    print(counter_app, keyword_app, wrong_app)


def foreign_update(model: Counter) -> Update[Counter, Actions]:
    """A case may only set fields of the model its update reads."""
    return Actions.cases(Actions.INC.then(State.set(Profile.name, "x")))  # pyright: ignore[reportReturnType]


def field_is_not_a_value() -> None:
    """A field names where to write; a value is read from the model that a view or update receives."""
    Text(Counter.count)  # pyright: ignore[reportArgumentType]
    _ = Counter.count + 1  # pyright: ignore[reportOperatorIssue]


def missing_model_attribute(model: Counter) -> View[Counter, Actions]:
    """Only declared fields can be read from the model."""
    return Text(model.missing)  # pyright: ignore[reportAttributeAccessIssue]
