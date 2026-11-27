from typing import Literal

from fleur.core import Boolean, Cond, DomAction, DomEffect, DomElement, Expr
from fleur.core.dom import DomElements, DomEvents, DomKeyboardEvent, DomLifecycle, DomScope

from ._dom_helpers import attribute_is, modified


def accordion_effect() -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        group = scope.unique_id("fleur-accordion-")
        selector = ':scope > details[data-fleur-part="accordion-item"]'
        items = root.query_all(selector)

        def on_key(event: DomKeyboardEvent) -> DomAction:
            down, up = Cond.equal(event.key, "ArrowDown"), Cond.equal(event.key, "ArrowUp")
            home, end = Cond.equal(event.key, "Home"), Cond.equal(event.key, "End")

            def navigate(summaries: DomElements) -> DomAction:
                index = summaries.index_of(event.target)
                offset = Cond.when(down, 1, -1)
                destination = Cond.when(
                    home, 0, Cond.when(end, -1, (index + offset + summaries.length) % summaries.length)
                )
                return DomAction.when(
                    index >= 0, DomAction.batch(event.prevent_default(), summaries.at(destination).focus())
                )

            return DomAction.when(
                Cond.every(Boolean.negate(modified(event)), Cond.some(up, down, home, end)),
                items.filter(lambda item: Boolean.negate(item.hidden))
                .map(lambda item: item.child(0))
                .with_snapshot(navigate),
            )

        return DomLifecycle(
            mount=scope.on(root, DomEvents.key_down, on_key),
            update=items.for_each(lambda item, _: item.set_attribute("name", group)),
        )

    return DomEffect.scoped("accordion", setup, watch_subtree=True, after_connect=False)


def avatar_effect() -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        fallback, image = root.child(0), root.child(1).as_image()

        def sync() -> DomAction:
            # currentSrc can retain the previous request while its replacement loads.
            loaded = Cond.every(
                image.has_attribute("src"),
                image.complete,
                image.natural_width > 0,
                Cond.equal(image.current_source, image.source),
            )
            return DomAction.with_value(
                loaded,
                lambda value: DomAction.batch(image.set_hidden(Boolean.negate(value)), fallback.set_hidden(value)),
            )

        synchronize = scope.action(sync())
        return DomLifecycle(
            mount=DomAction.batch(
                scope.listen(image, "load", lambda _: synchronize), scope.listen(image, "error", lambda _: synchronize)
            ),
            update=synchronize,
        )

    return DomEffect.scoped("avatar", setup, watch_subtree=True, after_connect=False)


def number_field_effect() -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        input_ = root.child(0).as_input()
        decrease, increase = root.child(1), root.child(2)
        unavailable = Cond.some(input_.has_attribute("readonly"), attribute_is(input_, "step", "any"))
        disabled = Cond.some(input_.has_attribute("disabled"), unavailable)

        def set_disabled(button: DomElement, value: Expr[bool]) -> DomAction:
            return DomAction.when(
                value, button.set_attribute("disabled", ""), otherwise=button.remove_attribute("disabled")
            )

        def sync() -> DomAction:
            def update_bounds(clone: DomElement) -> DomAction:
                probe = clone.as_input()

                def check_step(button: DomElement, direction: Literal[-1, 1]) -> DomAction:
                    return DomAction.batch(
                        probe.set_value(input_.value),
                        probe.step(direction),
                        button.set_attribute(
                            "aria-disabled", Cond.when(Cond.equal(input_.value, probe.value), "true", "false")
                        ),
                    )

                return DomAction.batch(check_step(decrease, -1), check_step(increase, 1))

            return DomAction.with_value(
                disabled,
                lambda blocked: DomAction.batch(
                    set_disabled(decrease, blocked),
                    set_disabled(increase, blocked),
                    # Let a detached input compute steps at off-step bounds.
                    DomAction.when(Boolean.negate(blocked), input_.clone().with_reference(update_bounds)),
                ),
            )

        def step(direction: Literal[-1, 1]) -> DomAction:
            return DomAction.when(
                Boolean.negate(Cond.some(input_.matches(":disabled"), unavailable)),
                DomAction.with_value(
                    input_.value,
                    lambda before: DomAction.batch(
                        input_.step(direction),
                        DomAction.when(
                            Cond.not_equal(input_.value, before),
                            DomAction.batch(
                                input_.dispatch("input", bubbles=True), input_.dispatch("change", bubbles=True)
                            ),
                        ),
                    ),
                ),
            )

        synchronize = scope.action(sync())
        return DomLifecycle(
            mount=DomAction.batch(
                scope.listen(decrease, "click", lambda _: step(-1)),
                scope.listen(increase, "click", lambda _: step(1)),
                scope.listen(input_, "input", lambda _: synchronize),
            ),
            update=synchronize,
        )

    return DomEffect.scoped("number-field", setup, watch_subtree=True, after_connect=False)
