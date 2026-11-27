import { afterEach, describe, expect, test } from "bun:test"

import { Http } from "../../src/http/client"
import { ShapeSchema } from "../../src/http/shape"
import { HttpError } from "../../src/http/types"

const realFetch = globalThis.fetch
afterEach(() => {
  globalThis.fetch = realFetch
})

const respond = (body: BodyInit | null, status: number) => {
  globalThis.fetch = (async () => new Response(body, { status })) as unknown as typeof fetch
}

const anyShape: ShapeSchema = { root: { kind: "any" }, defs: {} }
const problem: ShapeSchema = {
  root: { kind: "ref", name: "Problem" },
  defs: { Problem: { kind: "object", fields: { message: { kind: "string" } } } },
}

const failure = async (errorShape: ShapeSchema | undefined, timeoutMs?: number): Promise<HttpError> => {
  try {
    await Http.request({ method: "GET", url: "/todos", expect: "json", shape: anyShape, errorShape, timeoutMs })
  } catch (error) {
    return error as HttpError
  }
  throw new Error("The request did not fail")
}

describe("typed error bodies", () => {
  test("deliver a body of the declared shape", async () => {
    respond(JSON.stringify({ message: "Title is required" }), 422)
    expect(await failure(problem)).toMatchObject({ kind: "status", status: 422, body: { message: "Title is required" } })
  })

  test("give null for a body of another shape or an empty body", async () => {
    respond("<h1>Not Found</h1>", 404)
    expect((await failure(problem)).body).toBeNull()
    respond("", 500)
    expect((await failure(anyShape)).body).toBeNull()
  })

  test("try the text when its JSON reading does not fit the shape", async () => {
    respond("404", 404)
    expect((await failure({ root: { kind: "string" }, defs: {} })).body).toBe("404")
  })

  test("report a timeout while reading the error body as a timeout", async () => {
    globalThis.fetch = (async (_url: string, init: RequestInit) => {
      const stream = new ReadableStream<Uint8Array>({
        start(controller) {
          controller.enqueue(new TextEncoder().encode('{"mess'))
          init.signal?.addEventListener("abort", () => controller.error(new DOMException("Aborted", "AbortError")))
        },
      })
      return new Response(stream, { status: 422 })
    }) as unknown as typeof fetch
    expect(await failure(problem, 20)).toMatchObject({ kind: "timeout", body: null })
  })
})
