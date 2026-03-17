type NormalizedEvent = Record<string, unknown>

const toBoolean = (value: unknown): boolean => Boolean(value)
const toNumber = (value: unknown): number => (typeof value === "number" ? value : 0)
const toString = (value: unknown): string => (typeof value === "string" ? value : "")

const pointerLike = (event: Event): event is Event & Record<string, unknown> => {
  return "clientX" in event && "clientY" in event
}

const keyboardLike = (event: Event): event is Event & Record<string, unknown> => {
  return "key" in event
}

const inputLike = (event: Event): event is Event & { target?: unknown } => {
  return "target" in event
}

const normalizePointerEvent = (event: Event & Record<string, unknown>): NormalizedEvent => ({
  type: toString(event.type),
  pointer_id: toNumber(event.pointerId),
  client_x: toNumber(event.clientX),
  client_y: toNumber(event.clientY),
  button: toNumber(event.button),
  alt: toBoolean(event.altKey),
  ctrl: toBoolean(event.ctrlKey),
  shift: toBoolean(event.shiftKey),
  meta: toBoolean(event.metaKey),
})

const normalizeKeyboardEvent = (event: Event & Record<string, unknown>): NormalizedEvent => ({
  type: toString(event.type),
  key: toString(event.key),
  code: toString(event.code),
  repeat: toBoolean(event.repeat),
  alt: toBoolean(event.altKey),
  ctrl: toBoolean(event.ctrlKey),
  shift: toBoolean(event.shiftKey),
  meta: toBoolean(event.metaKey),
})

const normalizeInputEvent = (event: Event & { target?: unknown }): NormalizedEvent => {
  const target = event.target as { value?: unknown; checked?: unknown } | null
  return {
    type: event.type,
    value: target && "value" in target ? target.value : "",
    checked: Boolean(target && "checked" in target ? target.checked : false),
  }
}

const normalizeFocusEvent = (event: Event): NormalizedEvent => ({
  type: event.type,
})

const normalizeSubmitEvent = (event: Event): NormalizedEvent => ({
  type: event.type,
})

const normalizeFallbackEvent = (event: Event): NormalizedEvent => ({
  type: event.type,
})

const normalizeEventPayload = (eventType: string, event: Event): NormalizedEvent => {
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
