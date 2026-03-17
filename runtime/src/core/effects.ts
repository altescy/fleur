import { Dispatch, Msg, Subscription, VNode } from "./types"
import { wrapDispatch } from "./vdom"

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

export { Cmd, Html, Sub }
