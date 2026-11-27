# Making HTTP requests

`Http.get` describes a request. Schedule it with `Cmd.task` in an update case to run it in
the browser. The command dispatches a message carrying either an `HttpResponse` or an `HttpError`.

## Load a text resource

Save this component as `status.py`. It disables the refresh button while a request is pending
and displays the response body after a successful request.

```python
from fleur import Cmd, Component, Cond, Http, HttpError, HttpResponse, Model, Msg, MsgGroup, State
from fleur.core import PointerEvent
from fleur.ui import Button, Text, VStack


class StatusModel(Model):
    pending: State[bool]
    text: State[str]


class StatusMsg(MsgGroup):
    REFRESH: Msg[PointerEvent] = Msg()
    RECEIVED: Msg[HttpResponse[str]] = Msg()
    FAILED: Msg[HttpError] = Msg()


def app() -> Component[StatusModel, StatusMsg]:
    return Component(
        StatusModel(pending=False, text="Refresh to check the service."),
        StatusMsg.cases(
            StatusMsg.REFRESH.then(
                (
                    State.set(StatusModel.pending, True) & State.set(StatusModel.text, "Loading…"),
                    Cmd.task(
                        Http.get("/status.txt", expect=Http.expectText(), timeout_ms=4000),
                        ok=StatusMsg.RECEIVED,
                        err=StatusMsg.FAILED,
                    ),
                )
            ),
            StatusMsg.RECEIVED.then(
                State.set(StatusModel.pending, False)
                & State.set(
                    StatusModel.text,
                    Cond.when(
                        StatusMsg.RECEIVED.event.ok,
                        StatusMsg.RECEIVED.event.body,
                        "Could not load the service status.",
                    ),
                )
            ),
            StatusMsg.FAILED.then(
                State.set(StatusModel.pending, False)
                & State.set(StatusModel.text, StatusMsg.FAILED.event.message)
            ),
        ),
        VStack(
            Button("Refresh", onclick=StatusMsg.REFRESH, props={"disabled": StatusModel.pending}),
            Text(StatusModel.text, props={"role": "status"}),
            gap="sm",
        ),
    )
```

Build the page, add its text resource and serve them from the same origin.

```bash
uv run fleur build status:app -o dist/index.html
echo "All systems operational" > dist/status.txt
uv run python -m http.server 8000 --directory dist
```

Open `http://127.0.0.1:8000` and click Refresh.

## Send values from the model

The URL, query, headers and body accept values read from the model. Build a path with
parameters through `Url.path`, which fills `{name}` placeholders (the same form as OpenAPI
paths) with percent-encoded values. A placeholder without a parameter, or a parameter without
a placeholder, raises `ValueError` when the update is built.

```python
from fleur import Http, Url

save = Http.put(
    Url.path("/todos/{id}", id=Editor.todo_id),
    expect=Http.expectJson(),
    query={"notify": True},
    headers={"Authorization": "Bearer " + Editor.token},
    body={"title": Editor.title, "done": False},
)
```

Schedule `save` with `Cmd.task` like any other request. The runtime appends `query` to the
URL with `URLSearchParams`, keeping an existing query string and fragment. A body that is not
a string is sent as JSON with `Content-Type: application/json` unless you set that header.
Values inside the body may come from the model at any depth.

## Decode typed JSON

Pass a type to `Http.expectJson` to receive the body as that type. Declare the response model
with `State` fields, like any other model.

```python
class Todo(Model):
    id: State[int]
    title: State[str]
    note: State[str | None]

load = Http.get("/todos", expect=Http.expectJson(list[Todo]))
# Declare LOADED as Msg[HttpResponse[list[Todo]]].
```

The runtime checks the body against the type, like an Elm JSON decoder. A field of another
type or a missing required field fails with `HttpError(kind="decode")`, whose message locates
the mismatch, for example `body[0].title: expected string, got integer`. Extra fields are
ignored, and a missing field whose type allows `None` reads as `None`. A typed body describes a
successful response, so a status other than 2xx fails with `HttpError(kind="status")` instead
of reaching the response handler.

A decoded body and the items of a model list are seen as instances of their model, so read
their fields as attributes: `Actions.LOADED.event.body.title`, or
`Array.map(Board.todos, lambda todo: Text(todo.title))`. A misspelled field is a type error.

Supported types are `str`, `int`, `float`, `bool`, `None`, `Literal[...]`, unions, `list[T]`,
`Mapping[str, T]` and models. Another type raises `TypeError` when the request is built.

## Handle responses and failures

- A request using `Http.expectText()` returns `HttpResponse[str]`. `Http.expectJson()` without a
  type returns `HttpResponse[JsonValue]` and does not check the body.
- Without a type, a decoded HTTP response arrives in the response handler even for a 404 or
  500. Use `response.ok`, `response.status`, or `response.status_text` to choose what to display.
- A network failure, timeout, abort, or decoding failure arrives in the error handler.
  Read `error.kind` for the category and `error.message` for details. The status fields
  are `None` when a response is unavailable.

Requests use the browser's fetch API and follow its CORS rules. Use relative URLs for resources
served alongside the app. A cross-origin endpoint must allow the page's origin.
