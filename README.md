# 💐 Fleur

Fleur is an Elm-like architecture for Python-first frontend apps.

You define `Model`, `Msg`, `update`, and `view` in Python, and Fleur compiles your component into browser-executable JavaScript and HTML.

## Installation

```bash
uv sync
```

## Quick start

Create an `app.py` that prints `bloom(App)`, then generate HTML:

```bash
uv run python app.py > app.html
python -m http.server 8000
```

Then open `http://localhost:8000/app.html`.

## Example

```python
from fleur import Component, Model, Msg, MsgGroup, State, bloom
from fleur.ui import Button, Text, VStack


class CounterModel(Model):
    count: State[int]


class CounterMsg(MsgGroup):
    INC = Msg()
    DEC = Msg()


def App() -> Component[CounterModel, CounterMsg]:
    init = CounterModel(count=0)
    update = CounterMsg.caseof(
        CounterMsg.INC(CounterModel.count.set(CounterModel.count + 1)),
        CounterMsg.DEC(CounterModel.count.set(CounterModel.count - 1)),
    )
    view = VStack(
        Text(f"Count: {CounterModel.count}"),
        Button("+", onclick=CounterMsg.INC),
        Button("-", onclick=CounterMsg.DEC),
        gap="sm",
    )
    return Component(init, update, view)


html = bloom(App)
```

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
