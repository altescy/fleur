from collections.abc import Callable

import pytest

from fleur import Array, Cond, Model, State
from fleur.core import DomAction, DomEffect, DomElement, DomLifecycle, DomScope, Expr
from fleur.core.model import model_ref
from fleur.js import emit
from fleur.js.ast import ESTreeGeneratedIdentifier
from fleur.js.builder import ident


class Settings(Model):
    caption: State[str]
    captions: State[list[str]]


settings = model_ref(Settings, ident("model"))


def _compile(setup: Callable[[DomElement, DomScope], DomLifecycle]) -> str:
    return emit(DomEffect.scoped("caption", setup).__compile__())


def test_scoped_input_accepts_render_time_expressions() -> None:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        caption = scope.input(settings.caption + "!")
        upper = scope.input(Array.map(settings.captions, lambda item: item + "?"))
        return DomLifecycle(mount=DomAction.batch(root.set_text(caption), root.set_text(upper[0])))

    assert "caption" in _compile(setup)


def test_scoped_input_rejects_another_input() -> None:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        caption = scope.input(settings.caption)
        decorated = scope.input(caption + "!")
        return DomLifecycle(mount=root.set_text(decorated))

    with pytest.raises(ValueError, match=r"DomScope.input\(\) #2 of effect 'caption' refers to a value created"):
        _compile(setup)


def test_scoped_input_rejects_scope_values_and_root() -> None:
    def with_value(root: DomElement, scope: DomScope) -> DomLifecycle:
        count = scope.value(0)
        return DomLifecycle(mount=root.set_text(scope.input(Expr[str](count.value.__compile__()))))

    def with_root(root: DomElement, scope: DomScope) -> DomLifecycle:
        return DomLifecycle(mount=root.set_text(scope.input(root.id)))

    for setup in (with_value, with_root):
        with pytest.raises(ValueError, match="refers to a value created inside the effect"):
            _compile(setup)


def test_scoped_setup_rejects_direct_model_reads() -> None:
    def in_update(root: DomElement, scope: DomScope) -> DomLifecycle:
        return DomLifecycle(update=root.set_text(settings.caption))

    def in_listener(root: DomElement, scope: DomScope) -> DomLifecycle:
        return DomLifecycle(mount=scope.listen(root, "refresh", lambda _: root.set_text(settings.caption)))

    for setup in (in_update, in_listener):
        with pytest.raises(ValueError, match="reads a render-time value"):
            _compile(setup)


def test_scoped_setup_rejects_bindings_from_the_enclosing_view() -> None:
    item = Expr[str](ESTreeGeneratedIdentifier())

    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        return DomLifecycle(mount=root.set_text(item))

    with pytest.raises(ValueError, match="reads a render-time value"):
        _compile(setup)


def test_scoped_setup_allows_its_own_bindings() -> None:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        caption = scope.input(settings.caption)
        last = scope.value("")
        return DomLifecycle(
            mount=DomAction.with_value(root.id, lambda current: last.set(current)),
            update=scope.listen(
                root, "refresh", lambda event: root.set_text(Cond.when(event.alt, caption, last.value))
            ),
        )

    # The only model read is the input argument, evaluated during rendering.
    assert _compile(setup).count("model.caption") == 1


def test_unscoped_effect_may_read_the_model_because_it_reruns_with_fresh_closures() -> None:
    effect = DomEffect("caption", lambda root: root.set_text(settings.caption), dependencies=[settings.caption])
    assert "model.caption" in emit(effect.__compile__())
