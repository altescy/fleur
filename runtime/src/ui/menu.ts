const itemSelector = 'button[role="menuitem"]'
const openSelector = ":popover-open"
const openAtLastItem = new WeakSet<HTMLElement>()
const autofocusTargets = new WeakMap<HTMLElement, HTMLElement>()
const contextOrigins = new WeakMap<HTMLElement, HTMLElement>()
const pendingTabCloses = new WeakMap<HTMLElement, KeyboardEvent>()
const contextMenuRoot = '[data-fleur-part="context-menu-root"]'

export function menuParts(root: Element): [HTMLElement, HTMLElement] | undefined {
  const trigger = root.firstElementChild
  const panel = trigger?.nextElementSibling
  if (trigger instanceof HTMLElement && panel instanceof HTMLElement && panel.getAttribute("role") === "menu") {
    return [trigger, panel]
  }
}

function menuItems(panel: HTMLElement): HTMLButtonElement[] {
  return Array.from(panel.querySelectorAll<HTMLButtonElement>(`:scope > ${itemSelector}:not([hidden]):not(:disabled)`))
}

function closeMenu(panel: HTMLElement, trigger: HTMLElement): void {
  const origin = contextOrigins.get(panel)
  panel.hidePopover()
  const returnTarget = origin?.isConnected ? origin : trigger
  returnTarget.focus({ preventScroll: true })
}

function openContextMenu(root: HTMLElement, trigger: HTMLElement, panel: HTMLElement, point?: MouseEvent): void {
  const doc = root.ownerDocument
  const focused = doc.activeElement
  const origin = focused instanceof HTMLElement && trigger.contains(focused) ? focused : trigger
  const anchor = origin.getBoundingClientRect()
  contextOrigins.set(panel, origin)
  if (panel.matches(openSelector)) {
    const first = menuItems(panel)[0] ?? panel
    first.focus({ preventScroll: true })
  } else {
    origin.focus({ preventScroll: true })
    panel.showPopover()
  }

  const { width, height } = panel.getBoundingClientRect()
  const { clientWidth, clientHeight } = doc.documentElement
  const gutter = 8
  const x = point?.clientX ?? anchor.left
  const y = point?.clientY ?? anchor.bottom
  root.style.setProperty("--fleur-context-menu-x", `${Math.max(gutter, Math.min(x, clientWidth - width - gutter))}px`)
  root.style.setProperty("--fleur-context-menu-y", `${Math.max(gutter, Math.min(y, clientHeight - height - gutter))}px`)
}

function onContextMenu(event: MouseEvent): void {
  const root = event.currentTarget as HTMLElement
  const parts = menuParts(root)
  if (event.defaultPrevented || !parts || !(event.target instanceof Node) || !parts[0].contains(event.target)) return
  event.preventDefault()
  const [trigger, panel] = parts
  const pointer = event.button === 2 || event.clientX !== 0 || event.clientY !== 0 ? event : undefined
  openContextMenu(root, trigger, panel, pointer)
}

function onMenuBeforeToggle(event: Event): void {
  const parts = menuParts(event.currentTarget as Element)
  if (!parts || event.target !== parts[1] || !("newState" in event)) return
  const [, panel] = parts
  pendingTabCloses.delete(panel)
  autofocusTargets.get(panel)?.removeAttribute("autofocus")
  autofocusTargets.delete(panel)
  if (event.newState !== "open") return

  // The browser runs its popover focusing steps immediately after beforetoggle.
  const items = menuItems(panel)
  const target = (openAtLastItem.has(panel) ? items.at(-1) : items[0]) ?? panel
  if (!target.hasAttribute("autofocus")) {
    target.setAttribute("autofocus", "")
    autofocusTargets.set(panel, target)
  }
}

function onMenuToggle(event: Event): void {
  const parts = menuParts(event.currentTarget as Element)
  if (!parts || event.target !== parts[1]) return
  const [trigger, panel] = parts
  trigger.setAttribute("aria-expanded", String(panel.matches(openSelector)))
}

function onMenuKey(event: KeyboardEvent): void {
  if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return
  const root = event.currentTarget as HTMLElement
  const parts = menuParts(root)
  if (!parts) return
  const [trigger, panel] = parts
  const open = panel.matches(openSelector)
  const context = root.matches(contextMenuRoot)
  if (context && event.target instanceof Node && trigger.contains(event.target)
    && (event.key === "ContextMenu" || (event.key === "F10" && event.shiftKey))) {
    event.preventDefault()
    openContextMenu(root, trigger, panel)
    return
  }
  if (!context && event.target === trigger && !open && (event.key === "ArrowDown" || event.key === "ArrowUp")) {
    event.preventDefault()
    if (event.key === "ArrowUp") openAtLastItem.add(panel)
    trigger.click()
    openAtLastItem.delete(panel)
    return
  }
  if (!open) return
  if (event.key === "Tab") {
    // Let the browser move focus before hiding the panel, including on Shift+Tab.
    pendingTabCloses.set(panel, event)
    setTimeout(() => {
      // A close or reopen in the meantime supersedes this Tab action.
      if (pendingTabCloses.get(panel) !== event) return
      pendingTabCloses.delete(panel)
      if (panel.isConnected && panel.matches(openSelector)) panel.hidePopover()
    }, 0)
    return
  }
  if (event.key === "Escape") {
    event.preventDefault()
    closeMenu(panel, trigger)
    return
  }
  const items = menuItems(panel)
  const index = items.findIndex(item => item === event.target)
  let next: HTMLButtonElement | undefined
  switch (event.key) {
    case "ArrowDown":
      next = index < items.length - 1 ? items[index + 1] : items[0]
      break
    case "ArrowUp":
      next = index <= 0 ? items.at(-1) : items[index - 1]
      break
    case "Home":
      next = items[0]
      break
    case "End":
      next = items.at(-1)
      break
    default:
      return
  }
  event.preventDefault()
  next?.focus()
}

function onMenuClick(event: MouseEvent): void {
  const parts = menuParts(event.currentTarget as Element)
  if (!parts || !(event.target instanceof Element)) return
  const [trigger, panel] = parts
  const item = event.target.closest(itemSelector)
  if (item?.parentElement !== panel) return
  if (item.getAttribute("aria-disabled") === "true") {
    event.preventDefault()
    event.stopPropagation()
    return
  }
  // Finish closing before the action can change the view or move focus.
  if (panel.matches(openSelector)) closeMenu(panel, trigger)
}

export function attachMenu(root: HTMLElement): void {
  root.addEventListener("beforetoggle", onMenuBeforeToggle, true)
  root.addEventListener("toggle", onMenuToggle, true)
  root.addEventListener("keydown", onMenuKey)
  root.addEventListener("click", onMenuClick, true)
  if (root.matches(contextMenuRoot)) root.addEventListener("contextmenu", onContextMenu)
}
