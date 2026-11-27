import { describe, expect, test } from "bun:test"

import { findMismatch, ShapeSchema } from "../../src/http/shape"

const todos: ShapeSchema = {
  root: { kind: "list", item: { kind: "ref", name: "Todo" } },
  defs: {
    Todo: {
      kind: "object",
      fields: {
        id: { kind: "integer" },
        title: { kind: "string" },
        state: { kind: "literal", values: ["open", "done"] },
        note: { kind: "union", options: [{ kind: "string" }, { kind: "null" }] },
        tags: { kind: "dict", value: { kind: "number" } },
      },
    },
  },
}

const check = (value: unknown, schema: ShapeSchema = todos) => findMismatch(value, schema.root, schema, "body")

describe("findMismatch", () => {
  test("accepts a value of the shape and ignores extra fields", () => {
    expect(check([{ id: 1, title: "A", state: "open", note: null, tags: { x: 1.5 }, extra: true }])).toBeNull()
  })

  test("locates the first mismatch", () => {
    expect(check([{ id: 1, title: "A", state: "open", note: null, tags: {} }, { id: 2, title: 3 }])).toBe(
      "body[1].title: expected string, got integer",
    )
    expect(check([{ id: 1.5, title: "A", state: "open", note: null, tags: {} }])).toBe(
      "body[0].id: expected integer, got number",
    )
    expect(check([{ id: 1, title: "A", state: "later", note: null, tags: {} }])).toBe(
      'body[0].state: expected one of "open", "done", got "later"',
    )
    expect(check([{ id: 1, title: "A", state: "open", note: null, tags: { x: "1" } }])).toBe(
      'body[0].tags["x"]: expected number, got string',
    )
    expect(check({})).toBe("body: expected array, got object")
  })

  test("reports a missing required field and fills a missing optional one with null", () => {
    expect(check([{ id: 1, state: "open", tags: {} }])).toBe("body[0].title: missing")
    const todo: Record<string, unknown> = { id: 1, title: "A", state: "open", tags: {} }
    expect(check([todo])).toBeNull()
    expect(todo.note).toBeNull()
  })

  test("follows recursive references", () => {
    const tree: ShapeSchema = {
      root: { kind: "ref", name: "Node" },
      defs: { Node: { kind: "object", fields: { children: { kind: "list", item: { kind: "ref", name: "Node" } } } } },
    }
    expect(check({ children: [{ children: [] }] }, tree)).toBeNull()
    expect(check({ children: [{ children: [1] }] }, tree)).toBe("body.children[0].children[0]: expected object, got integer")
  })
})
