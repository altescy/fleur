export const isFleurDialog = (el: Element): el is HTMLDialogElement =>
  el.localName === "dialog" && el.getAttribute("data-fleur-ui") === "dialog"

const pending = new WeakMap<HTMLDialogElement, boolean>()

export function setDialogOpen(dialog: HTMLDialogElement, open: boolean): void {
  const scheduled = pending.has(dialog)
  if (!scheduled && dialog.open === open) return
  pending.set(dialog, open)
  if (scheduled) return

  // showModal requires a connected element. Focus events must also see the fully patched view.
  queueMicrotask(() => {
    const shouldOpen = pending.get(dialog)
    pending.delete(dialog)
    if (!dialog.isConnected || dialog.open === shouldOpen) return
    if (shouldOpen) dialog.showModal()
    else dialog.close()
  })
}
