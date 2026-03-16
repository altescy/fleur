import { describe, expect, test } from "bun:test"

import { Cmd } from "../src/effects"

describe("Cmd.task", () => {
  test("dispatches ok message on resolve", async () => {
    const received: Array<{ type: string; value?: unknown }> = []
    const cmd = Cmd.task(
      () => Promise.resolve(42),
      (value) => ({ type: "OK", value }),
      (error) => ({ type: "ERR", value: error }),
    )

    cmd((msg) => received.push(msg))
    await Promise.resolve()

    expect(received).toEqual([{ type: "OK", value: 42 }])
  })

  test("dispatches err message on reject", async () => {
    const received: Array<{ type: string; value?: unknown }> = []
    const cmd = Cmd.task(
      () => Promise.reject(new Error("boom")),
      (value) => ({ type: "OK", value }),
      (error) => ({ type: "ERR", value: error instanceof Error ? error.message : error }),
    )

    cmd((msg) => received.push(msg))
    await Promise.resolve()
    await Promise.resolve()

    expect(received).toEqual([{ type: "ERR", value: "boom" }])
  })
})
