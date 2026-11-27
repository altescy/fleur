import { describe, expect, test } from "bun:test"

import { diff } from "../../src/core/diff"
import { DomEffect } from "../../src/core/types"
import { h } from "../../src/core/vdom"

describe("diff", () => {
  test("compares DOM effects by key and arguments", () => {
    const effect = (key: string, value: boolean): DomEffect => ({ key, args: [value], run: () => {} })
    const before = h("div", { "domEffect:test": effect("test", true) })
    const same = h("div", { "domEffect:test": effect("test", true) })
    const after = effect("test", false)
    const replaced = h("div", { "domEffect:test": effect("different", true) })

    expect(diff(before, same)).toEqual([])
    expect(diff(before, h("div", { "domEffect:test": after }))).toEqual([
      { type: "PROPS", path: [], props: { "domEffect:test": after } },
    ])
    expect(diff(before, replaced)).toEqual([
      { type: "PROPS", path: [], props: { "domEffect:test": replaced.props["domEffect:test"] } },
    ])
  })

  test("reconciles named effects independently of ordinary props and node identity", () => {
    const keep: DomEffect = { key: "keep", args: [], run: () => {} }
    const remove: DomEffect = { key: "old", args: [], run: () => {} }
    const add: DomEffect = { key: "new", args: [], run: () => {} }
    const before = h("input", { "domEffect:old": remove, "domEffect:keep": keep, placeholder: "old" })
    const after = h("input", { "domEffect:new": add, "domEffect:keep": keep, placeholder: "new" })

    const [patch] = diff(before, after)
    expect(patch).toEqual({
      type: "PROPS",
      path: [],
      props: { placeholder: "new", "domEffect:old": undefined, "domEffect:new": add },
    })
    if (patch.type === "PROPS") {
      expect(Object.keys(patch.props)).toEqual(["domEffect:old", "placeholder", "domEffect:new"])
    }
  })

  test("refreshes an opted-in DOM effect after its children are patched", () => {
    const effect: DomEffect = { key: "refresh", args: [], run: () => {}, refresh: true }
    const before = h("div", { "domEffect:test": effect }, "A")

    expect(diff(before, h("div", { "domEffect:test": effect }, "B"))).toEqual([
      { type: "TEXT", path: [0], value: "B" },
      { type: "PROPS", path: [], props: { "domEffect:test": effect } },
    ])
    expect(diff(before, h("div", { "domEffect:test": effect }, "A"))).toEqual([])
  })

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
