import { Patch, PatchType } from "./types"
import { instantiate, removeProp, setProp } from "./dom"

export const getNode = (root: Node, path: number[]): Node | null => {
  let node: Node | null = root
  for (const i of path) {
    if (!node) return null
    node = node.childNodes[i] ?? null
  }
  return node
}

export const apply = (root: Node, patch: Patch): Node => {
  const node = getNode(root, patch.path)
  if (!node) return root

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
      const parentNode = getNode(root, patch.to.slice(0, -1))
      if (!parentNode) return root
      const refNode = parentNode.childNodes[patch.to.at(-1) ?? 0]
      parentNode.insertBefore(node, refNode ?? null)
      return root
    }
    case PatchType.REMOVE:
      node.parentNode?.removeChild(node)
      return root
    case PatchType.REPLACE: {
      const replacedNode = instantiate(patch.vnode)
      const parent = node.parentNode
      if (!parent) return root
      parent.replaceChild(replacedNode, node)
      return replacedNode
    }
    case PatchType.TEXT:
      node.textContent = patch.value
      return root
    case PatchType.PROPS: {
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
