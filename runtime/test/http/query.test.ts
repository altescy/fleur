import { describe, expect, test } from "bun:test"

import { withQuery } from "../../src/http/client"

describe("withQuery", () => {
  test("appends encoded parameters to a relative URL", () => {
    expect(withQuery("/todos", { q: "a b&c", page: 2, done: false })).toBe("/todos?q=a+b%26c&page=2&done=false")
  })

  test("keeps an existing query string and fragment", () => {
    expect(withQuery("/todos?sort=asc#top", { q: "x" })).toBe("/todos?sort=asc&q=x#top")
    expect(withQuery("/todos?", { q: "x" })).toBe("/todos?q=x")
  })

  test("leaves the URL unchanged without parameters", () => {
    expect(withQuery("/todos", undefined)).toBe("/todos")
    expect(withQuery("/todos", {})).toBe("/todos")
  })
})
