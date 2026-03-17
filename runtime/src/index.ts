import { Cmd, Html, Sub } from "./core/effects"
import { h, lazy } from "./core/vdom"
import { program } from "./core/program"

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
