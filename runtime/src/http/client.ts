import { DecodedBody, HttpBody, HttpError, HttpExpect, HttpQueryValue, HttpRequest, HttpResponse } from "./types"

const isHttpError = (error: unknown): error is HttpError => {
  return typeof error === "object" && error !== null && "kind" in error && "message" in error
}

const isAbortError = (error: unknown): boolean => {
  if (!(error instanceof Error)) return false
  return error.name === "AbortError"
}

const toMessage = (error: unknown): string => {
  if (error instanceof Error) return error.message
  return String(error)
}

const hasContentType = (headers: Record<string, string>): boolean => {
  for (const key of Object.keys(headers)) {
    if (key.toLowerCase() === "content-type") return true
  }
  return false
}

const withDefaultContentType = (headers: Record<string, string> | undefined): Record<string, string> => {
  const next = { ...(headers ?? {}) }
  if (!hasContentType(next)) {
    next["Content-Type"] = "application/json"
  }
  return next
}

const buildFetchBody = (body: HttpBody | undefined): BodyInit | undefined => {
  if (body === undefined || body === null) return undefined
  if (typeof body === "string") return body
  if (
    body instanceof Blob
    || body instanceof FormData
    || body instanceof URLSearchParams
    || body instanceof ReadableStream
    || body instanceof ArrayBuffer
    || ArrayBuffer.isView(body)
  ) {
    return body
  }
  return JSON.stringify(body)
}

const decodeResponseBody = async <TExpect extends HttpExpect>(
  response: Response,
  expect: TExpect,
  url: string,
): Promise<DecodedBody<TExpect>> => {
  try {
    if (expect === "json") {
      return (await response.json()) as DecodedBody<TExpect>
    }
    return (await response.text()) as DecodedBody<TExpect>
  } catch (error) {
    const httpError: HttpError = {
      kind: "decode",
      message: toMessage(error),
      url,
      status: response.status,
      status_text: response.statusText,
    }
    throw httpError
  }
}

const responseHeaders = (response: Response): Record<string, string> => {
  const headers: Record<string, string> = {}
  response.headers.forEach((value, key) => {
    headers[key] = value
  })
  return headers
}

const buildFetchError = (error: unknown, request: HttpRequest<HttpExpect>): HttpError => {
  const details = { url: request.url, status: null, status_text: null }
  if (isAbortError(error)) {
    return {
      ...details,
      kind: request.timeoutMs !== undefined ? "timeout" : "abort",
      message: request.timeoutMs !== undefined ? `Request timed out after ${request.timeoutMs}ms` : "Request aborted",
    }
  }

  if (error instanceof TypeError) {
    return {
      ...details,
      kind: "network",
      message: error.message,
    }
  }

  return {
    ...details,
    kind: "unknown",
    message: toMessage(error),
  }
}

// Append encoded query parameters, keeping any existing query string and fragment.
export const withQuery = (url: string, query: Record<string, HttpQueryValue> | undefined): string => {
  const entries = Object.entries(query ?? {})
  if (entries.length === 0) return url
  const hashIndex = url.indexOf("#")
  const base = hashIndex === -1 ? url : url.slice(0, hashIndex)
  const hash = hashIndex === -1 ? "" : url.slice(hashIndex)
  const params = new URLSearchParams(entries.map(([key, value]) => [key, String(value)])).toString()
  const separator = !base.includes("?") ? "?" : base.endsWith("?") || base.endsWith("&") ? "" : "&"
  return base + separator + params + hash
}

const executeRequest = async <TExpect extends HttpExpect>(
  original: HttpRequest<TExpect>,
): Promise<HttpResponse<TExpect>> => {
  const request = { ...original, url: withQuery(original.url, original.query) }
  const controller = request.timeoutMs !== undefined ? new AbortController() : undefined
  const timeoutId =
    request.timeoutMs !== undefined
      ? setTimeout(() => {
        controller?.abort()
      }, request.timeoutMs)
      : undefined

  const headers =
    request.body !== undefined && request.body !== null && typeof request.body !== "string"
      ? withDefaultContentType(request.headers)
      : request.headers

  try {
    const response = await fetch(request.url, {
      method: request.method,
      headers,
      body: buildFetchBody(request.body),
      credentials: request.credentials,
      signal: controller?.signal,
    })

    const body = await decodeResponseBody(response, request.expect, request.url)
    return {
      ok: response.ok,
      status: response.status,
      status_text: response.statusText,
      url: response.url,
      headers: responseHeaders(response),
      body,
    }
  } catch (error) {
    if (isHttpError(error)) {
      throw error
    }
    throw buildFetchError(error, request)
  } finally {
    if (timeoutId !== undefined) clearTimeout(timeoutId)
  }
}

const Http = {
  request: <TExpect extends HttpExpect>(request: HttpRequest<TExpect>): Promise<HttpResponse<TExpect>> => executeRequest(request),
}

export { Http }
