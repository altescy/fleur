import { enableAnchoredPopover } from "./popover"

const synchronize = new WeakMap<HTMLElement, () => void>()
const optionSelector = '[role="option"]'

function searchText(value: string): string {
  return value.normalize("NFKC").toLowerCase().trim()
}

export function syncCombobox(root: HTMLElement): void {
  const existing = synchronize.get(root)
  if (existing) {
    existing()
    return
  }
  const [, input, popup] = Array.from(root.children)
  if (!(input instanceof HTMLInputElement) || !(popup instanceof HTMLElement)) return
  const [list, empty] = Array.from(popup.children)
  if (!(list instanceof HTMLElement) || !(empty instanceof HTMLElement)) return
  const anchored = enableAnchoredPopover(popup)

  let open = false
  let composing = false
  let query: string | null = null
  let matches: HTMLElement[] = []
  let active: HTMLElement | undefined

  const setActive = (option?: HTMLElement): void => {
    if (active !== option) active?.removeAttribute("data-fleur-active")
    active = option
    if (option) {
      if (!option.hasAttribute("data-fleur-active")) option.setAttribute("data-fleur-active", "")
      if (input.getAttribute("aria-activedescendant") !== option.id) {
        input.setAttribute("aria-activedescendant", option.id)
      }
    } else {
      input.removeAttribute("aria-activedescendant")
    }
  }

  const sync = (): void => {
    if (input.disabled) {
      open = false
      query = null
    }
    const selected = root.getAttribute("data-fleur-value")
    const filter = searchText(query ?? "")
    let selectedLabel = ""
    matches = []
    list.querySelectorAll<HTMLElement>(optionSelector).forEach((option, index) => {
      const id = `${list.id}-option-${index}`
      if (option.id !== id) option.id = id
      const label = option.textContent ?? ""
      const chosen = option.getAttribute("data-fleur-value") === selected
      if (chosen) selectedLabel = label
      if (option.getAttribute("aria-selected") !== String(chosen)) {
        option.setAttribute("aria-selected", String(chosen))
      }
      const match = searchText(label).includes(filter)
      if (option.hidden === match) option.hidden = !match
      if (match) matches.push(option)
    })
    if (query === null && input.value !== selectedLabel) input.value = selectedLabel
    if (active && (!open || !matches.includes(active))) setActive()
    else if (active) setActive(active)
    const noMatches = matches.length === 0
    if (empty.hidden === noMatches) empty.hidden = !noMatches
    if (popup.hidden === open) {
      popup.hidden = !open
      if (anchored) popup.togglePopover(open)
      input.setAttribute("aria-expanded", String(open))
    }
  }

  const close = (): void => {
    open = false
    composing = false
    query = null
    setActive()
    sync()
  }

  input.addEventListener("click", () => {
    if (open || input.disabled) return
    open = true
    sync()
  })
  input.addEventListener("input", () => {
    query = input.value
    open = true
    setActive()
    sync()
  }, true)
  input.addEventListener("compositionstart", () => { composing = true })
  input.addEventListener("compositionend", () => { composing = false })
  input.addEventListener("blur", close)
  input.addEventListener("keydown", event => {
    if (event.defaultPrevented || event.isComposing || composing || event.keyCode === 229) return
    if (event.key === "Escape" && open) {
      event.preventDefault()
      close()
    } else if (event.key === "Enter" && open) {
      event.preventDefault()
      active?.click()
    } else if (!event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey
      && (event.key === "ArrowDown" || event.key === "ArrowUp")) {
      event.preventDefault()
      if (!open) {
        open = true
        sync()
      }
      const forward = event.key === "ArrowDown"
      const index = active ? matches.indexOf(active) : forward ? -1 : matches.length
      const option = matches[Math.max(0, Math.min(index + (forward ? 1 : -1), matches.length - 1))]
      setActive(option)
      option?.scrollIntoView({ block: "nearest" })
    }
  })
  const clickedOption = (event: MouseEvent): HTMLElement | null =>
    event.target instanceof HTMLElement ? event.target.closest(optionSelector) : null
  list.addEventListener("mousedown", event => {
    if (event.button === 0 && clickedOption(event)) event.preventDefault()
  })
  list.addEventListener("click", event => {
    if (!clickedOption(event)) return
    // Close before the option's handler dispatches the new selection to the model.
    close()
    input.focus({ preventScroll: true })
  }, true)

  synchronize.set(root, sync)
  sync()
}
