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
    || (oldV.type === VNodeType.ELEMENT && newV.type === VNodeType.ELEMENT && oldV.tag !== newV.tag)
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
    const oldKeyIndex = new Map<string | number, number>()
    for (let i = 0; i < oldElement.children.length; i++) {
      const key = getKey(oldElement.children[i])
      if (key != null) oldKeyIndex.set(key, i)
    }

    const used = new Set<number>()
    for (let i = 0; i < newElement.children.length; i++) {
      const newChild = newElement.children[i]
      const key = getKey(newChild)
      if (key != null && oldKeyIndex.has(key)) {
        const oldIndex = oldKeyIndex.get(key) as number
        used.add(oldIndex)
        patches.push(...diff(oldElement.children[oldIndex], newChild, [...path, i]))
        if (oldIndex !== i) {
          patches.push({ type: PatchType.MOVE, path: [...path, oldIndex], to: [...path, i] })
        }
      } else {
        patches.push({ type: PatchType.INSERT, path: [...path, i], vnode: newChild })
      }
    }

    for (let i = oldElement.children.length - 1; i >= 0; i--) {
      if (!used.has(i)) {
        patches.push({ type: PatchType.REMOVE, path: [...path, i] })
      }
    }
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
  for (const k in { ...oldElement.props, ...newElement.props }) {
    if (oldElement.props[k] !== newElement.props[k]) {
      propPatches[k] = newElement.props[k]
    }
  }
  if (Object.keys(propPatches).length > 0) {
    patches.push({ type: PatchType.PROPS, path, props: propPatches })
  }
  return patches
}
