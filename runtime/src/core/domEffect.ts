import { DomEventOrigin, domEventOrigin, withDomEventOrigin } from "./events"
import { DomEffect, DomEffectLifecycle, VPropValue } from "./types"

type PendingEffect = { effect: DomEffect; origin?: DomEventOrigin }
type InstalledEffect = { key: string; lifecycle?: DomEffectLifecycle; dispose?: () => void }
type EffectSlot = { pending?: PendingEffect; active?: InstalledEffect }

const slotsByNode = new WeakMap<Node, Map<string, EffectSlot>>()

export const isDomEffectProp = (name: string): boolean => name === "domEffect" || name.startsWith("domEffect:")

export const isDomEffect = (value: VPropValue): value is DomEffect =>
  typeof value === "object" && value !== null
  && "key" in value && typeof value.key === "string"
  && "args" in value && Array.isArray(value.args)
  && "run" in value && typeof value.run === "function"

function runDomEffect(element: Element, slot: EffectSlot, effect: DomEffect): void {
  if (slot.active?.key !== effect.key) {
    const previous = slot.active
    slot.active = undefined
    previous?.dispose?.()
  }
  if (slot.active?.lifecycle) {
    slot.active.lifecycle.update?.(...effect.args)
    return
  }
  const dispose = effect.dispose?.bind(null, element)
  const mounted = slot.active !== undefined
  const active: InstalledEffect = { key: effect.key, dispose }
  slot.active = active
  if (!mounted) effect.mount?.(element)
  if (slot.active !== active) return

  const lifecycle = effect.run(element, ...effect.args)
  if (!lifecycle) return
  if (slot.active !== active) {
    // A setup action can dispatch an event that detaches this effect.
    lifecycle.dispose?.()
    return
  }
  active.lifecycle = lifecycle
  active.dispose = lifecycle.dispose?.bind(lifecycle) ?? dispose
  lifecycle.update?.(...effect.args)
}

export function scheduleDomEffect(element: Element, name: string, effect: DomEffect): void {
  let slots = slotsByNode.get(element)
  if (!slots) {
    slots = new Map()
    slotsByNode.set(element, slots)
  }
  let slot = slots.get(name)
  if (!slot) {
    slot = {}
    slots.set(name, slot)
  }

  if (effect.sync) {
    slot.pending = undefined
    runDomEffect(element, slot, effect)
    return
  }
  const origin = domEventOrigin()
  if (slot.pending) {
    slot.pending.effect = effect
    slot.pending.origin = origin
    return
  }
  const pending = { effect, origin }
  const scheduled = slot
  scheduled.pending = pending

  queueMicrotask(() => {
    if (scheduled.pending !== pending) return
    scheduled.pending = undefined
    if (element.isConnected) {
      withDomEventOrigin(pending.origin, () => runDomEffect(element, scheduled, pending.effect))
    }
  })
}

function disposeSlot(slot: EffectSlot): void {
  slot.pending = undefined
  const active = slot.active
  slot.active = undefined
  active?.dispose?.()
}

export function cancelDomEffect(node: Node, name: string): void {
  const slots = slotsByNode.get(node)
  const slot = slots?.get(name)
  if (!slots || !slot) return
  slots.delete(name)
  if (slots.size === 0) slotsByNode.delete(node)
  disposeSlot(slot)
}

export function disposeDomEffects(node: Node): void {
  const slots = slotsByNode.get(node)
  slotsByNode.delete(node)
  slots?.forEach(disposeSlot)
  node.childNodes.forEach(disposeDomEffects)
}
