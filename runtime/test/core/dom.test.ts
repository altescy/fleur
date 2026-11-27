import { describe, expect, test } from "bun:test"

import { removeProp, setProp } from "../../src/core/dom"
import { disposeDomEffects } from "../../src/core/domEffect"
import { DomEffect, JsonValue } from "../../src/core/types"

type FakeStyle = {
  values: Record<string, string>
  setProperty: (key: string, value: string) => void
}

type FakeElement = {
  style: FakeStyle
  attrs: Record<string, string>
  value: string
  checked: boolean
  selected: boolean
  setAttribute: (name: string, value: string) => void
  removeAttribute: (name: string) => void
}

const createFakeElement = (): FakeElement => {
  const style: FakeStyle = {
    values: {},
    setProperty: (key: string, value: string) => {
      style.values[key] = value
    },
  }

  return {
    style,
    attrs: {},
    value: "",
    checked: false,
    selected: false,
    setAttribute(name: string, value: string): void {
      this.attrs[name] = value
    },
    removeAttribute(name: string): void {
      delete this.attrs[name]
      if (name === "style") {
        style.values = {}
      }
    },
  }
}

describe("setProp", () => {
  test("replaces style object values", () => {
    const el = createFakeElement()

    setProp(el as unknown as Element, "style", { background: "#eef2ff", border: "1px solid #c7d2fe" })
    setProp(el as unknown as Element, "style", { gap: "8px" })

    expect(el.style.values).toEqual({ gap: "8px" })
  })

  test("updates value property for controlled inputs", () => {
    const el = createFakeElement()

    setProp(el as unknown as Element, "value", "hello")
    setProp(el as unknown as Element, "value", "")

    expect(el.value).toBe("")
  })

  test("sets falsy attributes except false/null", () => {
    const el = createFakeElement()

    setProp(el as unknown as Element, "tabindex", 0)
    setProp(el as unknown as Element, "aria-label", "")

    expect(el.attrs.tabindex).toBe("0")
    expect(el.attrs["aria-label"]).toBe("")
  })

  test("runs only the latest pending DOM effect on a connected element", async () => {
    const element = { ...createFakeElement(), isConnected: false }
    const target = element as unknown as Element
    const applied: JsonValue[] = []
    const effect = (value: JsonValue): DomEffect => ({
      key: "test",
      args: [value],
      run: (_element, next) => { applied.push(next) },
    })

    setProp(target, "domEffect", effect("before insertion"))
    element.isConnected = true
    setProp(target, "domEffect", effect("latest"))
    expect(applied).toEqual([])
    await Promise.resolve()
    expect(applied).toEqual(["latest"])
    expect(element.attrs).toEqual({})

    setProp(target, "domEffect", effect("cancelled"))
    removeProp(target, "domEffect")
    await Promise.resolve()
    setProp(target, "domEffect", effect("unmounted"))
    element.isConnected = false
    await Promise.resolve()
    expect(applied).toEqual(["latest"])
  })

  test("updates an installed DOM effect and disposes it when an ancestor is removed", async () => {
    const target = { isConnected: true, childNodes: [] } as unknown as Element
    const ancestor = { childNodes: [target] } as unknown as Node
    const calls: JsonValue[] = []
    const effect: DomEffect = {
      key: "test",
      args: [1],
      run: () => {
        calls.push("setup")
        return {
          update: (value) => { calls.push(value) },
          dispose: () => { calls.push("dispose") },
        }
      },
    }

    setProp(target, "domEffect", effect)
    await Promise.resolve()
    setProp(target, "domEffect", { ...effect, args: [2] })
    await Promise.resolve()
    setProp(target, "domEffect", { ...effect, args: [3] })
    disposeDomEffects(ancestor)
    await Promise.resolve()
    expect(calls).toEqual(["setup", 1, 2, "dispose"])
  })

  test("cancels a pending effect without cancelling its sibling", async () => {
    const target = { isConnected: true, childNodes: [] } as unknown as Element
    const calls: string[] = []
    const effect = (key: string): DomEffect => ({
      key, args: [], run: () => { calls.push(key) },
    })

    setProp(target, "domEffect:a", effect("cancelled"))
    setProp(target, "domEffect:b", effect("B"))
    removeProp(target, "domEffect:a")
    setProp(target, "domEffect:a", effect("A"))
    await Promise.resolve()

    expect(calls).toEqual(["B", "A"])
  })

  test("cleans up a scoped effect removed during setup", () => {
    const target = { isConnected: true, childNodes: [] } as unknown as Element
    const calls: string[] = []
    setProp(target, "domEffect:self", {
      key: "self",
      args: [],
      sync: true,
      run: () => {
        removeProp(target, "domEffect:self")
        return {
          update: () => { calls.push("update") },
          dispose: () => { calls.push("dispose") },
        }
      },
    })

    expect(calls).toEqual(["dispose"])
  })
})
