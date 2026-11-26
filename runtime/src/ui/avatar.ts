const synchronize = new WeakMap<HTMLElement, () => void>()

export function syncAvatar(root: HTMLElement): void {
  const existing = synchronize.get(root)
  if (existing) {
    existing()
    return
  }

  const [fallback, image] = Array.from(root.children)
  if (!(fallback instanceof HTMLElement) || !(image instanceof HTMLImageElement)) return
  const sync = (): void => {
    // An image can retain the previous request's currentSrc while its replacement loads.
    const loaded = !!image.getAttribute("src") && image.complete && image.naturalWidth > 0 && image.currentSrc === image.src
    if (image.hidden === loaded) image.hidden = !loaded
    if (fallback.hidden !== loaded) fallback.hidden = loaded
  }
  image.addEventListener("load", sync)
  image.addEventListener("error", sync)
  synchronize.set(root, sync)
  sync()
}
