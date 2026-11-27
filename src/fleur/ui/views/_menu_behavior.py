from fleur.core import Boolean, Cond, DomAction, DomEffect, DomElement, DomEvent, Expr, Number, String
from fleur.core.dom import DomBounds, DomElements, DomEvents, DomKeyboardEvent, DomLifecycle, DomPointerEvent, DomScope

from ._dom_helpers import attribute_is, modified, set_expanded

_ITEM = 'button[role="menuitem"]'


def _items(panel: DomElement) -> DomElements:
    return panel.query_all(f":scope > {_ITEM}:not([hidden]):not(:disabled)")


def _move(event: DomEvent, items: DomElements) -> DomAction:
    def navigate(choices: DomElements) -> DomAction:
        index = choices.index_of(event.target)
        last = choices.length - 1
        down = Cond.equal(event.key, "ArrowDown")
        up = Cond.equal(event.key, "ArrowUp")
        home = Cond.equal(event.key, "Home")
        end = Cond.equal(event.key, "End")
        destination = Cond.when(
            down,
            Cond.when(index < last, index + 1, 0),
            Cond.when(up, Cond.when(index <= 0, -1, index - 1), Cond.when(home, 0, -1)),
        )
        return DomAction.when(
            Cond.some(down, up, home, end), DomAction.batch(event.prevent_default(), choices.at(destination).focus())
        )

    return items.with_snapshot(navigate)


def _position(root: DomElement, panel: DomElement, x: Expr[int | float], y: Expr[int | float]) -> DomAction:
    return panel.bounds.with_snapshot(
        lambda bounds: DomAction.batch(
            root.set_style(
                "--fleur-context-menu-x",
                String.from_number(Number.clamp(x, 8, root.viewport_width - bounds.width - 8)) + "px",
            ),
            root.set_style(
                "--fleur-context-menu-y",
                String.from_number(Number.clamp(y, 8, root.viewport_height - bounds.height - 8)) + "px",
            ),
        )
    )


def menu_effect(*, context: bool) -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        trigger = root.child(0)
        panel = root.child(1).as_popover()
        valid = Cond.every(trigger.exists, attribute_is(panel, "role", "menu"))
        origin = scope.reference()
        autofocus = scope.reference()
        open_at_last = scope.value(False)
        tab_close = scope.timer()

        def close() -> DomAction:
            target = DomElement.when(origin.element.connected, origin.element, trigger)
            return DomAction.batch(panel.hide(), target.focus(prevent_scroll=True))

        def open_context(event: DomEvent, *, pointer: DomPointerEvent | None = None) -> DomAction:
            focused = root.active_element

            def position(anchor: DomBounds) -> DomAction:
                if pointer is None:
                    return _position(root, panel, anchor.left, anchor.bottom)
                use_pointer = Cond.some(
                    Cond.equal(pointer.button, 2),
                    Cond.not_equal(pointer.client_x, 0),
                    Cond.not_equal(pointer.client_y, 0),
                )
                return _position(
                    root,
                    panel,
                    Cond.when(use_pointer, pointer.client_x, anchor.left),
                    Cond.when(use_pointer, pointer.client_y, anchor.bottom),
                )

            return DomAction.batch(
                event.prevent_default(),
                origin.set(DomElement.when(trigger.contains(focused), focused, trigger)),
                origin.element.bounds.with_snapshot(
                    lambda anchor: DomAction.batch(
                        DomAction.when(
                            panel.is_open,
                            _items(panel).at(0).or_else(panel).focus(prevent_scroll=True),
                            otherwise=DomAction.batch(origin.element.focus(prevent_scroll=True), panel.show()),
                        ),
                        position(anchor),
                    )
                ),
            )

        def before_toggle(event: DomEvent) -> DomAction:
            destination = _items(panel).at(Cond.when(open_at_last.value, -1, 0)).or_else(panel)
            set_autofocus = destination.with_reference(
                lambda item: DomAction.when(
                    Boolean.negate(item.has_attribute("autofocus")),
                    DomAction.batch(item.set_attribute("autofocus", ""), autofocus.set(item)),
                )
            )
            return DomAction.when(
                Cond.every(valid, event.target.same_as(panel), Cond.not_equal(event.new_state, None)),
                DomAction.batch(
                    tab_close.cancel(),
                    autofocus.element.remove_attribute("autofocus"),
                    autofocus.clear(),
                    DomAction.when(Cond.equal(event.new_state, "open"), set_autofocus),
                ),
            )

        def on_key(event: DomKeyboardEvent) -> DomAction:
            if context:
                shortcut = Cond.every(
                    trigger.contains(event.target),
                    Cond.some(
                        Cond.equal(event.key, "ContextMenu"),
                        Cond.every(Cond.equal(event.key, "F10"), event.shift),
                    ),
                )
                open_action = open_context(event)
            else:
                up = Cond.equal(event.key, "ArrowUp")
                shortcut = Cond.every(
                    event.target.same_as(trigger),
                    Boolean.negate(panel.is_open),
                    Cond.some(up, Cond.equal(event.key, "ArrowDown")),
                )
                open_action = DomAction.batch(
                    event.prevent_default(), open_at_last.set(up), trigger.click(), open_at_last.set(False)
                )

            def after_tab(element: DomElement) -> DomAction:
                popover = element.as_popover()
                return tab_close.start(
                    0, DomAction.when(Cond.every(popover.connected, popover.is_open), popover.hide())
                )

            while_open = DomAction.when(
                Cond.equal(event.key, "Tab"),
                panel.with_reference(after_tab),
                otherwise=DomAction.when(
                    Cond.equal(event.key, "Escape"),
                    DomAction.batch(event.prevent_default(), close()),
                    otherwise=_move(event, _items(panel)),
                ),
            )
            return DomAction.when(
                Cond.every(valid, Boolean.negate(modified(event, shift=False))),
                DomAction.when(shortcut, open_action, otherwise=DomAction.when(panel.is_open, while_open)),
            )

        def on_click(event: DomEvent) -> DomAction:
            item = event.target.closest(_ITEM)
            return DomAction.when(
                Cond.every(valid, item.parent.same_as(panel)),
                DomAction.when(
                    attribute_is(item, "aria-disabled", "true"),
                    DomAction.batch(event.prevent_default(), event.stop_propagation()),
                    otherwise=DomAction.when(panel.is_open, close()),
                ),
            )

        listeners = [
            scope.listen(root, "beforetoggle", before_toggle, capture=True),
            scope.listen(
                root,
                "toggle",
                lambda event: DomAction.when(
                    Cond.every(valid, event.target.same_as(panel)), set_expanded(trigger, panel.is_open)
                ),
                capture=True,
            ),
            scope.on(root, DomEvents.key_down, on_key),
            scope.on(root, DomEvents.click, on_click, capture=True),
        ]
        if context:
            listeners.append(
                scope.on(
                    root,
                    DomEvents.context_menu,
                    lambda event: DomAction.when(
                        Cond.every(valid, Boolean.negate(event.default_prevented), trigger.contains(event.target)),
                        open_context(event, pointer=event),
                    ),
                )
            )
        return DomLifecycle(mount=DomAction.batch(*listeners))

    return DomEffect.scoped("context-menu" if context else "menu", setup)
