from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Literal, cast

from fleur.core.model import Model
from fleur.core.runtime import RUNTIME_HTTP, RUNTIME_REQUEST, runtime_call
from fleur.core.task import TaskLike, TaskValueT
from fleur.js.ast import ESTreeExpression
from fleur.js.builder import json_expr
from fleur.types import JsonValue

HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
HttpErrorKind = Literal["network", "timeout", "abort", "http_status", "decode", "unknown"]
HttpCredentials = Literal["omit", "same-origin", "include"]


@dataclass(frozen=True, slots=True)
class HttpError(Model):
    kind: HttpErrorKind
    message: str
    url: str | None = None
    status: int | None = None
    status_text: str | None = None


@dataclass(frozen=True, slots=True)
class _HttpTask(Generic[TaskValueT], TaskLike[TaskValueT, HttpError]):
    expr: ESTreeExpression

    def __compile__(self) -> ESTreeExpression:
        return self.expr


@dataclass(frozen=True, slots=True)
class _Expect(Generic[TaskValueT]):
    name: str = field(repr=False)


class Http:
    @staticmethod
    def expectJson() -> _Expect[JsonValue]:
        return _Expect("json")

    @staticmethod
    def expectText() -> _Expect[str]:
        return _Expect("text")

    @staticmethod
    def request(
        method: HttpMethod,
        url: str,
        *,
        expect: _Expect[TaskValueT],
        headers: dict[str, str] | None = None,
        body: JsonValue | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[TaskValueT, HttpError]:
        request: dict[str, JsonValue] = {
            "method": method.upper(),
            "url": url,
            "expect": expect.name,
        }
        if headers is not None:
            request["headers"] = {k: v for k, v in headers.items()}
        if body is not None:
            request["body"] = body
        if timeout_ms is not None:
            request["timeoutMs"] = timeout_ms
        if credentials is not None:
            request["credentials"] = credentials

        compiled = runtime_call((RUNTIME_HTTP, RUNTIME_REQUEST), json_expr(request))
        return cast(TaskLike[TaskValueT, HttpError], _HttpTask(compiled))

    @staticmethod
    def get(
        url: str,
        *,
        expect: _Expect[TaskValueT],
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[TaskValueT, HttpError]:
        return Http.request(
            "GET",
            url,
            expect=expect,
            headers=headers,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def post(
        url: str,
        *,
        expect: _Expect[TaskValueT],
        body: JsonValue | None = None,
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[TaskValueT, HttpError]:
        return Http.request(
            "POST",
            url,
            expect=expect,
            headers=headers,
            body=body,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def put(
        url: str,
        *,
        expect: _Expect[TaskValueT],
        body: JsonValue | None = None,
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[TaskValueT, HttpError]:
        return Http.request(
            "PUT",
            url,
            expect=expect,
            headers=headers,
            body=body,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def patch(
        url: str,
        *,
        expect: _Expect[TaskValueT],
        body: JsonValue | None = None,
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[TaskValueT, HttpError]:
        return Http.request(
            "PATCH",
            url,
            expect=expect,
            headers=headers,
            body=body,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def delete(
        url: str,
        *,
        expect: _Expect[TaskValueT],
        body: JsonValue | None = None,
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[TaskValueT, HttpError]:
        return Http.request(
            "DELETE",
            url,
            expect=expect,
            headers=headers,
            body=body,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def head(
        url: str,
        *,
        expect: _Expect[TaskValueT],
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[TaskValueT, HttpError]:
        return Http.request(
            "HEAD",
            url,
            expect=expect,
            headers=headers,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def options(
        url: str,
        *,
        expect: _Expect[TaskValueT],
        headers: dict[str, str] | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[TaskValueT, HttpError]:
        return Http.request(
            "OPTIONS",
            url,
            expect=expect,
            headers=headers,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )
