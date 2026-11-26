from collections.abc import Mapping
from typing import Unpack

from typing_extensions import TypeAlias

from fleur import Array, Boolean, Cond, Object, View
from fleur.core import Expr, GroupedMsg, PointerEvent
from fleur.core.expr import ensure_expr
from fleur.core.types import KeyT, ModelT, MsgGroupT
from fleur.core.view import ViewProp, ViewProps
from fleur.ui.views import Box, Button
from fleur.ui.views._utils import extend_props
from fleur.ui.views.types import String, StyleMap, ViewStyleArgs

_TabViews: TypeAlias = Mapping[KeyT, View[ModelT, MsgGroupT]]
TabsContents: TypeAlias = _TabViews[str, ModelT, MsgGroupT] | Expr[_TabViews[str, ModelT, MsgGroupT]]
ActiveTab: TypeAlias = str | Expr[str]


def tabs(
    contents: _TabViews[KeyT, ModelT, MsgGroupT] | Expr[_TabViews[KeyT, ModelT, MsgGroupT]],
    active_tab: KeyT | Expr[KeyT],
    onselect: GroupedMsg[MsgGroupT, PointerEvent, KeyT] | None = None,
    *,
    tab_class: String | None = None,
    tab_style: StyleMap | None = None,
    props: ViewProps | None = None,
    **style_args: Unpack[ViewStyleArgs],
) -> View[ModelT, MsgGroupT]:
    """Style the wrapper with props and shorthands, or every tab button with tab_class and tab_style."""
    panels = Expr[_TabViews[KeyT, ModelT, MsgGroupT]](ensure_expr(contents))
    names = Object.keys(panels)

    def trigger(name: Expr[KeyT]) -> View[ModelT, MsgGroupT]:
        attrs: dict[str, ViewProp] = {
            "type": "button",
            "data-fleur-tabs": "trigger",
            "aria-pressed": Cond.when(Cond.equal(name, active_tab), "true", "false"),
        }
        if tab_class is not None:
            attrs["className"] = tab_class
        return Button(name, props=attrs, style=tab_style, onclick=onselect.bind(name) if onselect is not None else None)

    def panel(name: Expr[KeyT]) -> View[ModelT, MsgGroupT]:
        return Box(panels[name], props={"hidden": Boolean.negate(Cond.equal(name, active_tab))})

    return Box(
        Box[ModelT, MsgGroupT](Array.map(names, trigger), props={"data-fleur-tabs": "list"}),
        Array.map(names, panel),
        props=extend_props(props if props is not None else {}, {"data-fleur-tabs": "root"}),
        **style_args,
    )
