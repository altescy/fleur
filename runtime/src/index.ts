import { sortBy } from "./core/array"
import { Dom } from "./core/domAccess"
import { Cmd, Html, Sub } from "./core/effects"
import { Http } from "./http/client"
import { h, lazy, mergeStyleProps } from "./core/vdom"
import { program } from "./core/program"

const fleurRuntime = {
  h,
  lazy,
  mergeStyleProps,
  sortBy,
  Dom,
  Cmd,
  Sub,
  Html,
  Http,
  program,
}

Object.assign(globalThis, {
  __fleur: fleurRuntime,
})

export { Cmd, Dom, Html, Http, Sub, h, lazy, mergeStyleProps, program, sortBy }
