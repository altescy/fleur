import { Cmd, Sub } from "./effects"
import { diff } from "./diff"
import { DomEventOrigin, domEventOrigin, withDomEventOrigin } from "./events"
import { patch } from "./patch"
import { Dispatch, Msg, RuntimeComponent, Subscription, VNode } from "./types"
import { wrapDispatch } from "./vdom"

const program =
  <Model,>({ init, update, view, subscriptions = () => Sub.none() }: RuntimeComponent<Model>) =>
  (mountEl: HTMLElement): void => {
    let model: Model
    let vnode: VNode | undefined
    let root: Node = document.createComment("root")

    const activeSubs = new Map<string, () => void>()

    const queue: { message: Msg; origin?: DomEventOrigin }[] = []
    let running = false

    const dispatch: Dispatch = (msg) => {
      queue.push({ message: msg, origin: domEventOrigin() })
      process()
    }

    const process = (): void => {
      if (running) return
      running = true

      try {
        for (let next = queue.shift(); next; next = queue.shift()) {
          const { message, origin } = next
          withDomEventOrigin(origin, () => {
            const [m, cmd] = update(model, message)
            model = m
            render()
            refreshSubs()
            runCmd(cmd)
          })
        }
      } finally {
        running = false
      }
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

export { program }
