function setTabStop(list: Element, focus: EventTarget | null): void {
  const tabs = Array.from(list.children) as HTMLElement[]
  const stop = focus instanceof HTMLElement && focus.parentElement === list
    ? focus
    : tabs.find(tab => tab.getAttribute("aria-selected") === "true") ?? tabs[0]
  for (const tab of tabs) {
    const index = tab === stop ? 0 : -1
    if (tab.tabIndex !== index) tab.tabIndex = index
  }
}

function onTabFocus(event: FocusEvent): void {
  const list = event.currentTarget as HTMLElement
  setTabStop(list, event.type === "focusin" ? event.target : event.relatedTarget)
}

function onTabKey(event: KeyboardEvent): void {
  const list = event.currentTarget as HTMLElement
  const tab = event.target
  if (!(tab instanceof HTMLElement) || tab.parentElement !== list || event.altKey || event.ctrlKey || event.metaKey) {
    return
  }

  let next: Element | null
  switch (event.key) {
    case "ArrowLeft":
    case "ArrowRight": {
      const forward = (event.key === "ArrowRight") !== (getComputedStyle(list).direction === "rtl")
      next = forward
        ? tab.nextElementSibling ?? list.firstElementChild
        : tab.previousElementSibling ?? list.lastElementChild
      break
    }
    case "Home":
      next = list.firstElementChild
      break
    case "End":
      next = list.lastElementChild
      break
    default:
      return
  }
  event.preventDefault()
  if (next instanceof HTMLElement) next.focus()
}

// The factory emits a list followed by its keyed panels in the same order.
// Link actual DOM instances so a repeated view also gets distinct, stable IDs.
export function syncTabs(root: Element): void {
  const list = root.firstElementChild
  if (!(list instanceof HTMLElement)) return
  for (let i = 0; i < list.children.length; i++) {
    const tab = list.children[i]
    const panel = root.children[i + 1]
    if (!panel) continue
    if (!tab.id) tab.id = `fleur-tab-${crypto.getRandomValues(new Uint32Array(4)).join("-")}`
    if (!panel.id) panel.id = `${tab.id}-panel`
    if (tab.getAttribute("aria-controls") !== panel.id) tab.setAttribute("aria-controls", panel.id)
    if (panel.getAttribute("aria-labelledby") !== tab.id) panel.setAttribute("aria-labelledby", tab.id)
  }
  setTabStop(list, list.ownerDocument.activeElement)
  list.addEventListener("keydown", onTabKey)
  list.addEventListener("focusin", onTabFocus)
  list.addEventListener("focusout", onTabFocus)
}
