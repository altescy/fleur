# 💐 Fleur

Fleur is an Elm-like architecture for Python-first frontend apps.

You define `Model`, `Msg`, `update`, and `view` in Python, and Fleur compiles your component into browser-executable JavaScript and HTML.

## Installation

```bash
uv sync
```

## Quick start

1. Create an `app.py` with a component factory:

```python
from fleur import Component, Model, Msg, MsgGroup, State
from fleur.core import PointerEvent
from fleur.ui import Button, Text, VStack


class CounterModel(Model):
    count: State[int]


class CounterMsg(MsgGroup):
    INC = Msg[PointerEvent]()
    DEC = Msg[PointerEvent]()


def app() -> Component[CounterModel, CounterMsg]:
    return Component(
        init=CounterModel(count=0),
        update=CounterMsg.cases(
            CounterMsg.INC.then(State.set(CounterModel.count, CounterModel.count + 1)),
            CounterMsg.DEC.then(State.set(CounterModel.count, CounterModel.count - 1)),
        ),
        view=VStack(
            Text(f"Count: {CounterModel.count}"),
            Button("+", onclick=CounterMsg.INC),
            Button("-", onclick=CounterMsg.DEC),
            gap="sm",
        ),
    )
```

2. Start the dev server with hot reload:

```bash
uv run fleur dev app:app
```

Open `http://127.0.0.1:8000`. Edit `app.py` and the page reloads automatically.

3. Build a self-contained HTML file for production:

```bash
uv run fleur build app:app -o app.html
```

See `uv run fleur --help` for more options.

## Development

```bash
make test        # run pytest
make lint        # run ruff and pyright
make build       # build runtime bundle into src/fleur/assets/fleur.js
```

If you need to rebuild the TypeScript runtime directly:

```bash
bun install --cwd runtime
bun run --cwd runtime build
```