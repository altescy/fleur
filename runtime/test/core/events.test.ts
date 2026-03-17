import { describe, expect, test } from "bun:test"

import { normalizeEventPayload } from "../../src/core/events"

describe("normalizeEventPayload", () => {
  test("normalizes click as pointer-like payload", () => {
    const payload = normalizeEventPayload(
      "click",
      {
        type: "click",
        pointerId: 7,
        clientX: 12,
        clientY: 34,
        button: 0,
        altKey: false,
        ctrlKey: true,
        shiftKey: false,
        metaKey: false,
      } as unknown as Event,
    )

    expect(payload).toMatchObject({
      type: "click",
      pointer_id: 7,
      client_x: 12,
      client_y: 34,
      ctrl: true,
    })
  })

  test("normalizes keyboard payload", () => {
    const payload = normalizeEventPayload(
      "keydown",
      {
        type: "keydown",
        key: "Enter",
        code: "Enter",
        repeat: false,
        altKey: false,
        ctrlKey: false,
        shiftKey: true,
        metaKey: false,
      } as unknown as Event,
    )

    expect(payload).toMatchObject({
      type: "keydown",
      key: "Enter",
      code: "Enter",
      shift: true,
    })
  })
})
