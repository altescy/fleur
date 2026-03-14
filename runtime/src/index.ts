type Msg = { type: string; [key: string]: unknown }
type Dispatch = (msg: Msg) => void

type VText = {
  type: "TEXT"
  value: string
  __isVNode: true
}

type VElement = {
  type: "ELEMENT"
  tag: string
  props: Record<string, unknown>
  children: VNode[]
  __isVNode: true
}

type VLazy = {
  type: "LAZY"
  fn: (...args: unknown[]) => unknown
  args: unknown[]
  vnode: VNode | null
  __isVNode: true
}

type VNode = VText | VElement | VLazy

type Patch =
  | { type: "REPLACE"; path: number[]; vnode: VNode }
  | { type: "TEXT"; path: number[]; value: string }
  | { type: "PROPS"; path: number[]; props: Record<string, unknown> }
  | { type: "INSERT"; path: number[]; vnode: VNode }
  | { type: "MOVE"; path: number[]; to: number[] }
  | { type: "REMOVE"; path: number[] }

type Subscription = {
  key: string
  start: (dispatch: Dispatch) => () => void
}

type RuntimeComponent<Model> = {
  init: () => [Model, (dispatch: Dispatch) => void]
  update: (model: Model, message: Msg) => [Model, (dispatch: Dispatch) => void]
  view: (model: Model) => VNode
  subscriptions?: (model: Model) => Subscription[]
}

const shallowArgsEqual = (a: unknown[], b: unknown[]): boolean => {
  if (a.length !== b.length) return false
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false
  }
  return true
}

const VNodeType = {
  TEXT: "TEXT",
  ELEMENT: "ELEMENT",
  LAZY: "LAZY",
} as const

const isVNode = (v: unknown): v is VNode => v != null && typeof v === "object" && "__isVNode" in v

const text = (value: unknown): VText => ({ type: VNodeType.TEXT, value: String(value), __isVNode: true })
const asvnode = (value: unknown): VNode => (isVNode(value) ? value : text(value))

const h = (tag: string, props: Record<string, unknown> = {}, ...children: unknown[]): VElement => ({
  type: VNodeType.ELEMENT,
  tag,
  props,
  children: children.flat().map(asvnode),
  __isVNode: true,
})

const lazy = (fn: (...args: unknown[]) => unknown, ...args: unknown[]): VLazy => ({
  type: VNodeType.LAZY,
  fn,
  args,
  vnode: null,
  __isVNode: true,
})

const wrapDispatch = (dispatch: Dispatch, vnode: VNode): VNode => {
  switch (vnode.type) {
    case VNodeType.LAZY:
      return { ...vnode, fn: (...args: unknown[]) => wrapDispatch(dispatch, asvnode(vnode.fn(...args))) }
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

const setProp = (el: Element & { __listeners?: Record<string, EventListener> }, key: string, value: unknown): void => {
  if (key === "className") {
    el.setAttribute("class", String(value))
    return
  }

  if (key === "style" && value && typeof value === "object") {
    const style = el as HTMLElement
    for (const [styleKey, styleValue] of Object.entries(value as Record<string, unknown>)) {
      if (styleValue == null) continue
      style.style.setProperty(styleKey, String(styleValue))
    }
    return
  }

  if (key.startsWith("on") && typeof value === "function") {
    const type = key.slice(2).toLowerCase()
    if (el.__listeners?.[key]) el.removeEventListener(type, el.__listeners[key])
    const listener = value as EventListener
    el.addEventListener(type, listener)
    el.__listeners = { ...el.__listeners, [key]: listener }
  } else if (value) {
    el.setAttribute(key, String(value))
  }
}

const removeProp = (el: Element & { __handlers?: Record<string, EventListener> }, key: string): void => {
  if (key === "className") {
    el.removeAttribute("class")
    return
  }

  if (key === "style") {
    ;(el as HTMLElement).removeAttribute("style")
    return
  }

  if (key.startsWith("on")) {
    const type = key.slice(2).toLowerCase()
    const handler = el.__handlers?.[type]
    if (handler) el.removeEventListener(type, handler)
  } else {
    el.removeAttribute(key)
  }
}

const resolveLazy = (vnode: VNode): VNode => {
  if (vnode.type !== VNodeType.LAZY) return vnode
  if (!vnode.vnode) vnode.vnode = asvnode(vnode.fn(...vnode.args))
  return vnode.vnode
}

const instantiate = (vnode: VNode): Node => {
  const resolved = resolveLazy(vnode)
  switch (resolved.type) {
    case VNodeType.TEXT:
      return document.createTextNode(resolved.value)
    case VNodeType.ELEMENT: {
      const el = document.createElement(resolved.tag)
      for (const [k, v] of Object.entries(resolved.props || {})) {
        setProp(el, k, v)
      }
      resolved.children
        .map(resolveLazy)
        .map(asvnode)
        .map(instantiate)
        .forEach((c) => el.appendChild(c))
      return el
    }
    default:
      throw new Error("Unknown vnode type")
  }
}

const PatchType = {
  REPLACE: "REPLACE",
  TEXT: "TEXT",
  PROPS: "PROPS",
  INSERT: "INSERT",
  MOVE: "MOVE",
  REMOVE: "REMOVE",
} as const

const diff = (oldV: VNode | undefined, newV: VNode | undefined, path: number[] = []): Patch[] => {
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

  if (oldElement.children.some((c) => (c as VElement)?.props?.key != null) || newElement.children.some((c) => (c as VElement)?.props?.key != null)) {
    const oldKeyIndex = new Map<unknown, number>()
    for (let i = 0; i < oldElement.children.length; i++) {
      const key = (oldElement.children[i] as VElement)?.props?.key
      if (key != null) oldKeyIndex.set(key, i)
    }

    const used = new Set<number>()
    for (let i = 0; i < newElement.children.length; i++) {
      const newChild = newElement.children[i]
      const key = (newChild as VElement)?.props?.key
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

    for (let i = 0; i < oldElement.children.length; i++) {
      if (!used.has(i)) {
        patches.push({ type: PatchType.REMOVE, path: [...path, i] })
      }
    }
  } else {
    const maxLen = Math.max(oldElement.children.length, newElement.children.length)
    for (let i = 0; i < maxLen; i++) {
      patches.push(...diff(oldElement.children[i], newElement.children[i], [...path, i]))
    }
  }

  const propPatches: Record<string, unknown> = {}
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

const getNode = (root: Node, path: number[]): Node | null => {
  let node: Node | null = root
  for (const i of path) {
    if (!node) return null
    node = node.childNodes[i] ?? null
  }
  return node
}

const apply = (root: Node, patch: Patch): Node => {
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

const patch = (root: Node, patches: Patch[]): Node => {
  for (const p of patches) root = apply(root, p)
  return root
}

const Cmd = {
  none: (): ((dispatch: Dispatch) => void) => () => {},
  batch:
    (cmds: Array<(dispatch: Dispatch) => void>) =>
    (dispatch: Dispatch): void => {
      for (const c of cmds) c(dispatch)
    },
  map:
    (tagger: (msg: Msg) => Msg, cmd: (dispatch: Dispatch) => void) =>
    (dispatch: Dispatch): void =>
      cmd((m) => dispatch(tagger(m))),
  task:
    (fn: () => Promise<unknown>, ok: (value: unknown) => Msg, err: (error: unknown) => Msg) =>
    (dispatch: Dispatch): void => {
      fn()
        .then((v) => dispatch(ok(v)))
        .catch((e) => dispatch(err(e)))
    },
}

const Sub = {
  none: (): Subscription[] => [],
  batch: (subs: Subscription[][]): Subscription[] => subs.flat(),
  map: (tagger: (msg: Msg) => Msg, subs: Subscription[]): Subscription[] =>
    subs.map((s) => ({
      key: s.key,
      start(dispatch: Dispatch): () => void {
        return s.start((m) => dispatch(tagger(m)))
      },
    })),
  interval: (key: string, ms: number, tagger: (time: number) => Msg): Subscription[] => [
    {
      key,
      start(dispatch: Dispatch): () => void {
        const id = setInterval(() => dispatch(tagger(Date.now())), ms)
        return () => clearInterval(id)
      },
    },
  ],
}

const Html = {
  map: (fn: (msg: Msg) => Msg, vnode: VNode): VNode => wrapDispatch((m) => fn(m), vnode),
}

const program =
  <Model,>({ init, update, view, subscriptions = () => Sub.none() }: RuntimeComponent<Model>) =>
  (mountEl: HTMLElement): void => {
    let model: Model
    let vnode: VNode | undefined
    let root: Node = document.createComment("root")

    const activeSubs = new Map<string, () => void>()

    const queue: Msg[] = []
    let running = false

    const dispatch: Dispatch = (msg) => {
      queue.push(msg)
      process()
    }

    const process = (): void => {
      if (running) return
      running = true

      while (queue.length) {
        const msg = queue.shift() as Msg
        const [m, cmd] = update(model, msg)
        model = m
        render()
        refreshSubs()
        runCmd(cmd)
      }

      running = false
    }

    const runCmd = (cmd: (dispatch: Dispatch) => void): void => cmd(dispatch)

    const refreshSubs = (): void => {
      const next = new Map<string, Subscription>()
      for (const s of subscriptions(model)) next.set(s.key, s)
      for (const [k, u] of activeSubs) {
        if (!next.has(k)) {
          u()
          activeSubs.delete(k)
        }
      }

      for (const [k, s] of next) {
        if (!activeSubs.has(k)) {
          const unsub = s.start(dispatch)
          activeSubs.set(k, unsub)
        }
      }
    }

    const render = (): void => {
      const newVNode = wrapDispatch(dispatch, view(model))
      const patches = diff(vnode, newVNode)
      if (patches.length > 0) {
        root = patch(root, patches)
        vnode = newVNode
      }
    }

    const [m0, c0] = init()
    model = m0
    mountEl.appendChild(root)

    render()
    refreshSubs()
    runCmd(c0)
  }

const fleurRuntime = {
  h,
  lazy,
  Cmd,
  Sub,
  Html,
  program,
}

Object.assign(globalThis, {
  __fleur: fleurRuntime,
})

export { Cmd, Html, Sub, h, lazy, program }
