import { VNode, VNodeType } from "./types"
import { asVNode, resolveLazy } from "./vdom"
import { normalizeEventPayload } from "./events"

export const setProp = (el: Element & { __listeners?: Record<string, EventListener> }, key: string, value: unknown): void => {
  if (key === "className") {
    el.setAttribute("class", String(value))
    return
  }

  if (key === "style" && value && typeof value === "object") {
    const style = el as HTMLElement
    style.removeAttribute("style")
    for (const [styleKey, styleValue] of Object.entries(value as Record<string, unknown>)) {
      if (styleValue == null) continue
      style.style.setProperty(styleKey, String(styleValue))
    }
    return
  }

  if (key.startsWith("on") && typeof value === "function") {
    const type = key.slice(2).toLowerCase()
    if (el.__listeners?.[key]) el.removeEventListener(type, el.__listeners[key])
    const listener = ((event: Event) => {
      ;(value as (payload: unknown) => unknown)(normalizeEventPayload(type, event))
    }) as EventListener
    el.addEventListener(type, listener)
    el.__listeners = { ...el.__listeners, [key]: listener }
  } else if (value) {
    el.setAttribute(key, String(value))
  }
}

export const removeProp = (el: Element & { __listeners?: Record<string, EventListener> }, key: string): void => {
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
      for (const [k, v] of Object.entries(resolved.props || {})) {
        setProp(el, k, v)
      }
      resolved.children
        .map(resolveLazy)
        .map(asVNode)
        .map(instantiate)
        .forEach((c) => el.appendChild(c))
      return el
    }
    default:
      throw new Error("Unknown vnode type")
  }
}
