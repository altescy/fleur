import { Cmd, Html, Sub } from "./core/effects"
import { Http } from "./http/client"
import { h, lazy } from "./core/vdom"
import { program } from "./core/program"

const fleurRuntime = {
  h,
  lazy,
  Cmd,
  Sub,
  Html,
  Http,
  program,
}

Object.assign(globalThis, {
  __fleur: fleurRuntime,
})

export { Cmd, Html, Http, Sub, h, lazy, program }
