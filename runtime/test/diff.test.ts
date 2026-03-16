import { describe, expect, test } from "bun:test"

import { diff } from "../src/diff"
import { h } from "../src/vdom"

describe("diff", () => {
  test("creates TEXT patch when text changes", () => {
    const oldV = h("div", {}, "A")
    const newV = h("div", {}, "B")

    const patches = diff(oldV, newV)

    expect(patches.length).toBe(1)
    expect(patches[0]).toEqual({ type: "TEXT", path: [0], value: "B" })
  })

  test("creates MOVE patch for keyed reordering", () => {
    const oldV = h("ul", {}, h("li", { key: "a" }, "A"), h("li", { key: "b" }, "B"))
    const newV = h("ul", {}, h("li", { key: "b" }, "B"), h("li", { key: "a" }, "A"))

    const patches = diff(oldV, newV)
    const hasMove = patches.some((patch) => patch.type === "MOVE")

    expect(hasMove).toBe(true)
  })
})
