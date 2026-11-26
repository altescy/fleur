import { expect, test } from "bun:test"
import { mergeStyleProps } from "../../src/core/vdom"

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
