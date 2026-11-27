from fleur.core import Boolean, Cond, DomAction, DomEffect, DomElement, Expr, Number, String
from fleur.core.dom import DomElements, DomEvents, DomKeyboardEvent, DomLifecycle, DomScope

from ._dom_helpers import modified, set_expanded, supports_anchor

_DISMISS = "fleur:dismiss-hover-panel"
_VISIBLE_PANELS = ':is([data-fleur-part="tooltip-panel"], [data-fleur-part="preview-card-panel"]):not([hidden])'
_OPTION = '[role="option"]'


def hover_panel_effect(*, preview: bool) -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        panel = root.last_child.as_popover()
        hovered, focused = scope.value(False), scope.value(False)
        timer = scope.timer()

        escape = scope.on_document(
            root,
            DomEvents.key_down,
            lambda event: DomAction.when(
                Cond.every(
                    Cond.equal(event.key, "Escape"),
                    Boolean.negate(event.default_prevented),
                    Boolean.negate(panel.hidden),
                ),
                DomAction.batch(
                    event.prevent_default(),
                    root.document_query_all(_VISIBLE_PANELS).for_each(lambda other, _: other.dispatch(_DISMISS)),
                ),
            ),
        )

        def show(visible: Expr[bool]) -> DomAction:
            return DomAction.when(
                Cond.every(panel.connected, Cond.equal(panel.hidden, visible)),
                DomAction.batch(
                    panel.set_hidden(Boolean.negate(visible)),
                    DomAction.when(Cond.equal(panel.mode, "manual"), panel.toggle(visible)),
                    DomAction.when(visible, escape.attach(), otherwise=escape.detach()),
                ),
            )

        def update(delay: int = 0) -> DomAction:
            def change(visible: Expr[bool]) -> DomAction:
                if not delay:
                    return show(visible)
                return DomAction.when(
                    Cond.equal(panel.hidden, visible), timer.start(delay, show(visible)), otherwise=show(visible)
                )

            return DomAction.batch(
                timer.cancel(), DomAction.with_value(Cond.some(focused.value, hovered.value), change)
            )

        def dismiss() -> DomAction:
            return DomAction.batch(hovered.set(False), focused.set(False), update())

        listeners = [
            scope.listen(panel, _DISMISS, lambda _: dismiss()),
            scope.on(
                root,
                DomEvents.pointer_enter,
                lambda event: DomAction.when(
                    Cond.not_equal(event.pointer_type, "touch"), DomAction.batch(hovered.set(True), update(350))
                ),
            ),
            scope.on(
                root,
                DomEvents.pointer_leave,
                lambda event: DomAction.when(
                    Cond.not_equal(event.pointer_type, "touch"), DomAction.batch(hovered.set(False), update(120))
                ),
            ),
            scope.listen(
                root,
                "focusin",
                lambda event: DomAction.when(
                    event.target.matches(":focus-visible"), DomAction.batch(focused.set(True), update())
                ),
            ),
            scope.listen(
                root,
                "focusout",
                lambda event: DomAction.when(
                    Boolean.negate(root.contains(event.related_target)), DomAction.batch(focused.set(False), update())
                ),
            ),
        ]
        if preview:
            listeners.append(
                scope.listen(
                    root, "click", lambda event: DomAction.when(root.child(0).contains(event.target), dismiss())
                )
            )
        return DomLifecycle(
            mount=DomAction.batch(
                DomAction.when(supports_anchor(panel), panel.set_attribute("popover", "manual")), *listeners
            )
        )

    return DomEffect.scoped("preview-card" if preview else "tooltip", setup, after_connect=False)


def _search_text(value: Expr[str]) -> Expr[str]:
    return String.trim(String.lower(String.normalize(value, form="NFKC")))


def combobox_effect(value: str | Expr[str | None] | None) -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        selected = scope.input(value)
        field = root.child(1).as_input()
        popup = root.child(2).as_popover()
        options, empty = popup.child(0), popup.child(1)
        opened, composing, editing = scope.value(False), scope.value(False), scope.value(False)
        query = scope.value("")
        active = scope.reference()
        choices = options.query_all(_OPTION)
        matches = options.query_all(f"{_OPTION}:not([hidden])")
        disabled = field.has_attribute("disabled")

        def set_active(option: DomElement) -> DomAction:
            def select(element: DomElement) -> DomAction:
                return DomAction.batch(
                    DomAction.when(
                        Boolean.negate(active.element.same_as(element)),
                        active.element.remove_attribute("data-fleur-active"),
                    ),
                    active.set(element),
                    DomAction.when(
                        element.exists,
                        DomAction.batch(
                            element.set_attribute("data-fleur-active", ""),
                            field.set_attribute("aria-activedescendant", element.id),
                        ),
                        otherwise=field.remove_attribute("aria-activedescendant"),
                    ),
                )

            return option.with_reference(select)

        def sync() -> DomAction:
            def update_options(filter_text: Expr[str]) -> DomAction:
                def update_option(option: DomElement, index: Expr[int]) -> DomAction:
                    chosen = Cond.equal(option.attribute("data-fleur-value"), selected)
                    match = String.includes(_search_text(option.text), filter_text)
                    return DomAction.batch(
                        option.set_attribute("id", options.id + "-option-" + index),
                        option.set_attribute("aria-selected", Cond.when(chosen, "true", "false")),
                        option.set_hidden(Boolean.negate(match)),
                    )

                return choices.for_each(update_option)

            return DomAction.batch(
                DomAction.when(disabled, DomAction.batch(opened.set(False), editing.set(False))),
                DomAction.with_value(_search_text(Cond.when(editing.value, query.value, "")), update_options),
                DomAction.when(
                    Boolean.negate(editing.value),
                    field.set_value(
                        choices.find(lambda option: Cond.equal(option.attribute("data-fleur-value"), selected)).text
                    ),
                ),
                DomAction.when(
                    active.element.exists,
                    set_active(
                        DomElement.when(
                            Cond.every(opened.value, matches.index_of(active.element) >= 0),
                            active.element,
                            DomElement.missing(),
                        )
                    ),
                ),
                empty.set_hidden(matches.length > 0),
                DomAction.when(
                    Cond.equal(popup.hidden, opened.value),
                    DomAction.batch(
                        popup.set_hidden(Boolean.negate(opened.value)),
                        DomAction.when(Cond.equal(popup.mode, "manual"), popup.toggle(opened.value)),
                        set_expanded(field, opened.value),
                    ),
                ),
            )

        synchronize = scope.action(sync())
        close = scope.action(
            DomAction.batch(
                opened.set(False),
                composing.set(False),
                editing.set(False),
                set_active(DomElement.missing()),
                synchronize,
            )
        )

        def on_key(event: DomKeyboardEvent) -> DomAction:
            up, down = Cond.equal(event.key, "ArrowUp"), Cond.equal(event.key, "ArrowDown")

            def move(items: DomElements) -> DomAction:
                index = Cond.when(
                    active.element.exists, items.index_of(active.element), Cond.when(down, -1, items.length)
                )
                next_index = Number.clamp(index + Cond.when(down, 1, -1), 0, items.length - 1)
                return items.at(next_index).with_reference(
                    lambda option: DomAction.batch(set_active(option), option.scroll_into_view())
                )

            navigate = DomAction.batch(
                event.prevent_default(),
                DomAction.when(Boolean.negate(opened.value), DomAction.batch(opened.set(True), synchronize)),
                matches.with_snapshot(move),
            )
            return DomAction.when(
                Boolean.negate(
                    Cond.some(
                        event.default_prevented,
                        event.is_composing,
                        composing.value,
                        Cond.equal(event.key_code, 229),
                    )
                ),
                DomAction.when(
                    Cond.every(opened.value, Cond.equal(event.key, "Escape")),
                    DomAction.batch(event.prevent_default(), close),
                    otherwise=DomAction.when(
                        # Without an active option, Enter keeps its native meaning, such as submitting a form.
                        Cond.every(opened.value, active.element.exists, Cond.equal(event.key, "Enter")),
                        DomAction.batch(event.prevent_default(), active.element.click()),
                        otherwise=DomAction.when(
                            Cond.every(Boolean.negate(modified(event)), Cond.some(up, down)), navigate
                        ),
                    ),
                ),
            )

        return DomLifecycle(
            mount=DomAction.batch(
                DomAction.when(supports_anchor(popup), popup.set_attribute("popover", "manual")),
                scope.listen(
                    field,
                    "click",
                    lambda _: DomAction.when(
                        Boolean.negate(Cond.some(opened.value, disabled)),
                        DomAction.batch(opened.set(True), synchronize),
                    ),
                ),
                scope.listen(
                    field,
                    "input",
                    lambda _: DomAction.batch(
                        query.set(field.value),
                        editing.set(True),
                        opened.set(True),
                        set_active(DomElement.missing()),
                        synchronize,
                    ),
                    capture=True,
                ),
                scope.listen(field, "compositionstart", lambda _: composing.set(True)),
                scope.listen(field, "compositionend", lambda _: composing.set(False)),
                scope.listen(field, "blur", lambda _: close),
                scope.on(field, DomEvents.key_down, on_key),
                scope.on(
                    options,
                    DomEvents.mouse_down,
                    lambda event: DomAction.when(
                        Cond.every(Cond.equal(event.button, 0), event.target.closest(_OPTION).exists),
                        event.prevent_default(),
                    ),
                ),
                scope.listen(
                    options,
                    "click",
                    lambda event: DomAction.when(
                        event.target.closest(_OPTION).exists,
                        DomAction.batch(close, field.focus(prevent_scroll=True)),
                    ),
                    capture=True,
                ),
            ),
            update=synchronize,
        )

    return DomEffect.scoped("combobox", setup, watch_subtree=True, after_connect=False)
