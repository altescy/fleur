# Building interactive apps

Fleur compiles a Python component into HTML and JavaScript. The browser holds the model,
sends a message when an event occurs, and updates the view after the corresponding message
handler changes the model. The [quick start](../README.md#quick-start) shows this loop with
a counter.

Omit `from __future__ import annotations` in modules that declare a `Model` with `State` fields.
Fleur registers these fields from runtime annotations. The future import stores the annotations as
strings, so passing those fields to the model constructor raises `TypeError: Unknown model fields`.

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

## Handle a form submission

Use `Form(..., onsubmit=Messages.SAVE, prevent_default=True)` to update the current page on
submit. Declare `SAVE` as `Msg[SubmitEvent]` (from `fleur.core`) and place a
`Button("Save", props={"type": "submit"})` inside the form. Clicking the button and pressing
Enter in a text input both trigger the same message after native form validation.
Omitting `prevent_default` or setting it to `False` allows the browser's normal submission.
The flag also accepts a boolean model expression.

## Group related form controls

Use `Fieldset` to group controls under a native legend. Pass its accessible
name with `label`. The `disabled` flag can be a boolean or a model expression.

```python
Fieldset(
    field(id="book-title", label="Book title", control=lambda attrs: Input(props=attrs)),
    CheckboxField("Mark as a favorite"),
    label="Book details",
    disabled=Screen.book_details_locked,
)
```

While the fieldset is disabled, the browser skips its controls in the Tab order
and excludes them from native form submission. The controls retain their values
when the fieldset is enabled again.

## Open and close a modal dialog

`Dialog` takes a boolean `open` value and an `onclose` message. Set the flag to open or close
the modal from an update. Handle the native close event by setting the flag to false so Escape
and buttons in a `Form(props={"method": "dialog"})` also update your model.

```python
from fleur import Component, Model, Msg, MsgGroup, State
from fleur.core import DialogCloseEvent, PointerEvent
from fleur.ui import Button, Dialog, Form, Heading, VStack


class Settings(Model):
    editing: State[bool]


class Actions(MsgGroup):
    EDIT: Msg[PointerEvent] = Msg()
    CLOSED: Msg[DialogCloseEvent] = Msg()


def app() -> Component[Settings, Actions]:
    return Component(
        Settings(editing=False),
        Actions.cases(
            Actions.EDIT.then(State.set(Settings.editing, True)),
            Actions.CLOSED.then(State.set(Settings.editing, False)),
        ),
        VStack(
            Button("Edit settings", onclick=Actions.EDIT),
            Dialog(
                Heading("Settings", level=2, props={"id": "settings-title"}),
                Form(Button("Done", props={"type": "submit", "autofocus": True}), props={"method": "dialog"}),
                open=Settings.editing,
                onclose=Actions.CLOSED,
                props={"aria-labelledby": "settings-title"},
            ),
        ),
    )
```

The dialog opens with `showModal()`. The browser focuses the element marked `autofocus`
and restores focus to the previously focused element when the dialog closes.

## Confirm an operation

Use `AlertDialog` when the user needs to confirm an important operation. Give it a
unique `id`, a title, and a short description of the consequence. The dialog uses
these to provide its accessible name and description.

```python
AlertDialog(
    id="clear-notes",
    title="Clear reading notes?",
    description="This will permanently remove the current reading notes.",
    confirm_label="Clear notes",
    open=Screen.confirming,
    onclose=Actions.CLOSE_CONFIRMATION,
    onconfirm=Actions.CLEAR_NOTES,
)
```

The dialog places focus on Cancel when it opens. Cancel, Escape, and confirmation
all close it and return focus to the opening control. Declare `CLOSE_CONFIRMATION`
as `Msg[DialogCloseEvent]` and clear the open flag in its update.
Declare `CLEAR_NOTES` as `Msg[SubmitEvent]` and perform the operation in its update.

## Open a non-modal popover

Give the panel a unique `id` and forward the trigger attributes to a native button.
The button opens the panel with a click, Enter, or Space. Escape or a click outside
closes it. Add `autofocus` to the control that should receive focus on opening.

```python
Popover(
    Input(props={"aria-label": "Book title", "autofocus": True}),
    id="book-editor",
    trigger=lambda attrs: Button("Edit book", props=attrs),
)
```

The browser manages this example's visibility. To control it from the model, pass
`open=Screen.editing` and `ontoggle=Actions.TOGGLE`. Declare `TOGGLE` as
`Msg[ToggleEvent]` from `fleur.core` and set `Screen.editing` to
`Actions.TOGGLE.event.open` in the update. See the reading notes editor in the
[component gallery](../examples/component_gallery.py).

## Offer actions in a menu

Use `Menu` with `MenuItem` children and a unique `id`. Forward the trigger attributes to a
native button. Each item dispatches its own `Msg[PointerEvent]`.

```python
Menu(
    MenuItem("Edit notes…", onclick=Actions.EDIT),
    MenuItem("Clear notes", onclick=Actions.CLEAR, disabled=Screen.notes_empty),
    id="note-actions",
    trigger=lambda attrs: Button("Note actions", variant="secondary", props=attrs),
)
```

Enter, Space and Down Arrow open the menu at the first item. Up Arrow opens it at the
last item. Use the arrow keys, Home or End to move, and Enter or Space to select.
Escape and selection close the menu and return focus to its button. Tab closes the menu
and continues through the page. Disabled items remain focusable and cannot be selected.
The [component gallery](../examples/component_gallery.py) shows how an action opens an editor.

## Group action menus in a menubar

Pass `Menu` instances with native button triggers to a labelled `Menubar`.
Each menu exposes its own commands through `MenuItem`.

```python
Menubar(
    Menu(
        MenuItem("Edit notes…", onclick=Actions.EDIT),
        id="note-actions",
        trigger=lambda attrs: Button("Note", variant="ghost", props=attrs),
    ),
    Menu(
        MenuItem("Large text", onclick=Actions.LARGE_TEXT),
        id="view-actions",
        trigger=lambda attrs: Button("View", variant="ghost", props=attrs),
    ),
    label="Reading note commands",
)
```

Tab enters the menubar at its last focused menu button. Left and Right Arrow
move between buttons and switch menus while a menu is open. Up and Down Arrow
move within a menu. Escape closes the menu and returns focus to its button.

## Offer actions on a focused region

Use `ContextMenu` with `MenuItem` children when a set of actions belongs to a
particular region. Forward the trigger attributes to the view that should receive
right-click and keyboard events. Give the trigger an accessible name.

```python
ContextMenu(
    MenuItem("Edit notes…", onclick=Actions.EDIT_NOTES),
    id="notes-context",
    trigger=lambda attrs: Box(
        Text(Screen.notes),
        props={**attrs, "role": "group", "aria-label": "Reading note"},
    ),
)
```

Right-click opens the menu at the pointer. Shift+F10 and the Context Menu key open
it near the focused region. Escape closes it and returns focus to the target.
The [component gallery](../examples/component_gallery.py) also offers the same
actions through a visible menu button.

## Add a tooltip to a control

Use `Tooltip` for a short, supplemental description. Give it a unique `id` and
forward the trigger attributes to a focusable control. The attributes associate the
description with that control through `aria-describedby`.

```python
Tooltip(
    "Favorites appear in your saved reading list.",
    id="favorites-hint",
    trigger=lambda attrs: Toggle("Favorite", pressed=Screen.favorite, onchange=Actions.FAVORITE, props=attrs),
)
```

The description appears on keyboard focus or after a brief hover. The pointer can
move onto the description while it is visible. Escape dismisses it without moving
focus. Use visible text for information readers need to complete an action.

## Preview a link destination

Use `PreviewCard` with a `Link` trigger and display content such as `Text`.
The card appears on hover or keyboard focus. Escape dismisses the card and
Enter follows the link.

```python
PreviewCard(
    Text("Reading notes", font_weight=600),
    Text(Screen.notes),
    trigger=Link("Reading notes", href="#reading-notes"),
)
```

The card content is hidden from assistive technology and stays out of the Tab
order. Include the previewed information at the destination so it is available
when readers follow the link.

## Toggle a setting

Use `Switch` for an on/off setting that applies immediately. Keep its label steady
as the setting changes. The label is clickable, and Space toggles the focused switch.

```python
Switch("Dark mode", checked=Settings.dark, onchange=Actions.MODE)
```

Declare `MODE` as `Msg[InputEvent]` and update the setting with
`State.set(Settings.dark, Actions.MODE.event.checked)`.

## Filter and select a choice

Give `Combobox` a unique input `id`, a visible label, and a mapping of keys to labels.
The mapping can also be a Fleur model expression. Pass the model's selected key as
`value`. Use `None` when no choice is selected.

```python
Combobox(
    {"garden": "The Secret Garden", "willows": "The Wind in the Willows"},
    id="catalog-title",
    label="Book title in catalog",
    value=Screen.book,
    onselect=Actions.SELECT_BOOK,
    placeholder="Type part of a title",
)
```

Declare `SELECT_BOOK` as `Msg[PointerEvent, str]`. A click or Enter on a highlighted
option sends its key in `Actions.SELECT_BOOK.context`. Typing narrows the list, and
Escape or leaving the field restores the last confirmed label. The arrow keys move
the highlight while focus stays in the input.

## Adjust a value within a range

Use `Slider` to choose a single number. Set `min`, `max`, and `step` to
define the range. Give the input a visible label using `field()` or use
the `label` argument for an accessible name.

```python
Slider(label="Reading text size", min=14, max=30, step=2, value=Screen.font_size, oninput=Actions.RESIZE)
```

Declare `RESIZE` as `Msg[InputEvent]`. For a live preview, pass the message to
`oninput` and update the model using `Number.from_string(Actions.RESIZE.event.value)`.
Use `onchange` for updates when the user commits a value.

## Show a temporary notification

Keep `Toast` in the view and show it with an `open` flag. Declare `CLOSE_TOAST`
as `Msg[ToastCloseEvent]` and set the flag to false in its update. The message
can read `event.reason` to distinguish a timeout from dismissal.

```python
Toast(
    "Added to your reading list.",
    open=Screen.toast_open,
    onclose=Actions.CLOSE_TOAST,
)
```

The toast announces its message politely and leaves focus in place when it appears.
The default display time is 5 seconds. Pass `duration_ms` to change it or use
`duration_ms=None` to keep the toast open until dismissal. The timer pauses while the
pointer is over the toast or its button has focus, then resumes with the remaining time.
Use `dismiss_label` to set the accessible name of the close button.

## Group related disclosures

Place `AccordionItem` views directly inside an `Accordion`. Opening an item closes
the previously open item in that group. Use `initial_open=True` on one item to show
its content when the group first renders.

```python
Accordion(
    AccordionItem("Adding a book", Text("Choose Add to reading list."), initial_open=True),
    AccordionItem("Editing notes", Text("Open Note actions and choose Edit notes.")),
)
```

Enter and Space toggle the focused summary. Up and Down Arrow move between summaries,
and Home and End move to the first or last summary.

## Group related controls in a toolbar

Use `Toolbar` to group buttons and links under one accessible label. Tab enters
the toolbar at the last focused control, or at the first available control on the
first visit. Left and Right Arrow move between controls in a horizontal toolbar.
Use `orientation="vertical"` for a toolbar with Up and Down Arrow navigation.
Home and End move to the first or last available control.

```python
Toolbar(
    Button("Left", onclick=Actions.ALIGN.bind("left"), props={"type": "button"}),
    Button("Center", onclick=Actions.ALIGN.bind("center"), props={"type": "button"}),
    Button("Right", onclick=Actions.ALIGN.bind("right"), props={"type": "button"}),
    label="Reading title alignment",
)
```

The controls keep their own activation behavior. When a button represents a
setting, bind `aria-pressed` to the model so the current choice is exposed.

## Toggle a pressed button

Use `Toggle` for an independent button with two states, such as a favorite.
Pass the current state as `pressed` and keep the button's accessible name stable.
Click, Enter, and Space all activate the native button.

```python
Toggle("Favorite", pressed=Screen.favorite, onchange=Actions.FAVORITE)
```

Declare `FAVORITE` as `Msg[PointerEvent, bool]`. Its context is the next pressed
state. Apply it with `State.set(Screen.favorite, Actions.FAVORITE.context)`.
The button exposes the model's state through `aria-pressed`.

## Toggle multiple choices

Use `ToggleGroup` when several choices can be pressed together. Give the group a
label, a mapping of keys to captions, and the current selection as a sequence of
keys.

```python
ToggleGroup(
    {"bold": "Bold", "italic": "Italic"},
    label="Title emphasis",
    value=Screen.emphasis,
    onchange=Actions.EMPHASIS,
)
```

Declare `EMPHASIS` as `Msg[PointerEvent, Sequence[str]]` and update the model
with `State.set(Screen.emphasis, Actions.EMPHASIS.context)`. The message context
contains the complete new selection. Arrow keys move focus, and Enter or Space
toggles the focused choice. Inside a `Toolbar`, the group shares the toolbar’s
tab stop and arrow-key navigation.

## Show a profile image with a fallback

Pass `Avatar` a display name, image source and fallback initials. The initials
appear while the image loads, when it fails, or when the source is absent. The
avatar keeps the same accessible name and occupies the same space in each state.

```python
Avatar(name="Lead reviewer", src=Screen.reviewer_image, fallback="LR")
```

Use `name=None` for a decorative avatar when adjacent text already provides
the display name.

## Scroll within part of the page

Use `ScrollArea` when content needs its own scrollable region. Give the region
a label and constrain its size with a layout property such as `max_h`.

```python
ScrollArea(log_entries, label="Activity log", max_h=css("20rem"))
```

Tab moves focus into the region. The browser handles scrolling by keyboard,
wheel, or touch. Horizontal scrolling is available for content such as code
whose long lines extend beyond the region.

## Select multiple checkboxes

Give `CheckboxGroup` a group label, a mapping of value keys to checkbox labels,
and the selected keys from your model. Each checkbox keeps its native label and
its place in the Tab order.

```python
CheckboxGroup(
    {"to-read": "To read", "reading": "Reading", "finished": "Finished"},
    label="Shelves to show",
    value=Screen.visible_shelves,
    onchange=Actions.FILTER_SHELVES,
)
```

Declare `FILTER_SHELVES` as `Msg[InputEvent, Sequence[str]]` and update the model
with `State.set(Screen.visible_shelves, Actions.FILTER_SHELVES.context)`. The
context contains all selected keys. For native form submission, pass a shared
`name` to submit each checked key under that name.

## Enter a number with step controls

Use `NumberField` for direct numeric input with increase and decrease buttons.
Pass `min`, `max`, `step`, and `required` to configure native form validation.
The buttons and arrow keys use the browser's numeric step behavior.

```python
field(
    id="amount",
    label="Amount (JPY)",
    control=lambda attrs: NumberField(
        value=Screen.amount,
        min=1,
        step=1,
        required=True,
        oninput=Actions.AMOUNT,
        input_props=attrs,
    ),
)
```

The input message carries the value as a string, including an empty string when
the field is blank. Use `input_props` for the input’s label and error
associations, and `increase_label` or `decrease_label` to name the buttons.

## Display a measurement within a range

Use `Meter` to display a measurement such as storage usage. Set `min` and `max`
for the range. The optional `low`, `high`, and `optimum` values let the browser
distinguish between more and less desirable measurements.

```python
Meter(value=Screen.storage_used, min=0, max=100, low=60, high=85, optimum=0, label="Storage usage")
```

Give the meter an accessible name with `label` or reference a visible label
with `aria-labelledby` in `props`. Use `aria-describedby` to associate the meter
with additional information, such as a visible value with units.

## Group navigation links

Use `NavigationMenu` to present groups of links in a named navigation landmark.
Give each `NavigationMenuGroup` a unique `id` for its link list.

```python
NavigationMenu(
    NavigationMenuGroup(
        "Library",
        Link("Books", href="/books"),
        Link("Authors", href="/authors"),
        id="library-navigation",
    ),
    label="Main navigation",
)
```

Enter or Space on a group button toggles its links. Tab moves between visible
links and buttons. Escape closes the open group and returns focus to its button.
Links use the browser's normal navigation, including fragment links.
Set `auto_close=False` for a sidebar that should stay open when a link is
followed or focus leaves the navigation.
With `multiple=True`, several groups can stay open together. Escape closes
the group that contains focus and returns focus to its button.

## Work with browser values

Use `Array.length` to count items, `Array.sum` to total numeric values, and `Array.join` to
combine strings. Use `Array.map` first when each item contains a numeric field to sum.

```python
from fleur import Array, Number, String, Url
from fleur.core import array

total = Array.sum(array([1200, 800]))
highest_first = Array.sort_by(array([900, 1200]), lambda amount: amount, descending=True)
label = Number.format(total, locale="ja-JP")
line = Array.join(array(["Travel", String.from_number(total)]), ",")
encoded = Url.encode_component(line)
```

`Array.sort_by(items, key, descending=False)` returns a sorted copy. Supply a numeric key
for amounts or a string key for lexical ordering (including ISO dates). Equal keys keep
their input order in either direction. The `descending` flag can follow a model field.

`Number.from_string` uses JavaScript's number conversion rules. Empty text becomes zero,
and invalid text becomes `NaN`. Use `Number.is_finite` and any application constraints to
validate an input. Use `String.replace_all` for text such as quoted CSV fields, and
`String.from_number` to generate numeric text without locale formatting.
The [expense report example](../examples/expense_report.py) combines these operations.

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
