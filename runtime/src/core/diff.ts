import { Patch, PatchType, VElement, VNode, VNodeType } from "./types"
import { resolveLazy, shallowArgsEqual } from "./vdom"

const getKey = (node: VNode): string | number | null => {
  if (node.type !== VNodeType.ELEMENT) return null
  const key = node.props.key
  if (typeof key === "string" || typeof key === "number") return key
  return null
}

export const diff = (oldV: VNode | undefined, newV: VNode | undefined, path: number[] = []): Patch[] => {
  if (oldV?.type === VNodeType.LAZY && newV?.type === VNodeType.LAZY) {
    if (oldV.fn === newV.fn && shallowArgsEqual(oldV.args, newV.args)) return []
    oldV = resolveLazy(oldV)
    newV = resolveLazy(newV)
  }

  if (oldV?.type === VNodeType.LAZY) oldV = resolveLazy(oldV)
  if (newV?.type === VNodeType.LAZY) newV = resolveLazy(newV)

  if (!oldV && newV) return [{ type: PatchType.REPLACE, path, vnode: newV }]
  if (oldV && !newV) return [{ type: PatchType.REMOVE, path }]
  if (!oldV || !newV) return []

  if (
    oldV.type !== newV.type
    || (oldV.type === VNodeType.ELEMENT && newV.type === VNodeType.ELEMENT
      && (oldV.tag !== newV.tag || oldV.props.fleurTabs !== newV.props.fleurTabs
        || oldV.props.fleurMenu !== newV.props.fleurMenu
        || (newV.props.fleurMenu && oldV.props["data-fleur-part"] !== newV.props["data-fleur-part"])
        || oldV.props.fleurTooltip !== newV.props.fleurTooltip
        || oldV.props.fleurPreviewCard !== newV.props.fleurPreviewCard
        || oldV.props.fleurCombobox !== newV.props.fleurCombobox
        || oldV.props.fleurToast !== newV.props.fleurToast
        || oldV.props.fleurAccordion !== newV.props.fleurAccordion
        || oldV.props.fleurToolbar !== newV.props.fleurToolbar
        || oldV.props.fleurMenubar !== newV.props.fleurMenubar
        || oldV.props.fleurAvatar !== newV.props.fleurAvatar
        || oldV.props.fleurNavigationMenu !== newV.props.fleurNavigationMenu
        || oldV.props.fleurNumberField !== newV.props.fleurNumberField
        || (newV.tag === "dialog" && oldV.props["data-fleur-ui"] !== newV.props["data-fleur-ui"])))
  ) {
    return [{ type: PatchType.REPLACE, path, vnode: newV }]
  }
  if (newV.type === VNodeType.TEXT && oldV.type === VNodeType.TEXT) {
    if (oldV.value !== newV.value) {
      return [{ type: PatchType.TEXT, path, value: newV.value }]
    }
    return []
  }

  const oldElement = oldV as VElement
  const newElement = newV as VElement
  const patches: Patch[] = []

  if (oldElement.children.some((c) => getKey(c) != null) || newElement.children.some((c) => getKey(c) != null)) {
    const keyed = new Map<string | number, number>()
    const unkeyed: number[] = []
    oldElement.children.forEach((child, index) => {
      const key = getKey(child)
      if (key === null) unkeyed.push(index)
      else keyed.set(key, index)
    })

    let unkeyedIndex = 0
    const used = new Set<number>()
    const matches = newElement.children.map((child) => {
      const key = getKey(child)
      const index = key === null ? unkeyed[unkeyedIndex++] : keyed.get(key)
      if (index === undefined || used.has(index)) return undefined
      used.add(index)
      return index
    })

    // Patch paths refer to the DOM after preceding patches have been applied.
    const order = oldElement.children.map((_, index) => index)
    for (let i = order.length - 1; i >= 0; i--) {
      if (!used.has(order[i])) {
        patches.push({ type: PatchType.REMOVE, path: [...path, i] })
        order.splice(i, 1)
      }
    }

    matches.forEach((oldIndex, index) => {
      const childPath = [...path, index]
      const newChild = newElement.children[index]
      if (oldIndex === undefined) {
        patches.push({ type: PatchType.INSERT, path: childPath, vnode: newChild })
        order.splice(index, 0, -1)
        return
      }
      const from = order.indexOf(oldIndex, index)
      if (from !== index) {
        patches.push({ type: PatchType.MOVE, path: [...path, from], to: childPath })
        order.splice(from, 1)
        order.splice(index, 0, oldIndex)
      }
      patches.push(...diff(oldElement.children[oldIndex], newChild, childPath))
    })
  } else {
    const sharedLen = Math.min(oldElement.children.length, newElement.children.length)
    for (let i = 0; i < sharedLen; i++) {
      patches.push(...diff(oldElement.children[i], newElement.children[i], [...path, i]))
    }

    for (let i = oldElement.children.length - 1; i >= newElement.children.length; i--) {
      patches.push({ type: PatchType.REMOVE, path: [...path, i] })
    }

    for (let i = oldElement.children.length; i < newElement.children.length; i++) {
      patches.push({ type: PatchType.INSERT, path: [...path, i], vnode: newElement.children[i] })
    }
  }

  const propPatches = {} as VElement["props"]
  if (newElement.props.fleurTabs && patches.length > 0) {
    propPatches.fleurTabs = true
  }
  // Changed options can reset the browser selection even when the model value is unchanged.
  if (newElement.tag === "select" && newElement.props.value != null && patches.length > 0) {
    propPatches.value = newElement.props.value
  }
  for (const k in { ...oldElement.props, ...newElement.props }) {
    if (oldElement.props[k] !== newElement.props[k]) {
      propPatches[k] = newElement.props[k]
    }
  }
  if (newElement.tag === "input" && newElement.props.type === "range") {
    const boundsChanged = "min" in propPatches || "max" in propPatches || "step" in propPatches || "type" in propPatches
    if ("value" in propPatches || (boundsChanged && newElement.props.value != null)) {
      // Let the browser clamp the value against the final bounds.
      delete propPatches.value
      propPatches.value = newElement.props.value
    }
  }
  if (patches.length > 0 || Object.keys(propPatches).length > 0) {
    if (newElement.props.fleurCombobox) propPatches.fleurCombobox = true
    if (newElement.props.fleurToast) propPatches.fleurToast = true
    if (newElement.props.fleurAccordion) propPatches.fleurAccordion = true
    if (newElement.props.fleurToolbar) propPatches.fleurToolbar = true
    if (newElement.props.fleurMenubar) propPatches.fleurMenubar = true
    if (newElement.props.fleurAvatar) propPatches.fleurAvatar = true
    if (newElement.props.fleurNumberField) propPatches.fleurNumberField = true
  }
  if (Object.keys(propPatches).length > 0) {
    patches.push({ type: PatchType.PROPS, path, props: propPatches })
  }
  return patches
}
