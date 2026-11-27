from fleur.core import Boolean, Cond, DomAction, DomElement, DomEvent, Expr
from fleur.core.dom import DomPopover


def modified(event: DomEvent, *, shift: bool = True) -> Expr[bool]:
    return Cond.some(event.default_prevented, event.alt, event.ctrl, event.meta, event.shift if shift else False)


def attribute_is(element: DomElement, attribute: str, value: str) -> Expr[bool]:
    return Cond.equal(element.attribute(attribute), value)


def set_expanded(element: DomElement, expanded: bool | Expr[bool]) -> DomAction:
    return element.set_attribute("aria-expanded", Cond.when(expanded, "true", "false"))


def focus_opener(panel: DomElement) -> DomAction:
    """Give the browser the activating control as its native focus return target."""
    source = panel.event_origin("click").closest(
        'button, input:is([type="button"], [type="submit"], [type="reset"], [type="image"]), [role="button"]'
    )
    return source.focus(prevent_scroll=True)


def supports_anchor(panel: DomPopover) -> Expr[bool]:
    return Cond.every(
        panel.supported,
        DomElement.supports_style("position-area", "block-end"),
        DomElement.supports_style("anchor-scope", "--fleur-popover-trigger"),
    )


def can_focus(root: DomElement, control: DomElement, disabled: str) -> Expr[bool]:
    hidden = control.closest("[hidden], [inert]")
    return Cond.every(
        Boolean.negate(control.matches(disabled)),
        Cond.some(Boolean.negate(hidden.exists), hidden.same_as(root), Boolean.negate(root.contains(hidden))),
    )
