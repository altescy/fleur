import { domEventOrigin, normalizeEventPayload } from "./events"
import { EventPayload } from "./types"

const element = (node: EventTarget | null | undefined): HTMLElement | null =>
  node instanceof HTMLElement ? node : null

const dialog = (node: HTMLElement | null): HTMLDialogElement | null =>
  node instanceof HTMLDialogElement ? node : null

const uniqueId = (prefix: string): string => prefix + crypto.getRandomValues(new Uint32Array(4)).join("-")

export const Dom = {
  element,
  uniqueId,
  document: (node: HTMLElement | null) => node?.ownerDocument ?? null,
  queryAll: (target: ParentNode | null, selector: string) =>
    Array.from(target?.querySelectorAll(selector) ?? []).filter(child => child instanceof HTMLElement),
  at: (nodes: HTMLElement[], index: number) => nodes.at(index) ?? null,
  closest: (node: HTMLElement | null, selector: string) => element(node?.closest(selector)),
  matches: (node: HTMLElement | null, selector: string) => node?.matches(selector) ?? false,
  contains: (node: HTMLElement | null, other: HTMLElement | null) => node?.contains(other) ?? false,
  text: (node: HTMLElement | null) => node?.textContent ?? "",
  setText: (node: HTMLElement | null, value: string) => {
    if (node && node.textContent !== value) node.textContent = value
  },
  hidden: (node: HTMLElement | null) => node?.hidden ?? false,
  setHidden: (node: HTMLElement | null, hidden: boolean) => {
    if (node && node.hidden !== hidden) node.hidden = hidden
  },
  click: (node: HTMLElement | null) => node?.click(),
  dispatch: (node: HTMLElement | null, type: string, bubbles: boolean, detail: string | null) => {
    node?.dispatchEvent(detail === null ? new Event(type, { bubbles }) : new CustomEvent(type, { bubbles, detail }))
  },
  removeAttribute: (node: HTMLElement | null, name: string) => node?.removeAttribute(name),
  setStyle: (node: HTMLElement | null, name: string, value: string) => node?.style.setProperty(name, value),
  scrollIntoView: (node: HTMLElement | null, block: ScrollLogicalPosition) => node?.scrollIntoView({ block }),
  bounds: (node: HTMLElement | null) => node?.getBoundingClientRect() ?? new DOMRect(),
  viewportWidth: (node: HTMLElement | null) => node?.ownerDocument.documentElement.clientWidth ?? 0,
  viewportHeight: (node: HTMLElement | null) => node?.ownerDocument.documentElement.clientHeight ?? 0,
  popoverSupported: (node: HTMLElement | null) => typeof node?.togglePopover === "function",
  popoverMode: (node: HTMLElement | null) => node?.popover ?? null,
  showPopover: (node: HTMLElement | null) => node?.showPopover?.(),
  hidePopover: (node: HTMLElement | null) => node?.hidePopover?.(),
  togglePopover: (node: HTMLElement | null, open: boolean) => node?.togglePopover?.(open),
  cssSupports: (property: string, value: string) => CSS.supports(property, value),
  input: (node: HTMLElement | null) => node instanceof HTMLInputElement ? node : null,
  cloneInput: (node: HTMLElement | null) => node instanceof HTMLInputElement ? node.cloneNode() : null,
  inputValue: (node: HTMLInputElement | null) => node?.value ?? "",
  setInputValue: (node: HTMLInputElement | null, value: string) => {
    if (node && node.value !== value) node.value = value
  },
  step: (node: HTMLInputElement | null, direction: 1 | -1) => {
    if (direction === 1) node?.stepUp()
    else node?.stepDown()
  },
  imageComplete: (node: HTMLElement | null) => node instanceof HTMLImageElement && node.complete,
  imageWidth: (node: HTMLElement | null) => node instanceof HTMLImageElement ? node.naturalWidth : 0,
  imageSource: (node: HTMLElement | null) => node instanceof HTMLImageElement ? node.src : "",
  imageCurrentSource: (node: HTMLElement | null) => node instanceof HTMLImageElement ? node.currentSrc : "",
  now: () => performance.now(),
  child: (node: HTMLElement | null, index: number) => element(node?.children[index]),
  children: (node: HTMLElement | null) => Array.from(node?.children ?? []).filter((child) => child instanceof HTMLElement),
  query: (node: HTMLElement | null, selector: string) => element(node?.querySelector(selector)),
  parent: (node: HTMLElement | null) => element(node?.parentElement),
  previous: (node: HTMLElement | null) => element(node?.previousElementSibling),
  next: (node: HTMLElement | null) => element(node?.nextElementSibling),
  last: (node: HTMLElement | null) => element(node?.lastElementChild),
  active: (node: HTMLElement | null) => element(node?.ownerDocument.activeElement),
  eventOrigin: (node: HTMLElement | null, type: string) => {
    const origin = domEventOrigin()
    return origin?.type === type && origin.target?.ownerDocument === node?.ownerDocument ? origin.target : null
  },
  attribute: (node: HTMLElement | null, name: string) => node?.getAttribute(name) ?? null,
  id: (node: HTMLElement | null) => node?.id ?? "",
  direction: (node: HTMLElement | null) => node ? getComputedStyle(node).direction : "",
  connected: (node: HTMLElement | null) => node?.isConnected ?? false,
  focus: (node: HTMLElement | null, preventScroll: boolean) => node?.focus({ preventScroll }),
  setAttribute: (node: HTMLElement | null, name: string, value: string) => {
    if (node && node.getAttribute(name) !== value) node.setAttribute(name, value)
  },
  ensureId: (node: HTMLElement | null, prefix: string) => {
    if (node && !node.id) node.id = uniqueId(prefix)
  },
  dialogOpen: (node: HTMLElement | null) => dialog(node)?.open ?? false,
  showModal: (node: HTMLElement | null) => dialog(node)?.showModal(),
  closeDialog: (node: HTMLElement | null) => dialog(node)?.close(),
  toggleState: (event: Event) => "newState" in event ? event.newState : null,
  detailText: (event: Event) => event instanceof CustomEvent && typeof event.detail === "string" ? event.detail : null,
  eventValue: (event: Event, name: string, type: "string" | "number") => {
    const value: unknown = Reflect.get(event, name)
    return typeof value === type ? value : null
  },
  focusById: async (id: string, preventScroll: boolean): Promise<null> => {
    // Rendering and its deferred effects are scheduled before commands.
    await Promise.resolve()
    const node = document.getElementById(id)
    if (!node) throw "not_found"
    if (node instanceof HTMLElement) {
      node.focus({ preventScroll })
      if (node.ownerDocument.activeElement === node) return null
    }
    throw "not_focusable"
  },
  listener: (
    target: EventTarget | null,
    type: string,
    handler: (event: Event, payload: EventPayload) => void,
    capture: boolean,
    controller: AbortController,
  ) => {
    const listener = (event: Event) => handler(event, normalizeEventPayload(event.type, event))
    return {
      attach: () => target?.addEventListener(type, listener, { capture, signal: controller.signal }),
      detach: () => target?.removeEventListener(type, listener, capture),
    }
  },
}
