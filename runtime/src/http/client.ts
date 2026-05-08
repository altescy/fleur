import { HttpBody, HttpError, HttpExpect, HttpRequest, HttpResponse } from "./types"

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

const decodeResponse = async <TExpect extends HttpExpect>(
  response: Response,
  expect: TExpect,
  url: string,
): Promise<HttpResponse<TExpect>> => {
  try {
    if (expect === "json") {
      return (await response.json()) as HttpResponse<TExpect>
    }
    return (await response.text()) as HttpResponse<TExpect>
  } catch (error) {
    const httpError: HttpError = {
      kind: "decode",
      message: toMessage(error),
      url,
      status: response.status,
      statusText: response.statusText,
    }
    throw httpError
  }
}

const buildHttpStatusError = (response: Response, url: string): HttpError => ({
  kind: "http_status",
  message: `HTTP ${response.status} ${response.statusText}`,
  url,
  status: response.status,
  statusText: response.statusText,
})

const buildFetchError = (error: unknown, request: HttpRequest<HttpExpect>): HttpError => {
  if (isAbortError(error)) {
    return {
      kind: request.timeoutMs !== undefined ? "timeout" : "abort",
      message: request.timeoutMs !== undefined ? `Request timed out after ${request.timeoutMs}ms` : "Request aborted",
      url: request.url,
    }
  }

  if (error instanceof TypeError) {
    return {
      kind: "network",
      message: error.message,
      url: request.url,
    }
  }

  return {
    kind: "unknown",
    message: toMessage(error),
    url: request.url,
  }
}

const executeRequest = async <TExpect extends HttpExpect>(request: HttpRequest<TExpect>): Promise<HttpResponse<TExpect>> => {
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

    if (!response.ok) {
      throw buildHttpStatusError(response, request.url)
    }

    return await decodeResponse(response, request.expect, request.url)
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
  get: <TExpect extends HttpExpect>(
    url: string,
    expect: TExpect,
    options?: Omit<HttpRequest<TExpect>, "method" | "url" | "expect" | "body">,
  ): Promise<HttpResponse<TExpect>> => {
    return executeRequest({
      method: "GET",
      url,
      expect,
      headers: options?.headers,
      timeoutMs: options?.timeoutMs,
      credentials: options?.credentials,
    })
  },
}

export { Http }
