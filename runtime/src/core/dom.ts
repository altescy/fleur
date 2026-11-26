import { EventHandler, EventPayload, RuntimeEventHandler, StyleProps, VNode, VNodeType } from "./types"
import { asVNode, resolveLazy } from "./vdom"
import { normalizeEventPayload } from "./events"
import { syncAccordion } from "../ui/accordion"
import { syncAvatar } from "../ui/avatar"
import { syncCombobox } from "../ui/combobox"
import { syncTabs } from "../ui/tabs"
import { attachHoverPanel } from "../ui/hoverPanel"
import { syncToast } from "../ui/toast"
import { syncToolbar } from "../ui/toolbar"
import { isFleurDialog, setDialogOpen } from "../ui/dialog"
import { attachMenu } from "../ui/menu"
import { syncMenubar } from "../ui/menubar"
import { attachNavigationMenu } from "../ui/navigationMenu"
import { syncNumberField } from "../ui/numberField"
import { setPopoverOpen } from "../ui/popover"

type ElementWithListeners = Element & { __listeners?: Record<string, EventListener> }

const preventSubmitDefault = (event: Event): void => {
  if (event.target === event.currentTarget) event.preventDefault()
}

const usesValueAttribute = (el: Element): boolean => el.localName === "progress" || el.localName === "meter"

export const setProp = (
  el: ElementWithListeners,
  key: string,
  value: string | number | boolean | null | undefined | StyleProps | EventHandler | RuntimeEventHandler,
): void => {
  if (key === "fleurPopoverOpen" && el instanceof HTMLElement) {
    setPopoverOpen(el, value === true)
    return
  }
  if (key === "open" && isFleurDialog(el)) {
    setDialogOpen(el, value === true)
    return
  }
  if (key === "fleurTabs") {
    syncTabs(el)
    return
  }
  if (key === "fleurCombobox" && el instanceof HTMLElement) {
    syncCombobox(el)
    return
  }
  if (key === "fleurToast" && el instanceof HTMLElement) {
    syncToast(el)
    return
  }
  if (key === "fleurAccordion" && el instanceof HTMLElement) {
    syncAccordion(el)
    return
  }
  if (key === "fleurToolbar" && el instanceof HTMLElement) {
    syncToolbar(el)
    return
  }
  if (key === "fleurMenubar" && el instanceof HTMLElement) {
    syncMenubar(el)
    return
  }
  if (key === "fleurAvatar" && el instanceof HTMLElement) {
    syncAvatar(el)
    return
  }
  if (key === "fleurNavigationMenu" && el instanceof HTMLElement) {
    attachNavigationMenu(el)
    return
  }
  if (key === "fleurNumberField" && el instanceof HTMLElement) {
    syncNumberField(el)
    return
  }
  if (key === "fleurPreventSubmitDefault") {
    // Capture runs before the form's submit message can change the view.
    if (value === true) el.addEventListener("submit", preventSubmitDefault, true)
    return
  }

  if (key === "className") {
    el.setAttribute("class", String(value))
    return
  }

  if (key === "style" && value && typeof value === "object") {
    const style = el as HTMLElement
    style.removeAttribute("style")
    for (const [styleKey, styleValue] of Object.entries(value as StyleProps)) {
      if (styleValue == null) continue
      style.style.setProperty(styleKey, String(styleValue))
    }
    return
  }

  if (key.startsWith("on") && typeof value === "function") {
    const type = key.slice(2).toLowerCase()
    if (el.__listeners?.[key]) el.removeEventListener(type, el.__listeners[key])
    const listener = ((event: Event) => {
      // A queued native close event may arrive after the dialog has reopened or unmounted.
      if (type === "close" && isFleurDialog(el) && (el.open || !el.isConnected)) return
      if (type === "toggle" && !el.isConnected) return
      ;(value as (payload: EventPayload) => void)(normalizeEventPayload(type, event))
    }) as EventListener
    el.addEventListener(type, listener)
    el.__listeners = { ...el.__listeners, [key]: listener }
  } else if (key === "value" && !usesValueAttribute(el)) {
    ;(el as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | HTMLOptionElement).value = String(value ?? "")
  } else if (key === "checked") {
    ;(el as HTMLInputElement).checked = Boolean(value)
  } else if (key === "selected") {
    ;(el as HTMLOptionElement).selected = Boolean(value)
  } else if (value != null && value !== false) {
    el.setAttribute(key, String(value))
  }
}

export const removeProp = (el: Element & { __listeners?: Record<string, EventListener> }, key: string): void => {
  if (key === "fleurPopoverOpen" && el instanceof HTMLElement) {
    setPopoverOpen(el, false)
    return
  }
  if (key === "open" && isFleurDialog(el)) {
    setDialogOpen(el, false)
    return
  }
  if (key === "fleurPreventSubmitDefault") {
    el.removeEventListener("submit", preventSubmitDefault, true)
    return
  }

  if (key === "className") {
    el.removeAttribute("class")
    return
  }

  if (key === "style") {
    ;(el as HTMLElement).removeAttribute("style")
    return
  }

  if (key.startsWith("on")) {
    const type = key.slice(2).toLowerCase()
    const listener = el.__listeners?.[key]
    if (listener) {
      el.removeEventListener(type, listener)
      delete el.__listeners?.[key]
    }
  } else {
    if (key === "value" && !usesValueAttribute(el)) {
      ;(el as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | HTMLOptionElement).value = ""
    } else if (key === "checked") {
      ;(el as HTMLInputElement).checked = false
    } else if (key === "selected") {
      ;(el as HTMLOptionElement).selected = false
    }
    el.removeAttribute(key)
  }
}

export const instantiate = (vnode: VNode): Node => {
  const resolved = resolveLazy(vnode)
  switch (resolved.type) {
    case VNodeType.TEXT:
      return document.createTextNode(resolved.value)
    case VNodeType.ELEMENT: {
      const el = document.createElement(resolved.tag)
      const deferValue = resolved.tag === "select" || (resolved.tag === "input" && resolved.props.type === "range")
      for (const [k, v] of Object.entries(resolved.props || {})) {
        if (k === "fleurTabs" || k === "fleurMenu" || k === "fleurTooltip" || k === "fleurPreviewCard"
          || k === "fleurCombobox" || k === "fleurToast"
          || k === "fleurAccordion" || k === "fleurToolbar" || k === "fleurMenubar"
          || k === "fleurAvatar" || k === "fleurNumberField") continue
        if (resolved.tag === "dialog" && k === "open") continue
        if (deferValue && k === "value") continue
        setProp(el, k, v)
      }
      resolved.children
        .map(resolveLazy)
        .map(asVNode)
        .map(instantiate)
        .forEach((c) => el.appendChild(c))
      if (resolved.props.fleurTabs) syncTabs(el)
      if (resolved.props.fleurMenu) attachMenu(el)
      if (resolved.props.fleurTooltip || resolved.props.fleurPreviewCard) attachHoverPanel(el)
      if (resolved.props.fleurCombobox) syncCombobox(el)
      if (resolved.props.fleurToast) syncToast(el)
      if (resolved.props.fleurAccordion) syncAccordion(el)
      if (resolved.props.fleurToolbar) syncToolbar(el)
      if (resolved.props.fleurMenubar) syncMenubar(el)
      if (resolved.props.fleurAvatar) syncAvatar(el)
      if (resolved.props.fleurNumberField) syncNumberField(el)
      if (resolved.tag === "dialog" && resolved.props.open != null) {
        setProp(el, "open", resolved.props.open)
      }
      if (deferValue && resolved.props.value != null) {
        setProp(el, "value", resolved.props.value)
      }
      return el
    }
    default:
      throw new Error("Unknown vnode type")
  }
}
