type CloseReason = "timeout" | "dismiss"

const synchronize = new WeakMap<HTMLElement, () => void>()
const maxTimeout = 2_147_483_647

export function syncToast(root: HTMLElement): void {
  const existing = synchronize.get(root)
  if (existing) {
    existing()
    return
  }

  const [announcement, popup] = Array.from(root.children)
  if (!(announcement instanceof HTMLElement) || !(popup instanceof HTMLElement)) return
  const [message, dismissButton] = Array.from(popup.children)
  if (!(message instanceof HTMLElement) || !(dismissButton instanceof HTMLButtonElement)) return
  const doc = root.ownerDocument

  let requested = false
  let lastMessage = ""
  let lastDuration: string | null = null
  let hovered = false
  let focusWithin = false
  let previousFocus: HTMLElement | undefined
  let timer: ReturnType<typeof setTimeout> | undefined
  let remaining: number | null = null
  let startedAt = 0

  const pauseTimer = (): void => {
    if (timer === undefined || remaining === null) return
    clearTimeout(timer)
    timer = undefined
    remaining = Math.max(0, remaining - (performance.now() - startedAt))
  }

  const hide = (): void => {
    pauseTimer()
    remaining = null
    if (popup.hidden) return
    const restoreFocus = popup.contains(doc.activeElement)
    popup.hidden = true
    announcement.textContent = ""
    if (restoreFocus && previousFocus?.isConnected) previousFocus.focus({ preventScroll: true })
    previousFocus = undefined
  }

  const close = (reason: CloseReason): void => {
    if (popup.hidden || !root.isConnected) return
    hide()
    root.dispatchEvent(new CustomEvent<CloseReason>("toastclose", { detail: reason }))
  }

  const updateTimer = (): void => {
    if (popup.hidden || hovered || focusWithin) {
      pauseTimer()
      return
    }
    if (remaining === null || timer !== undefined) return
    startedAt = performance.now()
    timer = setTimeout(() => {
      timer = undefined
      close("timeout")
    }, remaining)
  }

  const sync = (): void => {
    if (!root.isConnected) return
    if (!root.hasAttribute("data-fleur-toast-open")) {
      requested = false
      hide()
      return
    }

    const text = message.textContent ?? ""
    const duration = root.getAttribute("data-fleur-toast-duration")
    if (requested && text === lastMessage && duration === lastDuration) return
    requested = true
    lastMessage = text
    lastDuration = duration

    if (popup.hidden) {
      previousFocus = doc.activeElement instanceof HTMLElement ? doc.activeElement : undefined
      popup.hidden = false
      hovered = popup.matches(":hover")
      focusWithin = popup.contains(doc.activeElement)
    }
    if (announcement.textContent !== text) announcement.textContent = text
    pauseTimer()
    const milliseconds = Number(duration)
    remaining = duration !== null && Number.isFinite(milliseconds)
      ? Math.max(0, Math.min(maxTimeout, milliseconds))
      : null
    updateTimer()
  }

  popup.addEventListener("pointerenter", event => {
    if (event.pointerType === "touch") return
    hovered = true
    updateTimer()
  })
  popup.addEventListener("pointerleave", event => {
    if (event.pointerType === "touch") return
    hovered = false
    updateTimer()
  })
  popup.addEventListener("focusin", () => {
    focusWithin = true
    updateTimer()
  })
  popup.addEventListener("focusout", event => {
    focusWithin = event.relatedTarget instanceof Node && popup.contains(event.relatedTarget)
    updateTimer()
  })
  dismissButton.addEventListener("click", () => close("dismiss"))

  synchronize.set(root, sync)
  queueMicrotask(sync)
}
