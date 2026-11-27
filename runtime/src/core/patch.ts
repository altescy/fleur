import { Patch, PatchType } from "./types"
import { instantiate, removeProp, setProp } from "./dom"
import { disposeDomEffects } from "./domEffect"

export const getNode = (root: Node, path: number[]): Node | null => {
  let node: Node | null = root
  for (const i of path) {
    if (!node) return null
    node = node.childNodes[i] ?? null
  }
  return node
}

const moveChild = (parent: Node, node: Node, from: number, to: number): void => {
  const reference = parent.childNodes[to] ?? null
  const focused = node.ownerDocument?.activeElement
  if (node.parentNode !== parent || !focused || !node.contains(focused)) {
    parent.insertBefore(node, reference)
    return
  }

  const target = parent as Node & { moveBefore?: (child: Node, reference: Node | null) => void }
  if (typeof target.moveBefore === "function") {
    target.moveBefore(node, reference)
    return
  }

  // Keep the focused subtree connected by moving the siblings it crosses.
  const forward = from < to
  const boundary = forward ? reference : node
  const anchor = forward ? node : node.nextSibling
  let sibling = forward ? node.nextSibling : reference
  while (sibling && sibling !== boundary) {
    const next = sibling.nextSibling
    parent.insertBefore(sibling, anchor)
    sibling = next
  }
}

export const apply = (root: Node, patch: Patch): Node => {
  const node = getNode(root, patch.path)

  switch (patch.type) {
    case PatchType.INSERT: {
      const parent = getNode(root, patch.path.slice(0, -1)) as Node | null
      if (!parent) return root
      const insertedNode = instantiate(patch.vnode)
      if ((patch.path.at(-1) ?? 0) >= parent.childNodes.length) {
        parent.appendChild(insertedNode)
      } else {
        const refNode = parent.childNodes[patch.path.at(-1) ?? 0]
        parent.insertBefore(insertedNode, refNode)
      }
      return root
    }
    case PatchType.MOVE: {
      if (!node) return root
      const parentNode = getNode(root, patch.to.slice(0, -1))
      if (!parentNode) return root
      moveChild(parentNode, node, patch.path.at(-1) ?? 0, patch.to.at(-1) ?? 0)
      return root
    }
    case PatchType.REMOVE:
      if (!node) return root
      node.parentNode?.removeChild(node)
      disposeDomEffects(node)
      return root
    case PatchType.REPLACE: {
      if (!node) {
        const parent = getNode(root, patch.path.slice(0, -1)) as Node | null
        if (!parent) return root
        const replacedNode = instantiate(patch.vnode)
        const index = patch.path.at(-1) ?? 0
        const refNode = parent.childNodes[index] ?? null
        if (refNode) {
          parent.replaceChild(replacedNode, refNode)
          disposeDomEffects(refNode)
        } else {
          parent.appendChild(replacedNode)
        }
        return root
      }

      const replacedNode = instantiate(patch.vnode)
      const parent = node.parentNode
      if (!parent) return root
      parent.replaceChild(replacedNode, node)
      disposeDomEffects(node)
      return patch.path.length === 0 ? replacedNode : root
    }
    case PatchType.TEXT:
      if (!node) return root
      node.textContent = patch.value
      return root
    case PatchType.PROPS: {
      if (!node) return root
      const target = node as Element & { __handlers?: Record<string, EventListener>; __listeners?: Record<string, EventListener> }
      for (const [k, v] of Object.entries(patch.props)) {
        if (v == null || v === false) {
          removeProp(target, k)
        } else {
          setProp(target, k, v)
        }
      }
      return root
    }
    default:
      return root
  }
}

export const patch = (root: Node, patches: Patch[]): Node => {
  for (const p of patches) root = apply(root, p)
  return root
}
