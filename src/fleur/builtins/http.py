from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Generic, Literal, TypeAlias, Union, overload

from fleur.core._shape import Shape, shape_of
from fleur.core.expr import Expr
from fleur.core.model import Model
from fleur.core.runtime import RUNTIME_HTTP, RUNTIME_REQUEST, runtime_call
from fleur.core.task import TaskLike, TaskValueT
from fleur.core.types import FleurValue
from fleur.js.ast import ESTreeArrayExpression, ESTreeExpression
from fleur.js.builder import json_expr, object_expr
from fleur.types import JsonValue

HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
HttpErrorKind = Literal["network", "timeout", "abort", "decode", "status", "unknown"]
HttpCredentials = Literal["omit", "same-origin", "include"]
HttpQueryValue: TypeAlias = str | int | float | bool
HttpQuery: TypeAlias = Mapping[str, HttpQueryValue | Expr[HttpQueryValue]]
"""Query parameters, encoded and appended to the URL by the runtime."""
HttpHeaders: TypeAlias = Mapping[str, str | Expr[str]]
HttpBody: TypeAlias = Union[JsonValue, Expr[FleurValue], Mapping[str, "HttpBody"], Sequence["HttpBody"]]
"""A JSON body whose values, at any depth, may be read from the model."""


@dataclass(frozen=True, slots=True)
class HttpError(Model):
    kind: HttpErrorKind
    message: str
    url: str | None = None
    status: int | None = None
    status_text: str | None = None


@dataclass(frozen=True, slots=True)
class HttpResponse(Model, Generic[TaskValueT]):
    ok: bool
    status: int
    status_text: str
    url: str
    headers: dict[str, str]
    body: TaskValueT


@dataclass(frozen=True, slots=True)
class _HttpTask(TaskLike[HttpResponse[TaskValueT], HttpError]):
    expr: ESTreeExpression

    def __compile__(self) -> ESTreeExpression:
        return self.expr


@dataclass(frozen=True, slots=True)
class _Expect(Generic[TaskValueT]):
    name: str = field(repr=False)
    shape: Shape | None = field(default=None, repr=False)


def _compile_body(value: HttpBody) -> ESTreeExpression:
    if isinstance(value, Expr):
        return value.__compile__()
    if isinstance(value, Mapping):
        return object_expr((key, _compile_body(item)) for key, item in value.items())
    if isinstance(value, Sequence) and not isinstance(value, str):
        return ESTreeArrayExpression([_compile_body(item) for item in value])
    return json_expr(value)


def _compile_strings(values: Mapping[str, HttpQueryValue | Expr[HttpQueryValue]]) -> ESTreeExpression:
    return object_expr(
        (key, value.__compile__() if isinstance(value, Expr) else json_expr(value)) for key, value in values.items()
    )


class Http:
    """Describe requests that the browser runs when a command schedules them.

    `url`, `query`, `headers` and `body` accept values read from the model. Build paths with
    parameters through `Url.path("/todos/{id}", id=...)`, which encodes each value.
    """

    @staticmethod
    @overload
    def expectJson() -> _Expect[JsonValue]: ...

    @staticmethod
    @overload
    def expectJson(body: type[TaskValueT]) -> _Expect[TaskValueT]: ...

    @staticmethod
    def expectJson(body: type[TaskValueT] | None = None) -> _Expect[TaskValueT] | _Expect[JsonValue]:
        """Decode a JSON body, optionally checking it against a type such as `TodoOut` or `list[TodoOut]`.

        With a type, the runtime validates the body like an Elm JSON decoder: a body of another
        shape fails with `HttpError(kind="decode")`, and a response whose status is not 2xx fails
        with `HttpError(kind="status")` instead of reaching the response handler. Without a type,
        the body is any `JsonValue` and every status reaches the response handler.
        """
        if body is None:
            return _Expect[JsonValue]("json")
        return _Expect[TaskValueT]("json", shape_of(body))

    @staticmethod
    def expectText() -> _Expect[str]:
        return _Expect("text")

    @staticmethod
    def request(
        method: HttpMethod,
        url: str | Expr[str],
        *,
        expect: _Expect[TaskValueT],
        query: HttpQuery | None = None,
        headers: HttpHeaders | None = None,
        body: HttpBody | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[HttpResponse[TaskValueT], HttpError]:
        fields: list[tuple[str, ESTreeExpression]] = [
            ("method", json_expr(method.upper())),
            ("url", url.__compile__() if isinstance(url, Expr) else json_expr(url)),
            ("expect", json_expr(expect.name)),
            *([("shape", json_expr(expect.shape))] if expect.shape is not None else []),
        ]
        if query:
            fields.append(("query", _compile_strings(query)))
        if headers is not None:
            fields.append(("headers", _compile_strings(headers)))
        if body is not None:
            fields.append(("body", _compile_body(body)))
        if timeout_ms is not None:
            fields.append(("timeoutMs", json_expr(timeout_ms)))
        if credentials is not None:
            fields.append(("credentials", json_expr(credentials)))
        return _HttpTask(runtime_call((RUNTIME_HTTP, RUNTIME_REQUEST), object_expr(fields)))

    @staticmethod
    def get(
        url: str | Expr[str],
        *,
        expect: _Expect[TaskValueT],
        query: HttpQuery | None = None,
        headers: HttpHeaders | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[HttpResponse[TaskValueT], HttpError]:
        return Http.request(
            "GET",
            url,
            expect=expect,
            query=query,
            headers=headers,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def post(
        url: str | Expr[str],
        *,
        expect: _Expect[TaskValueT],
        query: HttpQuery | None = None,
        headers: HttpHeaders | None = None,
        body: HttpBody | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[HttpResponse[TaskValueT], HttpError]:
        return Http.request(
            "POST",
            url,
            expect=expect,
            query=query,
            headers=headers,
            body=body,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def put(
        url: str | Expr[str],
        *,
        expect: _Expect[TaskValueT],
        query: HttpQuery | None = None,
        headers: HttpHeaders | None = None,
        body: HttpBody | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[HttpResponse[TaskValueT], HttpError]:
        return Http.request(
            "PUT",
            url,
            expect=expect,
            query=query,
            headers=headers,
            body=body,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def patch(
        url: str | Expr[str],
        *,
        expect: _Expect[TaskValueT],
        query: HttpQuery | None = None,
        headers: HttpHeaders | None = None,
        body: HttpBody | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[HttpResponse[TaskValueT], HttpError]:
        return Http.request(
            "PATCH",
            url,
            expect=expect,
            query=query,
            headers=headers,
            body=body,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def delete(
        url: str | Expr[str],
        *,
        expect: _Expect[TaskValueT],
        query: HttpQuery | None = None,
        headers: HttpHeaders | None = None,
        body: HttpBody | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[HttpResponse[TaskValueT], HttpError]:
        return Http.request(
            "DELETE",
            url,
            expect=expect,
            query=query,
            headers=headers,
            body=body,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def head(
        url: str | Expr[str],
        *,
        expect: _Expect[TaskValueT],
        query: HttpQuery | None = None,
        headers: HttpHeaders | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[HttpResponse[TaskValueT], HttpError]:
        return Http.request(
            "HEAD",
            url,
            expect=expect,
            query=query,
            headers=headers,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )

    @staticmethod
    def options(
        url: str | Expr[str],
        *,
        expect: _Expect[TaskValueT],
        query: HttpQuery | None = None,
        headers: HttpHeaders | None = None,
        timeout_ms: int | None = None,
        credentials: HttpCredentials | None = None,
    ) -> TaskLike[HttpResponse[TaskValueT], HttpError]:
        return Http.request(
            "OPTIONS",
            url,
            expect=expect,
            query=query,
            headers=headers,
            timeout_ms=timeout_ms,
            credentials=credentials,
        )
