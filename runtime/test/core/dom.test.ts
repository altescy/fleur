import { describe, expect, test } from "bun:test"

import { setProp } from "../../src/core/dom"

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
})
