const pending = new WeakMap<HTMLElement, boolean>()

export function enableAnchoredPopover(panel: HTMLElement): boolean {
  const supported = typeof panel.togglePopover === "function"
    && CSS.supports("position-area", "block-end")
    && CSS.supports("anchor-scope", "--fleur-popover-trigger")
  if (supported) panel.popover = "manual"
  return supported
}

export function setPopoverOpen(panel: HTMLElement, open: boolean): void {
  const scheduled = pending.has(panel)
  pending.set(panel, open)
  if (scheduled) return

  // Native popover methods need a connected panel and its fully patched contents.
  queueMicrotask(() => {
    const shouldOpen = pending.get(panel)
    pending.delete(panel)
    if (!panel.isConnected || panel.popover !== "auto" || panel.matches(":popover-open") === shouldOpen) return
    if (shouldOpen) panel.showPopover()
    else panel.hidePopover()
  })
}
