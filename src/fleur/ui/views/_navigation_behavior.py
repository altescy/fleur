from fleur.core import Boolean, Cond, DomAction, DomEffect, DomElement, Expr, String
from fleur.core.dom import DomElements, DomEvents, DomKeyboardEvent, DomLifecycle, DomPointerEvent, DomScope

from ._dom_helpers import attribute_is, can_focus, modified, set_expanded

_NAV_TRIGGER = 'button[data-fleur-part="navigation-trigger"]'
_CONTROL = 'button:where(:not([role]), [role="button"]), a:where(:not([role]), [role="link"])'
_BOUNDARY = (
    '[role="toolbar"], [role="menu"], [role="dialog"], [role="alertdialog"], [role="tablist"], [role="tabpanel"]'
)
_TOGGLE_GROUP = '[data-fleur-ui="toggle-group"]'
_DISABLED = ':disabled, [aria-disabled="true"]'


def _show_links(trigger: DomElement, expanded: bool | Expr[bool]) -> DomAction:
    links = trigger.next_sibling
    return DomAction.when(
        links.exists, DomAction.batch(set_expanded(trigger, expanded), links.set_hidden(Boolean.negate(expanded)))
    )


def navigation_menu_effect() -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        expanded = root.query_all(f':scope > ul > li > {_NAV_TRIGGER}[aria-expanded="true"]')
        multiple = root.has_attribute("data-fleur-multiple")
        keep_open = root.has_attribute("data-fleur-keep-open")
        # Safari and Firefox on macOS do not focus a clicked button, so focus leaves an open group
        # with no related target while its trigger is pressed. Let the click decide instead.
        pressing = scope.value(False)
        released = [
            scope.document_listener(root, name, lambda _: pressing.set(False), capture=True)
            for name in ("pointerup", "pointercancel")
        ]

        def expanded_for(target: DomElement) -> DomElement:
            return expanded.find(lambda trigger: trigger.parent.contains(target))

        def close_all() -> DomAction:
            return expanded.for_each(lambda trigger, _: _show_links(trigger, False))

        def on_click(event: DomPointerEvent) -> DomAction:
            target = event.target
            trigger = target.closest(_NAV_TRIGGER)
            link = target.closest("a[href]")
            target_name = String.or_empty(link.attribute("target"))
            follow_link = Cond.every(
                Boolean.negate(keep_open),
                Cond.equal(event.button, 0),
                Boolean.negate(modified(event)),
                link.exists,
                Boolean.negate(link.has_attribute("download")),
                Cond.some(Cond.equal(target_name, ""), Cond.equal(String.lower(target_name), "_self")),
            )

            def close_link_group(group: DomElement) -> DomAction:
                return DomAction.batch(
                    DomAction.when(link.same_as(root.active_element), group.focus(prevent_scroll=True)),
                    _show_links(group, False),
                )

            # Snapshot the expanded state before closing siblings or updating the trigger.
            toggle = DomAction.with_value(
                Boolean.negate(attribute_is(trigger, "aria-expanded", "true")),
                lambda opening: DomAction.batch(
                    DomAction.when(Cond.every(opening, Boolean.negate(multiple)), close_all()),
                    _show_links(trigger, opening),
                ),
            )
            return DomAction.when(
                Cond.every(
                    Boolean.negate(event.default_prevented),
                    target.closest('[data-fleur-ui="navigation-menu"]').same_as(root),
                ),
                DomAction.when(
                    trigger.exists,
                    toggle,
                    otherwise=DomAction.when(follow_link, expanded_for(link).with_reference(close_link_group)),
                ),
            )

        def on_key(event: DomKeyboardEvent) -> DomAction:
            trigger = DomElement.when(multiple, expanded_for(event.target), expanded.at(0))
            return DomAction.when(
                Cond.every(
                    Cond.equal(event.key, "Escape"), Boolean.negate(event.default_prevented), event.target.exists
                ),
                trigger.with_reference(
                    lambda group: DomAction.when(
                        group.exists, DomAction.batch(event.prevent_default(), group.focus(), _show_links(group, False))
                    )
                ),
            )

        return DomLifecycle(
            mount=DomAction.batch(
                *(listener.attach() for listener in released),
                scope.on(root, DomEvents.click, on_click),
                scope.on(root, DomEvents.key_down, on_key),
                scope.listen(
                    root,
                    "pointerdown",
                    lambda _: pressing.set(True),
                    capture=True,
                ),
                scope.listen(
                    root,
                    "focusout",
                    lambda event: DomAction.when(
                        Boolean.negate(Cond.some(keep_open, pressing.value, root.contains(event.related_target))),
                        close_all(),
                    ),
                ),
            )
        )

    return DomEffect.scoped("navigation-menu", setup, after_connect=False)


def toolbar_effect() -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        stop = scope.reference()
        is_group = root.matches(_TOGGLE_GROUP)
        boundary = Cond.when(is_group, f"{_BOUNDARY}, {_TOGGLE_GROUP}", _BOUNDARY)
        owned_by_toolbar = Cond.every(is_group, attribute_is(root.closest(_BOUNDARY), "role", "toolbar"))
        controls = root.query_all(_CONTROL).filter(
            lambda control: Cond.every(Boolean.negate(owned_by_toolbar), control.closest(boundary).same_as(root))
        )

        def available(items: DomElements) -> DomElements:
            return items.filter(lambda control: can_focus(root, control, f"{_DISABLED}, a:not([href])"))

        def sync() -> DomAction:
            def use_controls(items: DomElements) -> DomAction:
                def choose(choices: DomElements) -> DomAction:
                    active = choices.find(lambda control: control.same_as(root.active_element))
                    return DomAction.batch(
                        stop.set(
                            active.or_else(
                                DomElement.when(choices.index_of(stop.element) >= 0, stop.element, choices.at(0))
                            )
                        ),
                        items.for_each(
                            lambda control, _: control.set_attribute(
                                "tabindex", Cond.when(control.same_as(stop.element), "0", "-1")
                            )
                        ),
                    )

                return available(items).with_snapshot(choose)

            return controls.with_snapshot(use_controls)

        def on_key(event: DomKeyboardEvent) -> DomAction:
            vertical = Cond.some(
                attribute_is(root, "aria-orientation", "vertical"),
                Cond.every(
                    Boolean.negate(root.has_attribute("aria-orientation")),
                    attribute_is(root, "data-fleur-orientation", "vertical"),
                ),
            )
            forward = Cond.equal(event.key, Cond.when(vertical, "ArrowDown", "ArrowRight"))
            backward = Cond.equal(event.key, Cond.when(vertical, "ArrowUp", "ArrowLeft"))
            rtl = Cond.every(Boolean.negate(vertical), Cond.equal(root.direction, "rtl"))
            home, end = Cond.equal(event.key, "Home"), Cond.equal(event.key, "End")

            def navigate(items: DomElements) -> DomAction:
                index = items.index_of(event.target)
                step = Cond.when(Cond.not_equal(forward, rtl), 1, -1)
                destination = Cond.when(
                    home, 0, Cond.when(end, items.length - 1, (index + step + items.length) % items.length)
                )
                return DomAction.when(
                    index >= 0, DomAction.batch(event.prevent_default(), items.at(destination).focus())
                )

            return DomAction.when(
                Cond.every(Boolean.negate(modified(event)), Cond.some(forward, backward, home, end)),
                available(controls).with_snapshot(navigate),
            )

        synchronize = scope.action(sync())
        return DomLifecycle(
            mount=DomAction.batch(
                scope.listen(root, "focusin", lambda _: synchronize), scope.on(root, DomEvents.key_down, on_key)
            ),
            update=synchronize,
        )

    return DomEffect.scoped("toolbar", setup, watch_subtree=True, after_connect=False)


def menubar_effect() -> DomEffect:
    def setup(root: DomElement, scope: DomScope) -> DomLifecycle:
        menus = root.query_all(':scope > [data-fleur-part="popover-root"]').filter(
            lambda menu: Cond.every(menu.child(0).matches("button"), attribute_is(menu.child(1), "role", "menu"))
        )

        def available(items: DomElements) -> DomElements:
            return items.filter(lambda menu: can_focus(root, menu.child(0), _DISABLED))

        def contains_focus(menu: DomElement, target: DomElement) -> Expr[bool]:
            return Cond.some(menu.child(0).contains(target), menu.child(1).contains(target))

        def sync() -> DomAction:
            def use_menus(items: DomElements) -> DomAction:
                def choose(choices: DomElements) -> DomAction:
                    stop = (
                        choices.find(lambda menu: contains_focus(menu, root.active_element))
                        .or_else(choices.find(lambda menu: attribute_is(menu.child(0), "tabindex", "0")))
                        .or_else(choices.at(0))
                    )
                    return stop.with_reference(
                        lambda selected: items.for_each(
                            lambda menu, _: DomAction.batch(
                                menu.set_attribute("role", "none"),
                                menu.child(0).set_attribute("role", "menuitem"),
                                menu.child(0).set_attribute("tabindex", Cond.when(menu.same_as(selected), "0", "-1")),
                            )
                        )
                    )

                return available(items).with_snapshot(choose)

            return menus.with_snapshot(use_menus)

        def on_key(event: DomKeyboardEvent) -> DomAction:
            right = Cond.equal(event.key, "ArrowRight")
            horizontal = Cond.some(right, Cond.equal(event.key, "ArrowLeft"))

            def navigate(items: DomElements) -> DomAction:
                def move(index: Expr[int]) -> DomAction:
                    menu = items.at(index)
                    trigger = menu.child(0)
                    panel = menu.child(1).as_popover()
                    step = Cond.when(Cond.not_equal(right, Cond.equal(root.direction, "rtl")), 1, -1)
                    destination = items.at((index + step + items.length) % items.length).child(0)

                    def switch_menu(opened: Expr[bool]) -> DomAction:
                        return DomAction.batch(
                            event.prevent_default(),
                            DomAction.when(
                                Boolean.negate(destination.same_as(trigger)),
                                DomAction.batch(
                                    DomAction.when(opened, panel.hide()),
                                    destination.focus(prevent_scroll=True),
                                    DomAction.when(opened, destination.click()),
                                ),
                            ),
                        )

                    return DomAction.when(
                        index >= 0,
                        DomAction.when(
                            horizontal,
                            DomAction.when(
                                Boolean.negate(event.shift), DomAction.with_value(panel.is_open, switch_menu)
                            ),
                            # Tab continues from the menubar's single tab stop.
                            otherwise=DomAction.when(
                                panel.is_open, DomAction.batch(panel.hide(), trigger.focus(prevent_scroll=True))
                            ),
                        ),
                    )

                return DomAction.with_value(items.index_where(lambda menu: contains_focus(menu, event.target)), move)

            return DomAction.when(
                Cond.every(
                    Boolean.negate(modified(event, shift=False)),
                    event.target.exists,
                    Cond.some(horizontal, Cond.equal(event.key, "Tab")),
                ),
                available(menus).with_snapshot(navigate),
            )

        synchronize = scope.action(sync())
        return DomLifecycle(
            mount=DomAction.batch(
                scope.listen(root, "focusin", lambda _: synchronize), scope.on(root, DomEvents.key_down, on_key)
            ),
            update=synchronize,
        )

    return DomEffect.scoped("menubar", setup, watch_subtree=True, after_connect=False)
