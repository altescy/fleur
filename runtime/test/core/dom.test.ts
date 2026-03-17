import { describe, expect, test } from "bun:test"

import { setProp } from "../../src/core/dom"

type FakeStyle = {
  values: Record<string, string>
  setProperty: (key: string, value: string) => void
}

type FakeElement = {
  style: FakeStyle
  attrs: Record<string, string>
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
})
