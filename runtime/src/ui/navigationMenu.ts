const triggerSelector = 'button[data-fleur-part="navigation-trigger"]'

function expandedTriggers(root: HTMLElement): NodeListOf<HTMLButtonElement> {
  return root.querySelectorAll<HTMLButtonElement>(
    `:scope > ul > li > ${triggerSelector}[aria-expanded="true"]`,
  )
}

function expandedTriggerFor(root: HTMLElement, target: Node): HTMLButtonElement | undefined {
  return Array.from(expandedTriggers(root)).find(trigger => trigger.parentElement?.contains(target))
}

function setExpanded(trigger: HTMLButtonElement, expanded: boolean): void {
  const links = trigger.nextElementSibling
  if (!(links instanceof HTMLElement)) return
  trigger.setAttribute("aria-expanded", String(expanded))
  links.hidden = !expanded
}

function onNavigationClick(event: MouseEvent): void {
  const root = event.currentTarget as HTMLElement
  if (event.defaultPrevented || !(event.target instanceof Element)) return
  if (event.target.closest('[data-fleur-ui="navigation-menu"]') !== root) return

  const trigger = event.target.closest<HTMLButtonElement>(triggerSelector)
  if (trigger) {
    const open = trigger.getAttribute("aria-expanded") === "true"
    if (!open && !root.hasAttribute("data-fleur-multiple")) {
      expandedTriggers(root).forEach(expanded => setExpanded(expanded, false))
    }
    setExpanded(trigger, !open)
    return
  }

  if (root.hasAttribute("data-fleur-keep-open")) return
  if (event.button !== 0 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return
  const link = event.target.closest<HTMLAnchorElement>("a[href]")
  if (!link || link.hasAttribute("download")) return
  if (link.target && link.target.toLowerCase() !== "_self") return
  const expanded = expandedTriggerFor(root, link)
  if (!expanded) return

  // Keep focus on a visible control until the link's native navigation takes over.
  if (link === root.ownerDocument.activeElement) expanded.focus({ preventScroll: true })
  setExpanded(expanded, false)
}

function onNavigationKeydown(event: KeyboardEvent): void {
  if (event.key !== "Escape" || event.defaultPrevented || !(event.target instanceof Node)) return
  const root = event.currentTarget as HTMLElement
  const expanded = root.hasAttribute("data-fleur-multiple")
    ? expandedTriggerFor(root, event.target)
    : expandedTriggers(root)[0]
  if (!expanded) return
  event.preventDefault()
  expanded.focus()
  setExpanded(expanded, false)
}

function onNavigationFocusout(event: FocusEvent): void {
  const root = event.currentTarget as HTMLElement
  if (root.hasAttribute("data-fleur-keep-open")) return
  if (event.relatedTarget instanceof Node && root.contains(event.relatedTarget)) return
  expandedTriggers(root).forEach(trigger => setExpanded(trigger, false))
}

export function attachNavigationMenu(root: HTMLElement): void {
  root.addEventListener("click", onNavigationClick)
  root.addEventListener("keydown", onNavigationKeydown)
  root.addEventListener("focusout", onNavigationFocusout)
}
