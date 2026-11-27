import { expect, test } from "bun:test"
import { Html } from "../../src/core/effects"
import { EventHandler, Msg, RuntimeEventHandler, VElement } from "../../src/core/types"
import { h, mergeStyleProps, wrapDispatch } from "../../src/core/vdom"

test("overlaid declarations move to the end without mutating shared props or defaults", () => {
  const defaults = Object.freeze({ padding: "0", color: "black" })
  const supplied = Object.freeze({ "padding-left": "1px", opacity: 0, padding: "2px" })
  const onclick = () => ({ type: "CLICK" })
  const props = Object.freeze({ className: "user", onclick, style: supplied })
  const result = mergeStyleProps(props, defaults, { "padding-left": "3px" })

  expect(Object.entries(result.style as object)).toEqual([
    ["color", "black"], ["opacity", 0], ["padding", "2px"], ["padding-left", "3px"],
  ])
  expect(result.onclick).toBe(onclick)
  expect(result.className).toBe("user")
  expect(Object.keys(supplied)).toEqual(["padding-left", "opacity", "padding"])
})

test("passes the element and native event through mapped handlers and skips null messages", () => {
  const native = new Event("click", { cancelable: true })
  const onclick: EventHandler = (payload, element, event) => {
    if (!element.isConnected) return null
    event.preventDefault()
    return { type: payload.type }
  }
  const mapped = Html.map(message => ({ type: `child:${message.type}` }), h("button", { onclick }))
  const messages: Msg[] = []
  const wrapped = wrapDispatch(message => { messages.push(message) }, mapped) as VElement
  const listener = wrapped.props.onclick as RuntimeEventHandler
  const element = { isConnected: false }

  listener({ type: "click" }, element as Element, native)
  expect(messages).toEqual([])
  element.isConnected = true
  listener({ type: "click" }, element as Element, native)
  expect(messages).toEqual([{ type: "child:click" }])
  expect(native.defaultPrevented).toBe(true)
})
