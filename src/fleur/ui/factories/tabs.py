from collections.abc import Mapping
from typing import Unpack

from typing_extensions import TypeAlias

from fleur import Array, Boolean, Cond, Object, View
from fleur.core import Expr, GroupedMsg, PointerEvent
from fleur.core.dom import DomAction, DomEffect, DomElement, DomEvents, DomKeyboardEvent, EventBinding
from fleur.core.expr import ensure_expr
from fleur.core.types import KeyT, ModelT, MsgGroupT
from fleur.core.view import ViewProp, ViewProps
from fleur.ui.views import Box, Button
from fleur.ui.views.types import String, StyleMap, ViewStyleArgs

_TabViews: TypeAlias = Mapping[KeyT, View[ModelT, MsgGroupT]]
TabsContents: TypeAlias = _TabViews[str, ModelT, MsgGroupT] | Expr[_TabViews[str, ModelT, MsgGroupT]]
ActiveTab: TypeAlias = str | Expr[str]


def _tab_stop(tab_list: DomElement, focus: DomElement) -> DomAction:
    selected = tab_list.query(':scope > [aria-selected="true"]').or_else(tab_list.child(0))
    stop = DomElement.when(Cond.every(focus.exists, focus.parent.same_as(tab_list)), focus, selected)
    return stop.with_reference(
        lambda active: tab_list.for_each_child(
            lambda tab, index: tab.set_attribute("tabindex", Cond.when(tab.same_as(active), "0", "-1"))
        )
    )


def _link_tabs(root: DomElement) -> DomAction:
    tab_list = root.child(0)

    def link(tab: DomElement, index: Expr[int]) -> DomAction:
        panel = root.child(index + 1)
        return DomAction.when(
            panel.exists,
            DomAction.batch(
                tab.ensure_id("fleur-tab-"),
                DomAction.when(Cond.equal(panel.id, ""), panel.set_attribute("id", tab.id + "-panel")),
                tab.set_attribute("aria-controls", panel.id),
                panel.set_attribute("aria-labelledby", tab.id),
            ),
        )

    return DomAction.batch(tab_list.for_each_child(link), _tab_stop(tab_list, tab_list.active_element))


def _move_focus(event: DomKeyboardEvent) -> DomAction:
    tab_list, tab = event.current_target, event.target
    left = Cond.equal(event.key, "ArrowLeft")
    right = Cond.equal(event.key, "ArrowRight")
    home = Cond.equal(event.key, "Home")
    end = Cond.equal(event.key, "End")
    forward = Cond.not_equal(right, Cond.equal(tab_list.direction, "rtl"))
    adjacent = DomElement.when(
        forward,
        tab.next_sibling.or_else(tab_list.child(0)),
        tab.previous_sibling.or_else(tab_list.last_child),
    )
    destination = DomElement.when(home, tab_list.child(0), DomElement.when(end, tab_list.last_child, adjacent))
    return DomAction.when(
        Cond.every(
            tab.exists,
            tab.parent.same_as(tab_list),
            Boolean.negate(Cond.some(event.alt, event.ctrl, event.meta)),
            Cond.some(left, right, home, end),
        ),
        DomAction.batch(event.prevent_default(), destination.focus()),
    )


def tabs(
    contents: _TabViews[KeyT, ModelT, MsgGroupT] | Expr[_TabViews[KeyT, ModelT, MsgGroupT]],
    active_tab: KeyT | Expr[KeyT],
    onselect: GroupedMsg[MsgGroupT, PointerEvent, KeyT] | None = None,
    *,
    label: String = "Tabs",
    tab_class: String | None = None,
    tab_style: StyleMap | None = None,
    props: ViewProps | None = None,
    **style_args: Unpack[ViewStyleArgs],
) -> View[ModelT, MsgGroupT]:
    """Render a labelled tab list with manual activation and caller-controlled selection."""
    panels = Expr[_TabViews[KeyT, ModelT, MsgGroupT]](ensure_expr(contents))
    names = Object.keys(panels)

    def trigger(name: Expr[KeyT]) -> View[ModelT, MsgGroupT]:
        attrs: dict[str, ViewProp] = {
            "key": name,
            "type": "button",
            "role": "tab",
            "data-fleur-tabs": "trigger",
            "aria-selected": Cond.when(Cond.equal(name, active_tab), "true", "false"),
        }
        if tab_class is not None:
            attrs["className"] = tab_class
        return Button(name, props=attrs, style=tab_style, onclick=onselect.bind(name) if onselect is not None else None)

    def panel(name: Expr[KeyT]) -> View[ModelT, MsgGroupT]:
        return Box(
            panels[name],
            props={
                "key": name,
                "data-fleur-tabs": "panel",
                "role": "tabpanel",
                "tabindex": 0,
                "hidden": Boolean.negate(Cond.equal(name, active_tab)),
            },
        )

    return Box(
        Box[ModelT, MsgGroupT](
            Array.map(names, trigger),
            props={
                "data-fleur-tabs": "list",
                "role": "tablist",
                "aria-label": label,
                **EventBinding(action=lambda event: _tab_stop(event.current_target, event.target)).properties(
                    "focusin"
                ),
                **EventBinding(action=lambda event: _tab_stop(event.current_target, event.related_target)).properties(
                    "focusout"
                ),
                **EventBinding.on(DomEvents.key_down, action=_move_focus),
            },
        ),
        Array.map(names, panel),
        props=View.extend_props(
            props if props is not None else {},
            {
                "data-fleur-tabs": "root",
                **View.dom_effect(DomEffect("tabs", _link_tabs, watch_subtree=True, after_connect=False)),
            },
        ),
        **style_args,
    )
