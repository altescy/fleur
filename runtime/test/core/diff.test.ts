import { describe, expect, test } from "bun:test"

import { diff } from "../../src/core/diff"
import { h } from "../../src/core/vdom"

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

  test("reuses unkeyed siblings and updates keyed nodes at their new positions", () => {
    const item = (key: string, text: string) => h("li", { key }, text)
    const oldV = h("ul", {}, h("style", {}, "old"), item("a", "A"), item("b", "B"), item("gone", "Gone"))
    const newV = h("ul", {}, h("style", {}, "new"), item("b", "Updated"), item("a", "A"))

    expect(diff(oldV, newV)).toEqual([
      { type: "REMOVE", path: [3] },
      { type: "TEXT", path: [0, 0], value: "new" },
      { type: "MOVE", path: [2], to: [1] },
      { type: "TEXT", path: [1, 0], value: "Updated" },
    ])
  })

  test("emits REMOVE patches from tail to head", () => {
    const oldV = h("div", {}, h("span", {}, "A"), h("span", {}, "B"), h("span", {}, "C"), h("span", {}, "D"))
    const newV = h("div", {}, h("span", {}, "A"), h("span", {}, "X"))

    const patches = diff(oldV, newV)
    const removePaths = patches.filter((patch) => patch.type === "REMOVE").map((patch) => patch.path)

    expect(removePaths).toEqual([[3], [2]])
  })
})
