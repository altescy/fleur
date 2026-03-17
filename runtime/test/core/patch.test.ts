import { describe, expect, test } from "bun:test"

import { patch } from "../../src/core/patch"
import { h } from "../../src/core/vdom"
import { instantiate } from "../../src/core/dom"

type FakeNode = {
  childNodes: FakeNode[]
  parentNode: FakeNode | null
  textContent: string | null
  appendChild: (node: FakeNode) => FakeNode
  insertBefore: (node: FakeNode, ref: FakeNode | null) => FakeNode
  removeChild: (node: FakeNode) => FakeNode
  replaceChild: (next: FakeNode, prev: FakeNode) => FakeNode
}

const createFakeNode = (textContent: string | null = null): FakeNode => {
  const node: FakeNode = {
    childNodes: [],
    parentNode: null,
    textContent,
    appendChild(next: FakeNode): FakeNode {
      next.parentNode = node
      node.childNodes.push(next)
      return next
    },
    insertBefore(next: FakeNode, ref: FakeNode | null): FakeNode {
      next.parentNode = node
      if (!ref) {
        node.childNodes.push(next)
        return next
      }
      const index = node.childNodes.indexOf(ref)
      if (index < 0) {
        node.childNodes.push(next)
      } else {
        node.childNodes.splice(index, 0, next)
      }
      return next
    },
    removeChild(target: FakeNode): FakeNode {
      const index = node.childNodes.indexOf(target)
      if (index >= 0) {
        node.childNodes.splice(index, 1)
      }
      target.parentNode = null
      return target
    },
    replaceChild(next: FakeNode, prev: FakeNode): FakeNode {
      const index = node.childNodes.indexOf(prev)
      if (index >= 0) {
        next.parentNode = node
        prev.parentNode = null
        node.childNodes[index] = next
      }
      return prev
    },
  }
  return node
}

const createFakeElement = (): FakeNode & {
  style: Record<string, unknown>
  setAttribute: (name: string, value: string) => void
  removeAttribute: (name: string) => void
  addEventListener: (name: string, listener: EventListener) => void
  removeEventListener: (name: string, listener: EventListener) => void
} => ({
  ...createFakeNode(),
  style: {},
  setAttribute() {},
  removeAttribute() {},
  addEventListener() {},
  removeEventListener() {},
})

describe("patch", () => {
  test("applies INSERT when target node does not exist yet", () => {
    const previousDocument = (globalThis as { document?: object }).document
    ;(globalThis as { document: object }).document = {
      createElement: () => createFakeElement(),
      createTextNode: (value: string) => createFakeNode(value),
    }

    const root = instantiate(h("div", {}, "A"))

    try {
      patch(root, [{ type: "INSERT", path: [1], vnode: h("span", {}, "B") }])

      expect(root.childNodes.length).toBe(2)
      expect(root.childNodes[1]?.childNodes[0]?.textContent).toBe("B")
    } finally {
      if (previousDocument === undefined) {
        delete (globalThis as { document?: object }).document
      } else {
        ;(globalThis as { document: object }).document = previousDocument
      }
    }
  })

  test("keeps root when replacing nested node and applying next patch", () => {
    const previousDocument = (globalThis as { document?: object }).document
    ;(globalThis as { document: object }).document = {
      createElement: () => createFakeElement(),
      createTextNode: (value: string) => createFakeNode(value),
    }

    const root = instantiate(h("div", {}, h("span", {}, "A")))

    try {
      patch(root, [
        { type: "REPLACE", path: [0], vnode: h("span", {}, "B") },
        { type: "INSERT", path: [1], vnode: h("span", {}, "C") },
      ])

      expect(root.childNodes.length).toBe(2)
      expect(root.childNodes[0]?.childNodes[0]?.textContent).toBe("B")
      expect(root.childNodes[1]?.childNodes[0]?.textContent).toBe("C")
    } finally {
      if (previousDocument === undefined) {
        delete (globalThis as { document?: object }).document
      } else {
        ;(globalThis as { document: object }).document = previousDocument
      }
    }
  })
})
