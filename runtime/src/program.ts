import { Cmd, Sub } from "./effects"
import { diff } from "./diff"
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

export { program }
