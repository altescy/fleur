import { describe, expect, test } from "bun:test"

import { Cmd } from "../../src/core/effects"
import { Http } from "../../src/http/client"

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

describe("Http.request", () => {
  test("returns parsed json when expect is json", async () => {
    const originalFetch = globalThis.fetch
    globalThis.fetch = (() =>
      Promise.resolve({
        ok: true,
        status: 200,
        statusText: "OK",
        json: () => Promise.resolve({ ok: true }),
      } as Response)) as typeof fetch

    try {
      await expect(Http.request({ method: "GET", url: "https://example.com/todo", expect: "json" })).resolves.toEqual({ ok: true })
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  test("rejects with http_status error on non-2xx response", async () => {
    const originalFetch = globalThis.fetch
    globalThis.fetch = (() =>
      Promise.resolve({
        ok: false,
        status: 404,
        statusText: "Not Found",
      } as Response)) as typeof fetch

    try {
      await expect(Http.request({ method: "GET", url: "https://example.com/todo", expect: "json" })).rejects.toMatchObject({
        kind: "http_status",
        status: 404,
        statusText: "Not Found",
      })
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  test("rejects with timeout error when timed out", async () => {
    const originalFetch = globalThis.fetch
    globalThis.fetch = ((_: string | URL | Request, init?: RequestInit) =>
      new Promise((_, reject) => {
        const signal = init?.signal
        if (!signal) {
          reject(new Error("missing signal"))
          return
        }
        signal.addEventListener("abort", () => {
          reject(Object.assign(new Error("aborted"), { name: "AbortError" }))
        })
      })) as typeof fetch

    try {
      await expect(Http.request({ method: "GET", url: "https://example.com/todo", expect: "json", timeoutMs: 1 })).rejects.toMatchObject({
        kind: "timeout",
      })
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  test("stringifies object body and sets content-type", async () => {
    const originalFetch = globalThis.fetch
    let capturedInit: RequestInit | undefined
    globalThis.fetch = ((_: string | URL | Request, init?: RequestInit) => {
      capturedInit = init
      return Promise.resolve({ ok: true, status: 200, statusText: "OK", text: () => Promise.resolve("ok") } as Response)
    }) as typeof fetch

    try {
      await expect(
        Http.request({ method: "POST", url: "https://example.com/todo", expect: "text", body: { done: false } }),
      ).resolves.toBe("ok")
      expect(capturedInit?.body).toBe('{"done":false}')
      expect(capturedInit?.headers).toMatchObject({ "Content-Type": "application/json" })
    } finally {
      globalThis.fetch = originalFetch
    }
  })
})
