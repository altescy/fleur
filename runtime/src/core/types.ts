export type JsonPrimitive = string | number | boolean | null
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue }

export type Msg = { type: string; [key: string]: JsonValue | undefined }
export type Dispatch = (msg: Msg) => void

export type EventPayloadValue = string | number | boolean
export type EventPayload = { type: string } & Record<string, EventPayloadValue>

export type StyleValue = string | number | null | undefined
export type StyleProps = Record<string, StyleValue>
export type EventHandler = (payload: EventPayload, element: Element, event: Event) => Msg | null | void
export type RuntimeEventHandler = (payload: EventPayload, element: Element, event: Event) => void
export type DomEffectLifecycle = {
  update?: (...args: readonly JsonValue[]) => void
  dispose?: () => void
}
export type DomEffect = {
  key: string
  args: readonly JsonValue[]
  refresh?: boolean
  sync?: boolean
  mount?: (element: Element) => void
  dispose?: (element: Element) => void
  run: (element: Element, ...args: readonly JsonValue[]) => void | DomEffectLifecycle
}
export type VPropValue =
  | string | number | boolean | null | undefined | StyleProps | EventHandler | RuntimeEventHandler | DomEffect
export type VProps = Record<string, VPropValue>

export type VText = {
  type: "TEXT"
  value: string
  __isVNode: true
}

export type VElement = {
  type: "ELEMENT"
  tag: string
  props: VProps
  children: VNode[]
  __isVNode: true
}

export type VLazy = {
  type: "LAZY"
  fn: (...args: readonly unknown[]) => VNodeLike
  args: readonly unknown[]
  vnode: VNode | null
  __isVNode: true
}

export type VNode = VText | VElement | VLazy
export type VNodeLike = VNode | string | number | boolean | null | undefined

export type Patch =
  | { type: "REPLACE"; path: number[]; vnode: VNode }
  | { type: "TEXT"; path: number[]; value: string }
  | { type: "PROPS"; path: number[]; props: VProps }
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
