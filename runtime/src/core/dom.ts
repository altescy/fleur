import { RuntimeEventHandler, StyleProps, VNode, VNodeType, VPropValue } from "./types"
import { asVNode, resolveLazy } from "./vdom"
import { normalizeEventPayload, withDomEventOrigin } from "./events"
import { cancelDomEffect, isDomEffect, isDomEffectProp, scheduleDomEffect } from "./domEffect"

type ElementWithListeners = Element & { __listeners?: Record<string, EventListener> }

const usesValueAttribute = (el: Element): boolean => el.localName === "progress" || el.localName === "meter"
const eventProp = (key: string): { type: string; capture: boolean } => {
  const capture = key.startsWith("onCapture:")
  return { type: key.slice(capture ? "onCapture:".length : 2).toLowerCase(), capture }
}

export const setProp = (
  el: ElementWithListeners,
  key: string,
  value: VPropValue,
): void => {
  if (isDomEffectProp(key)) {
    if (isDomEffect(value)) scheduleDomEffect(el, key, value)
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
    const { type, capture } = eventProp(key)
    if (el.__listeners?.[key]) el.removeEventListener(type, el.__listeners[key], capture)
    const listener = ((event: Event) => {
      if (type === "toggle" && !el.isConnected) return
      const target = event.composedPath().find((node): node is HTMLElement => node instanceof HTMLElement) ?? null
      withDomEventOrigin({ type, target }, () => {
        ;(value as RuntimeEventHandler)(normalizeEventPayload(type, event), el, event)
      })
    }) as EventListener
    el.addEventListener(type, listener, capture)
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
  if (isDomEffectProp(key)) {
    cancelDomEffect(el, key)
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
    const { type, capture } = eventProp(key)
    const listener = el.__listeners?.[key]
    if (listener) {
      el.removeEventListener(type, listener, capture)
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
        if (isDomEffectProp(k)) continue
        if (deferValue && k === "value") continue
        setProp(el, k, v)
      }
      resolved.children
        .map(resolveLazy)
        .map(asVNode)
        .map(instantiate)
        .forEach((c) => el.appendChild(c))
      if (deferValue && resolved.props.value != null) {
        setProp(el, "value", resolved.props.value)
      }
      for (const [key, effect] of Object.entries(resolved.props)) {
        if (isDomEffectProp(key) && isDomEffect(effect)) scheduleDomEffect(el, key, effect)
      }
      return el
    }
    default:
      throw new Error("Unknown vnode type")
  }
}
