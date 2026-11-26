import { Dispatch, EventHandler, Msg, StyleProps, VElement, VLazy, VNode, VNodeLike, VNodeType, VProps, VText } from "./types"

export const shallowArgsEqual = (a: readonly unknown[], b: readonly unknown[]): boolean => {
  if (a.length !== b.length) return false
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false
  }
  return true
}

export const isVNode = (v: VNodeLike): v is VNode => v != null && typeof v === "object" && "__isVNode" in v

export const text = (value: VNodeLike): VText => ({ type: VNodeType.TEXT, value: String(value ?? ""), __isVNode: true })
export const asVNode = (value: VNodeLike): VNode => (isVNode(value) ? value : text(value))

const flattenChildren = (children: readonly VNodeLike[]): VNodeLike[] =>
  children.flatMap((child) => (Array.isArray(child) ? flattenChildren(child as readonly VNodeLike[]) : [child]))

export const h = (tag: string, props: VProps = {}, ...children: VNodeLike[]): VElement => ({
  type: VNodeType.ELEMENT,
  tag,
  props,
  children: flattenChildren(children).map(asVNode),
  __isVNode: true,
})

export const mergeStyleProps = (props: VProps, defaults: StyleProps, overrides: StyleProps): VProps => {
  const style: StyleProps = Object.create(null)
  const supplied = props.style
  for (const layer of [defaults, supplied, overrides]) {
    if (!layer || typeof layer !== "object" || Array.isArray(layer)) continue
    for (const [key, value] of Object.entries(layer)) {
      // DOM applies declarations in this order, including CSS shorthands and longhands.
      delete style[key]
      style[key] = value
    }
  }
  return { ...props, style }
}

export const lazy = (fn: (...args: readonly unknown[]) => VNodeLike, ...args: readonly unknown[]): VLazy => ({
  type: VNodeType.LAZY,
  fn,
  args,
  vnode: null,
  __isVNode: true,
})

export const wrapDispatch = (dispatch: Dispatch, vnode: VNode): VNode => {
  switch (vnode.type) {
    case VNodeType.LAZY:
      return { ...vnode, fn: (...args: readonly unknown[]) => wrapDispatch(dispatch, asVNode(vnode.fn(...args))) }
    case VNodeType.ELEMENT: {
      const newProps: VProps = {}
      for (const [k, v] of Object.entries(vnode.props || {})) {
        if (k.startsWith("on") && typeof v === "function") {
          const handler = v as EventHandler
          newProps[k] = (payload) => dispatch(handler(payload))
          continue
        }
        newProps[k] = v
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
