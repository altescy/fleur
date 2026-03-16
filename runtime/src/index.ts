import { Cmd, Html, Sub } from "./effects"
import { h, lazy } from "./vdom"
import { program } from "./program"

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
