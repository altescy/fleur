import { JsonValue } from "../core/types"

export type HttpExpect = "json" | "text"
export type HttpCredentials = "omit" | "same-origin" | "include"
export type HttpErrorKind = "network" | "timeout" | "abort" | "decode" | "unknown"

export type DecodedBody<TExpect extends HttpExpect> = TExpect extends "json" ? JsonValue : string

export type HttpResponse<TExpect extends HttpExpect> = {
  ok: boolean
  status: number
  statusText: string
  url: string
  headers: Record<string, string>
  body: DecodedBody<TExpect>
}

export type HttpBody = BodyInit | JsonValue | null

export type HttpRequest<TExpect extends HttpExpect = HttpExpect> = {
  method: string
  url: string
  expect: TExpect
  headers?: Record<string, string>
  body?: HttpBody
  timeoutMs?: number
  credentials?: HttpCredentials
}

export type HttpError = {
  kind: HttpErrorKind
  message: string
  url?: string
  status?: number
  statusText?: string
}
