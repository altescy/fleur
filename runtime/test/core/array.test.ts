import { expect, test } from "bun:test"
import { sortBy } from "../../src/core/array"

test("sortBy returns a stable copy in either direction and evaluates each key once", () => {
  const items = Object.freeze([{ n: 900 }, { n: 1200 }, { n: 900 }])
  const visited: number[] = []
  const descending = sortBy(items, item => {
    visited.push(item.n)
    return item.n
  }, true)
  expect(visited).toEqual([900, 1200, 900])
  expect(descending[0]).toBe(items[1])
  expect(descending[1]).toBe(items[0])
  expect(descending[2]).toBe(items[2])
  const ascending = sortBy(items, item => item.n, false)
  expect(ascending[0]).toBe(items[0])
  expect(ascending[1]).toBe(items[2])
  expect(ascending[2]).toBe(items[1])
})
