const synchronize = new WeakMap<HTMLElement, () => void>()

export function syncNumberField(root: HTMLElement): void {
  const existing = synchronize.get(root)
  if (existing) {
    existing()
    return
  }

  const [input, decrease, increase] = Array.from(root.children)
  if (!(input instanceof HTMLInputElement) || !(decrease instanceof HTMLButtonElement)
    || !(increase instanceof HTMLButtonElement)) return
  const controls = [[decrease, "stepDown"], [increase, "stepUp"]] as const

  const sync = (): void => {
    const disabled = input.disabled || input.readOnly || input.step === "any"
    for (const [button] of controls) {
      if (button.disabled !== disabled) button.disabled = disabled
    }
    if (disabled) return

    // Ask the browser whether each step would change the value, including off-step bounds.
    const probe = input.cloneNode() as HTMLInputElement
    for (const [button, step] of controls) {
      probe.value = input.value
      probe[step]()
      const blocked = String(input.value === probe.value)
      if (button.getAttribute("aria-disabled") !== blocked) button.setAttribute("aria-disabled", blocked)
    }
  }

  for (const [button, step] of controls) {
    button.addEventListener("click", () => {
      if (input.matches(":disabled") || input.readOnly || input.step === "any") return
      const before = input.value
      input[step]()
      if (input.value === before) return
      input.dispatchEvent(new Event("input", { bubbles: true }))
      input.dispatchEvent(new Event("change", { bubbles: true }))
    })
  }
  input.addEventListener("input", sync)
  synchronize.set(root, sync)
  sync()
}
