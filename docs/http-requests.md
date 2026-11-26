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

## Handle responses and failures

- A request using `Http.expectText()` returns `HttpResponse[str]`. Use `Http.expectJson()`
  for a response whose body is a `JsonValue`.
- A decoded HTTP response arrives in the response handler even for a 404 or 500.
  Use `response.ok` or `response.status` to choose what to display.
- A network failure, timeout, abort, or decoding failure arrives in the error handler.
  Read `error.kind` for the category and `error.message` for details.

Requests use the browser's fetch API and follow its CORS rules. Use relative URLs for resources
served alongside the app. A cross-origin endpoint must allow the page's origin.
