const stops = new WeakMap<HTMLElement, HTMLElement>()
const controlSelector = 'button:where(:not([role]), [role="button"]), a:where(:not([role]), [role="link"])'
const groupBoundary = '[role="toolbar"], [role="menu"], [role="dialog"], [role="alertdialog"], [role="tablist"], [role="tabpanel"]'
const toggleGroup = '[data-fleur-ui="toggle-group"]'

function toolbarControls(root: HTMLElement): HTMLElement[] {
  const isToggleGroup = root.matches(toggleGroup)
  // A toolbar manages all of its action buttons, including buttons in a toggle subgroup.
  if (isToggleGroup && root.closest(groupBoundary)?.getAttribute("role") === "toolbar") return []
  const boundary = isToggleGroup ? `${groupBoundary}, ${toggleGroup}` : groupBoundary
  return Array.from(root.querySelectorAll<HTMLElement>(controlSelector))
    .filter(control => control.closest(boundary) === root)
}

function canFocus(root: HTMLElement, control: HTMLElement): boolean {
  if (control.matches(':disabled, [aria-disabled="true"], a:not([href])')) return false
  const hidden = control.closest("[hidden], [inert]")
  return !hidden || hidden === root || !root.contains(hidden)
}

function updateStop(root: HTMLElement): void {
  const controls = toolbarControls(root)
  const available = controls.filter(control => canFocus(root, control))
  const focused = available.find(control => control === root.ownerDocument.activeElement)
  const previous = stops.get(root)
  const stop = focused ?? (previous && available.includes(previous) ? previous : available[0])
  if (stop) stops.set(root, stop)
  else stops.delete(root)
  for (const control of controls) {
    const index = control === stop ? "0" : "-1"
    if (control.getAttribute("tabindex") !== index) control.setAttribute("tabindex", index)
  }
}

function onToolbarFocus(event: FocusEvent): void {
  updateStop(event.currentTarget as HTMLElement)
}

function onToolbarKey(event: KeyboardEvent): void {
  if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return
  const root = event.currentTarget as HTMLElement
  const available = toolbarControls(root).filter(control => canFocus(root, control))
  const index = available.findIndex(control => control === event.target)
  if (index < 0) return

  let next: number
  if (event.key === "Home") next = 0
  else if (event.key === "End") next = available.length - 1
  else {
    const orientation = root.getAttribute("aria-orientation") ?? root.getAttribute("data-fleur-orientation")
    const vertical = orientation === "vertical"
    const forwardKey = vertical ? "ArrowDown" : "ArrowRight"
    const backwardKey = vertical ? "ArrowUp" : "ArrowLeft"
    if (event.key !== forwardKey && event.key !== backwardKey) return
    const rtl = !vertical && getComputedStyle(root).direction === "rtl"
    const moveForward = (event.key === forwardKey) !== rtl
    next = (index + (moveForward ? 1 : -1) + available.length) % available.length
  }
  event.preventDefault()
  available[next].focus()
}

export function syncToolbar(root: HTMLElement): void {
  updateStop(root)
  root.addEventListener("focusin", onToolbarFocus)
  root.addEventListener("keydown", onToolbarKey)
}
