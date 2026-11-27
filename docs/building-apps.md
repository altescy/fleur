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
declare a message such as `SELECT: Msg[PointerEvent, int]` and bind an item index with
`EditorMsg.SELECT.bind(index)`. The handler reads the index through `EditorMsg.SELECT.context`.
An event handler dispatches the message as is, so the type checker rejects an unbound
`onclick=EditorMsg.SELECT` that would leave the context empty.

The type checker also follows every message through the view tree. A view that dispatches a
message of another `MsgGroup`, whether through a component argument, a nested child, a
mapped list, or raw `props`, does not match the component's update. The same applies to
`Cmd.task`, `Cmd.map` and `Sub.interval`. Use `View.map` or `View.forward` to embed a child
component with its own message group.

Like an Elm `case`, `cases()` must handle every message of the group and raises a
`ValueError` naming any it misses. Use `State.unchanged()` for a message that needs no state
change. A click handler may also take a `Msg[None]` when the update does not read the event.

Enable `strictListInference` (and `strictDictionaryInference`) in your Pyright configuration.
Without it, a list that mixes views of different groups is inferred as `list[Unknown]` and
escapes the check. Raw `props` check the message group and the bound context, but not that an
`"onclick"` key receives a pointer event; prefer the typed component arguments or
`EventBinding.on` for that.

## Handle a form submission

Use `Form(..., onsubmit=EditorMsg.SAVE, prevent_default=True)` to update the current page on
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
                labelledby="settings-title",
            ),
        ),
    )
```

Name every dialog with `labelledby`, the id of its visible title, or with `label`;
the type checker rejects a `Dialog` without either. The dialog opens with
`showModal()` and focuses the element marked `autofocus`.
Escape restores focus to the button that opened the dialog. For model changes
without an activating button, the browser uses the previously focused element.

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
closes it. Escape returns focus to the opening button when focus is still in the
panel. Add `autofocus` to the control that should receive focus on opening.

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
`duration_ms=None` to keep the toast open until dismissal. Use a `State[int | None]`
field when the duration can change while the toast is open. The timer pauses while the
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

## Add DOM behavior to a custom view

Use `EventBinding` for actions that must run during a browser event. A binding
can cancel the browser's default action, perform a `DomAction`, and dispatch a
message. Use `EventBinding.on()` with a descriptor from `DomEvents` for native
events. For example, a keyboard callback receives a `DomKeyboardEvent` and
can send a message declared with `KeyboardEvent`. A plain event named
`keydown` without keyboard data does not call the typed binding.
Pass `capture=True` when the binding needs the capture phase.

```python
from fleur import View
from fleur.core import DomEvents, EventBinding

search = View(
    View(tag="input", props={"aria-label": "Search"}),
    View("Focus search", tag="button", props={"type": "button"}),
    tag="section",
    props=EventBinding.on(
        DomEvents.click,
        action=lambda event: event.current_target.query("input").focus(),
    ),
)
```

Use `EventBinding(...).properties("event-name")` for custom events. For
example, check that `event.detail_text` is present in `when` before including
it in the message's `payload`. The generic event reference returns `None`
for unavailable values such as the key of a mouse event.

Attach element-scoped effects with `View.dom_effect(*effects)`. A view can
combine effect props from several helpers with `View.extend_props`. Distinct
effect keys coexist. A later prop with the same key takes that slot. Across
renders, the same key identifies the same installed behavior. Change its
dependencies to supply new values, or use a new key to install a different effect.
Adding or removing an effect preserves the element, its focus, and unsaved
input values as long as the view keeps the same element identity.

`DomEffect(key, update, ...)` runs its update once the element is connected. List the model
expressions the update reads in `dependencies` so it runs again when their values
change. Use `watch_subtree=True` to also update after patches to the element
or its descendants. An optional `mount` runs once per installation, and
`dispose` runs when the effect or element is removed. Use
`after_connect=False` for operations such as linking IDs that must be ready
as soon as rendering returns.

The Python callbacks describe browser actions. Use `DomAction.when` to branch
on a browser value and `DomAction.batch` to run actions in order. Use
`DomAction.when_some(value, action)` to evaluate an optional expression once
and pass its present value to a typed action. Both `None` and a missing value,
such as an absent mapping key, run the `otherwise` action. Element references from event
targets and queries are local to those callbacks. Check `exists` when you need
to distinguish a missing element.

Use `DomEffect.scoped(key, setup)` when an effect owns listeners, timers, or
browser-local state. Its setup callback receives the element and a `DomScope`
and returns a `DomLifecycle`. Use `scope.input(Screen.caption)` in setup to
read the latest value of a render-time expression. It retains the expression's
type as a read-only input. Inputs are evaluated during rendering, so pass model
expressions such as `Screen.caption + "!"`, not values created inside the effect;
`scope.input(caption + "!")` with another input raises a `ValueError` when the
view compiles. Conversely, the setup must not read model fields or items of a
mapped view directly: a scoped effect is installed once, so such a value would
keep its first value. That also raises a `ValueError`; read it through `scope.input()`. The first values are available during mount.
When an input changes, the installed effect receives all current inputs before
its update runs, and its existing listeners read those values on subsequent events.
Allocate mutable browser-local values with `scope.value()` and element
references with `scope.reference()`. Use `scope.on()` and `scope.on_document()`
with the same descriptors as `EventBinding.on()`. For custom event names,
use `scope.listen()` or `scope.document_listener()`. A listener is attached to the
element its target resolves to at installation, so listen on the effect's root, the
document, or a child the view never replaces, and use `event.target.closest(...)` to
handle descendants that can change. The scope releases listeners and cancels its
timers when the view is removed.

### Reuse a DOM read within an action

A Python variable can name a DSL expression such as `panel.bounds`, but each
use of that expression can read the DOM again when the action runs. These
helpers evaluate the expression once in the browser, just before running the
actions described by the callback.

| What you want to reuse | Helper | What the callback receives |
| --- | --- | --- |
| A value such as a boolean, string, or number | `DomAction.with_value(expr, action)` | The result as an `Expr[T]` |
| One element found by a query or index | `element.with_reference(action)` | The resolved `DomElement` |
| The members and order of a collection | `elements.with_snapshot(action)` | The resolved `DomElements` |
| The geometry of an element at one moment | `bounds.with_snapshot(action)` | One measured `DomBounds` |

**Toast** captures whether focus is inside the popup before hiding it. Hiding
the popup can move focus, so the decision to restore focus uses the earlier
boolean. [Toast implementation](../src/fleur/ui/views/_toast_behavior.py)

```python
from fleur.core import Cond, DomAction, DomElement


def hide_toast(root: DomElement, popup: DomElement, previous_focus: DomElement) -> DomAction:
    return DomAction.with_value(
        popup.contains(root.active_element),
        lambda restore_focus: DomAction.batch(
            popup.set_hidden(True),
            DomAction.when(
                Cond.every(restore_focus, previous_focus.connected),
                previous_focus.focus(prevent_scroll=True),
            ),
        ),
    )
```

**Combobox** uses both a snapshot and a reference. Its ArrowDown handler
uses one collection of visible options to find the active option's index,
count the choices, and pick the next option. It then resolves that option once
to mark it active and scroll it into view. [Combobox implementation](../src/fleur/ui/views/_overlay_behavior.py)

```python
from collections.abc import Callable

from fleur.core import DomAction, DomElement, DomElements, Number


def move_down(
    matches: DomElements,
    active: DomElement,
    set_active: Callable[[DomElement], DomAction],
) -> DomAction:
    def move(items: DomElements) -> DomAction:
        next_index = Number.clamp(items.index_of(active) + 1, 0, items.length - 1)
        return items.at(next_index).with_reference(
            lambda option: DomAction.batch(set_active(option), option.scroll_into_view())
        )

    return matches.with_snapshot(move)
```

A reference fixes which node is used. A collection snapshot fixes the nodes
and their order. Properties on those nodes are still live, so use `with_value`
for a property you need to remember across a DOM change. For geometry, take a
snapshot after the layout change you want to measure. **ContextMenu** uses
`panel.bounds.with_snapshot(...)` after opening the panel so it can use the
width and height from the same measurement to fit the menu in the viewport.
[ContextMenu implementation](../src/fleur/ui/views/_menu_behavior.py)

### Request focus from an update

Use a command when an application message decides where focus should move.
For example, this update reveals an editor whose input has `id="editor"`
and requests focus after the view renders.

```python
from fleur import Cmd, State
from fleur.core import Dom

Actions.EDIT.then(
    (
        State.set(Screen.editing, True),
        Cmd.task(Dom.focus("editor", prevent_scroll=True), Actions.FOCUSED, Actions.FOCUS_FAILED),
    )
)
```

Declare `FOCUSED` as `Msg[None]` and `FOCUS_FAILED` as `Msg[DomFocusError]`.
The failure message carries `"not_found"` or `"not_focusable"`. Use a
view effect for behavior tied to the lifetime of a particular element.

To run several commands from one case, combine them with `Cmd.batch`, for example
`(State.set(...), Cmd.batch(load_profile, Cmd.task(Dom.focus("editor"), ...)))`. Likewise,
pass `Sub.batch(Sub.interval("clock", 1000, Actions.TICK), ...)` as the component's
subscriptions to run several at once. Every batched command or subscription must use the
component's message group, and `Sub.batch` raises `ValueError` when two subscriptions share
a key, because the runtime tells active subscriptions apart by key.

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

`items[index]` and `scores[key]` assume that the item exists, as in Python. When it may be
missing, use `Array.get(items, index)` or `Object.get(scores, key)`. They return
`Expr[T | None]`, so the type checker asks you to handle the missing case, for example with
`Cond.equal(value, None)` or `DomAction.when_some(value, action)`. `Array.get` also
accepts negative indices counted from the end.

`Number.from_string` uses JavaScript's number conversion rules. Empty text becomes zero,
and invalid text becomes `NaN`. Use `Number.is_finite` and any application constraints to
validate an input. Use `String.replace_all` for text such as quoted CSV fields, and
`String.from_number` to generate numeric text without locale formatting.
The [expense report example](../examples/expense_report.py) combines these operations.

## Compose two independent components

Save the following as `workspace.py` next to `editor.py`. Each editor gets its own nested model
field and its own parent message. `View.forward` renders the child component from its field,
and `Update.forward` runs the child update and stores its result there. Declare each parent
message with the child's group as its event, as in `FIRST: Msg[EditorMsg]`; the type checker
then matches it, and the field's model type, against the child component.

```python
from fleur import Component, Model, Msg, MsgGroup, State, Update, View
from fleur.ui import Text, VStack

from editor import EditorModel, app as editor


class WorkspaceModel(Model):
    first: State[EditorModel]
    second: State[EditorModel]


class WorkspaceMsg(MsgGroup):
    FIRST: Msg[EditorMsg] = Msg()
    SECOND: Msg[EditorMsg] = Msg()


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
            View.forward(WorkspaceModel.first, first, WorkspaceMsg.FIRST),
            Text("Second editor"),
            View.forward(WorkspaceModel.second, second, WorkspaceMsg.SECOND),
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
