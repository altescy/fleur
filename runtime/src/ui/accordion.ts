const groupNames = new WeakMap<HTMLElement, string>()

function accordionItems(root: HTMLElement): HTMLDetailsElement[] {
  return Array.from(root.querySelectorAll<HTMLDetailsElement>(':scope > details[data-fleur-part="accordion-item"]'))
}

function onAccordionKey(event: KeyboardEvent): void {
  if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return
  const root = event.currentTarget as HTMLElement
  const summaries = accordionItems(root)
    .filter(item => !item.hidden)
    .map(item => item.firstElementChild as HTMLElement)
  const index = summaries.findIndex(summary => summary === event.target)
  if (index < 0) return

  let next: number
  switch (event.key) {
    case "ArrowDown":
      next = (index + 1) % summaries.length
      break
    case "ArrowUp":
      next = (index + summaries.length - 1) % summaries.length
      break
    case "Home":
      next = 0
      break
    case "End":
      next = summaries.length - 1
      break
    default:
      return
  }
  event.preventDefault()
  summaries[next].focus()
}

export function syncAccordion(root: HTMLElement): void {
  let name = groupNames.get(root)
  if (!name) {
    name = `fleur-accordion-${crypto.getRandomValues(new Uint32Array(4)).join("-")}`
    groupNames.set(root, name)
    root.addEventListener("keydown", onAccordionKey)
  }
  // A details name is document-wide, including across two instances of the same view.
  for (const item of accordionItems(root)) {
    if (item.getAttribute("name") !== name) item.setAttribute("name", name)
  }
}
