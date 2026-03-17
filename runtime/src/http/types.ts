export type HttpExpect = "json" | "text"
export type HttpCredentials = "omit" | "same-origin" | "include"
export type HttpErrorKind = "network" | "timeout" | "abort" | "http_status" | "decode" | "unknown"

export type HttpRequest = {
  method: string
  url: string
  expect: HttpExpect
  headers?: Record<string, string>
  body?: unknown
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
