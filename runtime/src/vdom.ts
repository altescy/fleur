import { Dispatch, Msg, VElement, VLazy, VNode, VNodeType, VText } from "./types"

export const shallowArgsEqual = (a: unknown[], b: unknown[]): boolean => {
  if (a.length !== b.length) return false
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false
  }
  return true
}

export const isVNode = (v: unknown): v is VNode => v != null && typeof v === "object" && "__isVNode" in v

export const text = (value: unknown): VText => ({ type: VNodeType.TEXT, value: String(value), __isVNode: true })
export const asVNode = (value: unknown): VNode => (isVNode(value) ? value : text(value))

export const h = (tag: string, props: Record<string, unknown> = {}, ...children: unknown[]): VElement => ({
  type: VNodeType.ELEMENT,
  tag,
  props,
  children: children.flat().map(asVNode),
  __isVNode: true,
})

export const lazy = (fn: (...args: unknown[]) => unknown, ...args: unknown[]): VLazy => ({
  type: VNodeType.LAZY,
  fn,
  args,
  vnode: null,
  __isVNode: true,
})

export const wrapDispatch = (dispatch: Dispatch, vnode: VNode): VNode => {
  switch (vnode.type) {
    case VNodeType.LAZY:
      return { ...vnode, fn: (...args: unknown[]) => wrapDispatch(dispatch, asVNode(vnode.fn(...args))) }
    case VNodeType.ELEMENT: {
      const newProps: Record<string, unknown> = {}
      for (const [k, v] of Object.entries(vnode.props || {})) {
        newProps[k] = k.startsWith("on") && typeof v === "function" ? (...args: unknown[]) => dispatch((v as (...args: unknown[]) => Msg)(...args)) : v
      }
      const newChildren = vnode.children.map((c) => wrapDispatch(dispatch, c))
      return { ...vnode, props: newProps, children: newChildren }
    }
    default:
      return vnode
  }
}

export const resolveLazy = (vnode: VNode): VNode => {
  if (vnode.type !== VNodeType.LAZY) return vnode
  if (!vnode.vnode) vnode.vnode = asVNode(vnode.fn(...vnode.args))
  return vnode.vnode
}
