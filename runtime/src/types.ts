export type Msg = { type: string; [key: string]: unknown }
export type Dispatch = (msg: Msg) => void

export type VText = {
  type: "TEXT"
  value: string
  __isVNode: true
}

export type VElement = {
  type: "ELEMENT"
  tag: string
  props: Record<string, unknown>
  children: VNode[]
  __isVNode: true
}

export type VLazy = {
  type: "LAZY"
  fn: (...args: unknown[]) => unknown
  args: unknown[]
  vnode: VNode | null
  __isVNode: true
}

export type VNode = VText | VElement | VLazy

export type Patch =
  | { type: "REPLACE"; path: number[]; vnode: VNode }
  | { type: "TEXT"; path: number[]; value: string }
  | { type: "PROPS"; path: number[]; props: Record<string, unknown> }
  | { type: "INSERT"; path: number[]; vnode: VNode }
  | { type: "MOVE"; path: number[]; to: number[] }
  | { type: "REMOVE"; path: number[] }

export type Subscription = {
  key: string
  start: (dispatch: Dispatch) => () => void
}

export type RuntimeComponent<Model> = {
  init: () => [Model, (dispatch: Dispatch) => void]
  update: (model: Model, message: Msg) => [Model, (dispatch: Dispatch) => void]
  view: (model: Model) => VNode
  subscriptions?: (model: Model) => Subscription[]
}

export const VNodeType = {
  TEXT: "TEXT",
  ELEMENT: "ELEMENT",
  LAZY: "LAZY",
} as const

export const PatchType = {
  REPLACE: "REPLACE",
  TEXT: "TEXT",
  PROPS: "PROPS",
  INSERT: "INSERT",
  MOVE: "MOVE",
  REMOVE: "REMOVE",
} as const
