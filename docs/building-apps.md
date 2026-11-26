# Building interactive apps

Fleur compiles a Python component into HTML and JavaScript. The browser holds the model,
sends a message when an event occurs, and updates the view after the corresponding message
handler changes the model. The [quick start](../README.md#quick-start) shows this loop with
a counter.

## Keep input and preview in sync

Save this example as `editor.py`. The input reads its value from the model and dispatches
`CHANGE` on each edit. The update reads `event.value` and writes it back to the model.

```python
from fleur import Component, Cond, Model, Msg, MsgGroup, State, String
from fleur.core import InputEvent, PointerEvent
from fleur.ui import Button, Input, Text, VStack


class EditorModel(Model):
    name: State[str]


class EditorMsg(MsgGroup):
    CHANGE: Msg[InputEvent] = Msg()
    CLEAR: Msg[PointerEvent] = Msg()


def app() -> Component[EditorModel, EditorMsg]:
    is_blank = Cond.equal(String.trim(EditorModel.name), "")
    return Component(
        EditorModel(name=""),
        EditorMsg.cases(
            EditorMsg.CHANGE.then(State.set(EditorModel.name, EditorMsg.CHANGE.event.value)),
            EditorMsg.CLEAR.then(State.set(EditorModel.name, "")),
        ),
        VStack(
            Input(
                value=EditorModel.name,
                oninput=EditorMsg.CHANGE,
                props={"aria-label": "Display name"},
            ),
            Text(Cond.when(is_blank, "Enter a display name.", "Preview: " + EditorModel.name)),
            Button("Clear", onclick=EditorMsg.CLEAR, props={"disabled": is_blank}),
            gap="sm",
        ),
    )
```

```bash
uv run fleur dev editor:app
```

Open `http://127.0.0.1:8000`. Typing updates the preview and the Clear button empties the
input. A class-level field such as `EditorModel.name` represents the current browser value.
Use `Cond.when` to branch on that value at runtime. For a list or table of controls,
`Msg[PointerEvent, int]` can carry an item index through `Message.SELECT.bind(index)`.
The handler reads the index through `Message.SELECT.context`.

## Compose two independent components

Save the following as `workspace.py` next to `editor.py`. Each editor gets its own nested model
field and its own parent message. `View.forward` connects the child view to those two fields.
`Update.forward` runs the child update and stores its result in the corresponding model field.

```python
from fleur import Component, Model, Msg, MsgGroup, State, Update, View
from fleur.ui import Text, VStack

from editor import EditorModel, app as editor


class WorkspaceModel(Model):
    first: State[EditorModel]
    second: State[EditorModel]


class WorkspaceMsg(MsgGroup):
    FIRST = Msg()
    SECOND = Msg()


def app() -> Component[WorkspaceModel, WorkspaceMsg]:
    first = editor()
    second = editor()
    return Component(
        WorkspaceModel(first=first.init.model, second=second.init.model),
        WorkspaceMsg.cases(
            WorkspaceMsg.FIRST.then(Update.forward(WorkspaceModel.first, first, WorkspaceMsg.FIRST)),
            WorkspaceMsg.SECOND.then(Update.forward(WorkspaceModel.second, second, WorkspaceMsg.SECOND)),
        ),
        VStack(
            Text("First editor"),
            View.forward(WorkspaceModel.first, first.view, WorkspaceMsg.FIRST),
            Text("Second editor"),
            View.forward(WorkspaceModel.second, second.view, WorkspaceMsg.SECOND),
            gap="md",
        ),
    )
```

The parent owns initialization. This example copies each child's initial model. If a child
also needs a startup command or subscriptions, wire them into the parent explicitly.

## Generate and serve HTML

Use the CLI to build the component factory with the default page and theme.

```bash
uv run fleur build workspace:app -o dist/index.html
```

Call `bloom` from Python when you need page metadata or a custom theme.

```python
from pathlib import Path

from fleur import Page, bloom
from fleur.ui import ZEN_THEME

from workspace import app

output = Path("dist/index.html")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    bloom(app, page=Page(title="Editor workspace"), theme=ZEN_THEME),
    encoding="utf-8",
)
```

Serve the generated directory with any static HTTP server. To preview it locally, run
`uv run python -m http.server 8000 --directory dist` and open `http://127.0.0.1:8000`.
Both editors should accept input independently. The generated page includes the browser runtime.

- [Theming and styling](theming-and-styling.md) covers palette and CSS customization.
- [Making HTTP requests](http-requests.md) adds browser requests and result handling.
