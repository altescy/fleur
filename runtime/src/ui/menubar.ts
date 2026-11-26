import { menuParts } from "./menu"

type MenubarMenu = [trigger: HTMLButtonElement, panel: HTMLElement]

function menubarMenus(root: HTMLElement): MenubarMenu[] {
  const menus: MenubarMenu[] = []
  for (const child of Array.from(root.children)) {
    if (!child.matches('[data-fleur-part="popover-root"]')) continue
    const parts = menuParts(child)
    if (parts?.[0] instanceof HTMLButtonElement) menus.push([parts[0], parts[1]])
  }
  return menus
}

function canFocus(root: HTMLElement, [trigger]: MenubarMenu): boolean {
  if (trigger.matches(':disabled, [aria-disabled="true"]')) return false
  const hidden = trigger.closest("[hidden], [inert]")
  return !hidden || hidden === root || !root.contains(hidden)
}

function containsFocus([trigger, panel]: MenubarMenu, target: Node | null): boolean {
  return trigger.contains(target) || panel.contains(target)
}

function updateTabStop(root: HTMLElement, menus: MenubarMenu[]): void {
  const available = menus.filter(menu => canFocus(root, menu))
  const focused = root.ownerDocument.activeElement
  const stop = available.find(menu => containsFocus(menu, focused))
    ?? available.find(([trigger]) => trigger.getAttribute("tabindex") === "0")
    ?? available[0]
  for (const [trigger] of menus) {
    const index = trigger === stop?.[0] ? "0" : "-1"
    if (trigger.getAttribute("tabindex") !== index) trigger.setAttribute("tabindex", index)
  }
}

function onMenubarFocus(event: FocusEvent): void {
  const root = event.currentTarget as HTMLElement
  updateTabStop(root, menubarMenus(root))
}

function onMenubarKey(event: KeyboardEvent): void {
  if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return
  const horizontal = event.key === "ArrowLeft" || event.key === "ArrowRight"
  if ((!horizontal && event.key !== "Tab") || !(event.target instanceof Node)) return

  const root = event.currentTarget as HTMLElement
  const target = event.target
  const menus = menubarMenus(root).filter(menu => canFocus(root, menu))
  const index = menus.findIndex(menu => containsFocus(menu, target))
  if (index < 0) return
  const [trigger, panel] = menus[index]
  const open = panel.matches(":popover-open")

  if (!horizontal) {
    if (open) {
      panel.hidePopover()
      // Let native Tab order continue from the menubar's single tab stop.
      trigger.focus({ preventScroll: true })
    }
    return
  }
  if (event.shiftKey) return
  event.preventDefault()
  const rtl = getComputedStyle(root).direction === "rtl"
  const step = (event.key === "ArrowRight") !== rtl ? 1 : -1
  const [next] = menus[(index + step + menus.length) % menus.length]
  if (next === trigger) return
  if (open) panel.hidePopover()
  next.focus({ preventScroll: true })
  if (open) next.click()
}

export function syncMenubar(root: HTMLElement): void {
  const menus = menubarMenus(root)
  for (const [trigger] of menus) {
    trigger.parentElement?.setAttribute("role", "none")
    trigger.setAttribute("role", "menuitem")
  }
  updateTabStop(root, menus)
  root.addEventListener("focusin", onMenubarFocus)
  root.addEventListener("keydown", onMenubarKey)
}
