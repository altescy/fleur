import { EventPayload } from "./types"

const toBoolean = (value: boolean | undefined): boolean => Boolean(value)
const toNumber = (value: number | undefined): number => (typeof value === "number" ? value : 0)
const toString = (value: string | undefined): string => (typeof value === "string" ? value : "")

const pointerLike = (event: Event): event is PointerEvent | MouseEvent => "clientX" in event && "clientY" in event

const keyboardLike = (event: Event): event is KeyboardEvent => "key" in event

type InputTarget = HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement

const inputLike = (event: Event): event is Event & { target: EventTarget | null } => "target" in event

const isInputTarget = (target: EventTarget | null): target is InputTarget => {
  if (!target) return false
  return target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement
}

const normalizePointerEvent = (event: PointerEvent | MouseEvent): EventPayload => ({
  type: event.type,
  pointer_id: "pointerId" in event ? toNumber(event.pointerId) : 0,
  client_x: toNumber(event.clientX),
  client_y: toNumber(event.clientY),
  button: toNumber(event.button),
  alt: toBoolean(event.altKey),
  ctrl: toBoolean(event.ctrlKey),
  shift: toBoolean(event.shiftKey),
  meta: toBoolean(event.metaKey),
})

const normalizeKeyboardEvent = (event: KeyboardEvent): EventPayload => ({
  type: event.type,
  key: toString(event.key),
  code: toString(event.code),
  repeat: toBoolean(event.repeat),
  alt: toBoolean(event.altKey),
  ctrl: toBoolean(event.ctrlKey),
  shift: toBoolean(event.shiftKey),
  meta: toBoolean(event.metaKey),
})

const normalizeInputEvent = (event: Event & { target: EventTarget | null }): EventPayload => {
  const target = isInputTarget(event.target) ? event.target : null
  const checked = target instanceof HTMLInputElement ? target.checked : false
  return {
    type: event.type,
    value: target?.value ?? "",
    checked,
  }
}

const normalizeFocusEvent = (event: Event): EventPayload => ({
  type: event.type,
})

const normalizeSubmitEvent = (event: Event): EventPayload => ({
  type: event.type,
})

const normalizeFallbackEvent = (event: Event): EventPayload => ({
  type: event.type,
})

const normalizeEventPayload = (eventType: string, event: Event): EventPayload => {
  if (eventType.startsWith("pointer") && pointerLike(event)) {
    return normalizePointerEvent(event)
  }
  if ((eventType === "click" || eventType.startsWith("mouse")) && pointerLike(event)) {
    return normalizePointerEvent(event)
  }
  if (eventType.startsWith("key") && keyboardLike(event)) {
    return normalizeKeyboardEvent(event)
  }
  if ((eventType === "input" || eventType === "change") && inputLike(event)) {
    return normalizeInputEvent(event)
  }
  if (eventType === "focus" || eventType === "blur") {
    return normalizeFocusEvent(event)
  }
  if (eventType === "submit") {
    return normalizeSubmitEvent(event)
  }
  return normalizeFallbackEvent(event)
}

export { normalizeEventPayload }
