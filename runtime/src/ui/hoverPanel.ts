import { enableAnchoredPopover } from "./popover"

const previewCardPanel = '[data-fleur-part="preview-card-panel"]'
const panelSelector = `:is([data-fleur-part="tooltip-panel"], ${previewCardPanel})`
const dismissPanel = new WeakMap<Element, () => void>()
const hoverDelay = 350
const leaveDelay = 120

function onEscape(event: KeyboardEvent): void {
  if (event.key !== "Escape" || event.defaultPrevented) return
  const doc = event.currentTarget as Document
  const visible = doc.querySelectorAll(`${panelSelector}:not([hidden])`)
  for (const panel of Array.from(visible)) dismissPanel.get(panel)?.()
  if (visible.length > 0) event.preventDefault()
}

export function attachHoverPanel(root: HTMLElement): void {
  const panel = root.lastElementChild
  if (!(panel instanceof HTMLElement) || !panel.matches(panelSelector)) return
  const anchored = enableAnchoredPopover(panel)

  let hovered = false
  let focused = false
  let timer: ReturnType<typeof setTimeout> | undefined

  const show = (visible: boolean): void => {
    const wasVisible = !panel.hidden
    if (!panel.isConnected || wasVisible === visible) return
    panel.hidden = !visible
    if (anchored) panel.togglePopover(visible)
  }

  const update = (delay = 0): void => {
    clearTimeout(timer)
    const visible = focused || hovered
    if (delay > 0 && panel.hidden === visible) timer = setTimeout(() => show(visible), delay)
    else show(visible)
  }

  const dismiss = (): void => {
    // Only a subsequent pointer entry or keyboard focus can reopen a dismissed panel.
    hovered = false
    focused = false
    update()
  }
  dismissPanel.set(panel, dismiss)
  root.ownerDocument.addEventListener("keydown", onEscape)

  root.addEventListener("pointerenter", event => {
    if (event.pointerType === "touch") return
    hovered = true
    update(hoverDelay)
  })
  root.addEventListener("pointerleave", event => {
    if (event.pointerType === "touch") return
    hovered = false
    update(leaveDelay)
  })
  root.addEventListener("focusin", event => {
    const target = event.target
    if (!(target instanceof HTMLElement) || !target.matches(":focus-visible")) return
    focused = true
    update()
  })
  root.addEventListener("focusout", event => {
    if (event.relatedTarget instanceof Node && root.contains(event.relatedTarget)) return
    focused = false
    update()
  })
  if (panel.matches(previewCardPanel)) {
    root.addEventListener("click", event => {
      if (event.target instanceof Node && root.firstElementChild?.contains(event.target)) dismiss()
    })
  }
}

