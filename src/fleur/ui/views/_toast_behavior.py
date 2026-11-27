from fleur.core import Boolean, Cond, DomAction, DomEffect, DomElement, Expr, Number, String
from fleur.core.dom import DomEvents, DomLifecycle, DomScope, DomValue

_MAX_DELAY = 2_147_483_647


def toast_effect() -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        announcement, popup = root.child(0), root.child(1)
        message, dismiss = popup.child(0), popup.child(1)
        requested, hovered, focus_within = scope.value(False), scope.value(False), scope.value(False)
        last_message = scope.value("")
        last_duration: DomValue[str | None] = scope.value(None)
        remaining: DomValue[int | float] = scope.value(0)
        started_at: DomValue[int | float] = scope.value(0)
        timed = scope.value(False)
        previous_focus = scope.reference()
        timer = scope.timer()

        def pause_timer() -> DomAction:
            return DomAction.when(
                timer.pending,
                DomAction.batch(
                    timer.cancel(),
                    remaining.set(Number.clamp(remaining.value - (scope.now() - started_at.value), 0, _MAX_DELAY)),
                ),
            )

        pause = scope.action(pause_timer())

        def hide() -> DomAction:
            def conceal(restore_focus: Expr[bool]) -> DomAction:
                return DomAction.batch(
                    popup.set_hidden(True),
                    announcement.set_text(""),
                    DomAction.when(
                        Cond.every(restore_focus, previous_focus.element.connected),
                        previous_focus.element.focus(prevent_scroll=True),
                    ),
                    previous_focus.clear(),
                )

            return DomAction.batch(
                pause,
                timed.set(False),
                DomAction.when(
                    Boolean.negate(popup.hidden), DomAction.with_value(popup.contains(root.active_element), conceal)
                ),
            )

        conceal = scope.action(hide())

        def close(reason: str) -> DomAction:
            return DomAction.when(
                Cond.every(root.connected, Boolean.negate(popup.hidden)),
                DomAction.batch(conceal, root.dispatch("toastclose", detail=reason)),
            )

        def update_timer() -> DomAction:
            return DomAction.when(
                Cond.some(popup.hidden, hovered.value, focus_within.value),
                pause,
                otherwise=DomAction.when(
                    Cond.every(timed.value, Boolean.negate(timer.pending)),
                    DomAction.batch(started_at.set(scope.now()), timer.start(remaining.value, close("timeout"))),
                ),
            )

        update_delay = scope.action(update_timer())

        def show() -> DomAction:
            duration = root.attribute("data-fleur-toast-duration")
            milliseconds = Number.from_string(String.or_empty(duration))
            unchanged = Cond.every(
                requested.value, Cond.equal(last_message.value, message.text), Cond.equal(last_duration.value, duration)
            )
            return DomAction.when(
                Boolean.negate(unchanged),
                DomAction.batch(
                    requested.set(True),
                    last_message.set(message.text),
                    last_duration.set(duration),
                    DomAction.when(
                        popup.hidden,
                        DomAction.batch(
                            previous_focus.set(root.active_element),
                            popup.set_hidden(False),
                            hovered.set(popup.matches(":hover")),
                            focus_within.set(popup.contains(root.active_element)),
                        ),
                    ),
                    announcement.set_text(message.text),
                    pause,
                    timed.set(Cond.every(Cond.not_equal(duration, None), Number.is_finite(milliseconds))),
                    remaining.set(Number.clamp(milliseconds, 0, _MAX_DELAY)),
                    update_delay,
                ),
            )

        sync = scope.action(
            DomAction.when(
                root.connected,
                DomAction.when(
                    root.has_attribute("data-fleur-toast-open"),
                    show(),
                    otherwise=DomAction.batch(requested.set(False), conceal),
                ),
            )
        )
        return DomLifecycle(
            mount=DomAction.batch(
                scope.on(
                    popup,
                    DomEvents.pointer_enter,
                    lambda event: DomAction.when(
                        Cond.not_equal(event.pointer_type, "touch"), DomAction.batch(hovered.set(True), update_delay)
                    ),
                ),
                scope.on(
                    popup,
                    DomEvents.pointer_leave,
                    lambda event: DomAction.when(
                        Cond.not_equal(event.pointer_type, "touch"), DomAction.batch(hovered.set(False), update_delay)
                    ),
                ),
                scope.listen(popup, "focusin", lambda _: DomAction.batch(focus_within.set(True), update_delay)),
                scope.listen(
                    popup,
                    "focusout",
                    lambda event: DomAction.batch(focus_within.set(popup.contains(event.related_target)), update_delay),
                ),
                scope.listen(dismiss, "click", lambda _: close("dismiss")),
            ),
            update=DomAction.when(root.connected, sync, otherwise=DomAction.microtask(sync)),
        )

    return DomEffect.scoped("toast", setup, watch_subtree=True, after_connect=False)
