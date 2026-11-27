# Theming and styling

## Apply a page theme

```python
from app import app

from fleur import bloom
from fleur.ui import Theme

theme = Theme(light={"primary": "#2457a6"}, dark={"primary": "#91beff"}, space={"lg": 20})
html = bloom(app, theme=theme)
```

The example uses the component factory from the [quick start](../README.md#quick-start).
`BASIC_THEME` is the default. Use `bloom(app, theme=ZEN_THEME)` to try the other built-in preset.

Pass page metadata and additional head markup with `bloom(app, theme=theme, page=page)`.
Existing `page.extra_head_html` entries keep their order. The generated theme stylesheet follows them.

Set `Theme(mode="dark", ...)` to start in dark mode. Each theme applies its shared colors and
then the selected palette. Missing entries inherit from the same mode of `BASIC_THEME`.

## Use tokens and CSS values

```python
from fleur.ui import Box, Button, Text, css

save = Button("Save", bg="primary", p="lg")
preview = Button("Preview", bg=css("oklch(65% 0.2 260)"), px=8)
wide = Box(w="full")
half = Box(w="1/2")
content = Box(max_w=css("min(100%, 42rem)"), mx="auto")
scrollable = Box(Box(w=640), overflow_x="auto")
sidebar = Box(max_h=css("60dvh"), overflow_y="auto")
page_region = Box(min_h=css("100dvh"))
date = Text("2026-11-26", white_space="nowrap")
description = Text("Long description", overflow_wrap="anywhere")
```

Pyright checks built-in tokens and dimension keywords at the call site. Numeric lengths use pixels.
Dimension arguments such as `w`, `h`, `min_h`, and `max_h` accept `"full"` for `100%` and `"fit"`
for `fit-content`. Fractions `"1/2"`, `"1/3"`, `"2/3"`, `"1/4"`, and `"3/4"` also resolve
against the containing block according to CSS percentage sizing rules. Use grid tracks for
columns that must share the available space after subtracting gaps.
Margin arguments such as `mx` accept `"auto"`. Pair `mx="auto"` with a width or maximum width
to center a block. Use `overflow_x="auto"` or `overflow_y="auto"` to scroll when contents exceed
the width or height of the container. Use `white_space="nowrap"` to keep text on one line and
`overflow_wrap="anywhere"` to break long words when needed.
Use `css(...)` for literal or reactive CSS and `style={...}` for CSS declarations.
`Background.when(condition, "primary", "transparent")` checks both names in a reactive color choice.

## Override a region

Use `ThemeScope` to switch modes or override tokens for a subtree. This view binds the region's mode to
Fleur state. Changing `Appearance.mode` updates the region, while elements outside keep the page theme.

```python
from fleur import Model, State
from fleur.ui import Button, ThemeMode, ThemeScope, css

class Appearance(Model):
    mode: State[ThemeMode]

view = ThemeScope(
    Button("Parent"),
    ThemeScope(
        Button("Child"),
        ThemeScope(Button("Grandchild"), colors={"primary": "#21854a"}),
        components={"button": {"bg": "primary"}},
    ),
    components={"button": {"bg": css("#824399")}},
    mode=Appearance.mode,
)
```

Here the parent button stays purple. The child uses the current light or dark primary, and the
grandchild uses green in both modes. Each component property inherits the closest scope's override.
Color and radius tokens resolve against the palette and scale of the region where they are used.

## Switch themes in the browser

A scope can also select a complete theme. Keep the preset key and mode in separate state fields
to change either one while preserving the form, counter and tab state inside the scope.

```python
from typing import Literal

from fleur import Model, State
from fleur.ui import BASIC_THEME, ZEN_THEME, Button, Theme, ThemeMode, ThemeScope

Preset = Literal["basic", "zen"]
presets: dict[Preset, Theme] = {"basic": BASIC_THEME, "zen": ZEN_THEME}

class Settings(Model):
    preset: State[Preset]
    mode: State[ThemeMode]

preview = ThemeScope(
    Button("Save"),
    theme=Theme.select(Settings.preset, presets),
    mode=Settings.mode,
)
```

Pass a `Theme` directly for a fixed region. Use `State.set` in message handlers to update the
preset or mode at runtime. See [Building interactive apps](building-apps.md) for examples of state
updates.

Omitting `mode` inherits the enclosing mode, including the page's initial mode. Omitting `theme`
inherits the enclosing theme. Missing entries in a selected palette use `BASIC_THEME` values for
the same mode. Explicit scope overrides such as `colors` and `components` continue to apply.
Scoped styles use CSS `@scope` and a custom-property container query for inherited dark mode.
In a theme's `extra_css`, use `:scope` to target the region itself.

## Import a shadcn registry theme

Save a shadcn registry item containing `cssVars` as a JSON file, then load it when building
the page. The importer reads the shared, light, and dark palettes and normalizes older HSL
color values. The returned `Theme` can also be a choice in `Theme.select(...)`.

```python
from pathlib import Path

from app import app

from fleur import bloom
from fleur.integrations.shadcn import theme_from_shadcn_registry_json

registry = Path("theme.json").read_text(encoding="utf-8")
theme = theme_from_shadcn_registry_json(registry)
html = bloom(app, theme=theme)
```

## Override component styles

The standard controls and layout views get their defaults from the theme stylesheet.
Set page-wide component defaults with `Theme(components={...})` and region-wide defaults with
`ThemeScope(components={...})`. Both accept the same typed settings, for example
`components={"button": {"bg": "secondary"}, "input": {"radius": "sm"}}`.
Use `css(...)` with a literal CSS value for custom colors or radii, such as `css("#824399")`.

Adjust individual elements with view arguments such as `p="lg"`, `gap="sm"`, and `bg="card"`. Use `css(...)` when
an argument exists and you need a custom CSS value. Use stylesheet rules for media queries
and selectors, or for properties that have no view argument.

Supply a CSS class with `props={"className": "save"}`. A class can set `background` even
when `bg` supplies the themed color.
Input and Button use their own theme focus rings, independently of the background. Button hover tints
its background toward the text color, and Input hover accents its border.
Use `Button(variant="secondary")` for supporting actions or `variant="ghost"` for low-emphasis actions.
Textarea, Divider and Table also resolve their defaults from the theme stylesheet.

Place your stylesheet in `Page.extra_head_html` as a `<style>` or `<link>` element and pass
the page to `bloom`. Class selectors can override default component styles, including
layout defaults on `HStack` and `VStack`.

Inline declarations are applied in order from `props["style"]` to layout arguments such as
`col_span`, style shorthands, and finally `style={...}`. For padding, `p` sets all sides, `px` and `py` set
the axes, and individual sides such as `pl` take precedence. Both `props` and its `style` entry can be
reactive expressions. Other attributes and event handlers are carried through the merge.

## Cards, headings and form fields

Use `Card(*children)` for a padded surface. Its colors, border, radius and spacing follow the current
theme. Children stack vertically by default. Set `flex_direction="row"` for a horizontal card.
`Heading(..., level=1)` through `level=6` emit native headings. Choose the level for the document
outline and use `font_size` to change the visual size independently.

```python
from fleur.ui import Card, Heading, Option, Select, field

category = Card(
    Heading("Expenses", level=2),
    field(
        id="expense-category",
        label="Category",
        description="Choose the category used in reports.",
        control=lambda attrs: Select(
            Option("Travel", value="travel"),
            Option("Meals", value="meals"),
            value=Report.category,
            onchange=Msgs.CATEGORY,
            props=attrs,
        ),
    ),
)
```

Give each field a unique `id`. Its control receives the associated attributes and can also be an
`Input`, `Textarea` or custom view. Pass `error` as text or a reactive expression. A nonempty
error appears alongside the description and sets `aria-invalid` on the control. An empty string
or `None` clears the error. Style the wrapper with `props` or view arguments, and target
`[data-fleur-part="label"]`, `"description"` or `"error"` in its stylesheet.

`Select` uses the input theme settings. Its `onchange` message receives the option value in
`event.value`. Omitting an option's `value` uses its label. With `Select(value=...)`, the
selection follows the supplied value as options change. If it has no matching option, the
control shows no selection until a match returns. Omit the select's `value` to use native selection.

## Sortable table headers

`SortableTableHead("Amount", active=by_amount, descending=Report.descending, onsort=Msgs.SORT.bind("amount"))`
places a button in a column header. The active header displays its direction and exposes
`aria-sort`. Each inactive sortable header shows a bidirectional arrow. On activation, handle the
message to choose the column and direction, then pass the ordered rows to `TableBody`.
The expense report uses `Array.sort_by` on the filtered rows.

## Empty states

Use `EmptyState(title, description, *actions)` when a collection has no items to show.
The title and optional description accept text or model expressions. Actions can be ordinary
buttons or links. The title defaults to an `h3`; set `level` to fit the surrounding outline.

```python
EmptyState(
    "No expenses in this category",
    "Choose another category or show the full report.",
    Button("Show all categories", onclick=Msgs.CLEAR_FILTER, variant="secondary"),
)
```

## Disclosures

`Disclosure("Calculation details", Text("The subtotal includes the visible rows."))` renders
a native `<details>` with the first argument as its `<summary>`. Pass additional children for
the expanded content. Each disclosure starts closed and opens independently. Set
`props={"open": True}` to start one expanded.

## Checkbox fields

`CheckboxField("Dark mode", checked=Gallery.dark, onchange=Actions.MODE)` places a
native checkbox inside its visible label. Clicking the label or pressing Space on the
focused checkbox toggles it. Read `Actions.MODE.event.checked` to update the model.
Use `name`, `value`, `required`, and `disabled` for native form behavior. View style
arguments and `props` apply to the label, and `input_props` applies to the checkbox.

## Radio groups

Use `RadioGroup` to display a small set of mutually exclusive choices. The mapping's keys
are form values and its values are visible labels. Give each independent group in the same
form (or page, outside a form) a distinct, nonempty `name`. The `label` appears as its legend.

```python
RadioGroup(
    {"left": "Left", "center": "Center", "right": "Right"},
    name="title-alignment",
    label="Title alignment",
    value=Gallery.title_align,
    onselect=Actions.TITLE_ALIGN,
)
```

Declare the selection message as `Msg[InputEvent, str]` or use a narrower string literal
type for the option keys. Set the model field from the message's `.context` on change.
Tab enters the group at the checked radio. Arrow keys select another option in the same group.

## Progress

Use `Progress(label="Checking service status")` while an operation's total is unknown.
For a known total, use `Progress(label="Book review", value=Library.reviewed, max=4)`.
Supply a positive `max` (the browser default is 1). Both numbers can follow the model.
A value of zero shows the start of measurable progress, and `None` switches the same bar
to indeterminate. Use `label` or associate a visible HTML label to name the bar.

## Links and notices

`Link` renders a native anchor. Use a fragment or URL for `href`, or supply a file URL and
`download` filename for a download. The destination, filename and disabled state can follow
the model. A disabled link exposes `aria-disabled`, loses its destination and leaves the
normal Tab order. Use `variant="button"` to apply the theme's button styling.

```python
from fleur.ui import Button, Link, Notice

guide = Link("Read the guide", href="#guide")
export = Link("Download CSV", href=Report.csv_url, download="expenses.csv",
              disabled=Report.empty, variant="button")
feedback = Notice("Could not save your changes.", Button("Retry", onclick=Actions.RETRY),
                  variant="error")
```

`Notice(message, *actions)` accepts text or a view. Its `variant` can be `"info"`,
`"success"` or `"error"` and can follow the model. The message uses `role="status"` by
default for polite announcements. Choose `announce="assertive"` for an urgent message
(`role="alert"`) or `announce="off"` for static information. Action buttons sit outside the
live region so updating the message doesn't announce their labels.

## Customize grids

`Grid(columns=3)` sets three equal tracks. `Grid(min_col=120)` fits as many tracks of at least 120px
as the available width allows. If both are given, `columns` takes precedence. A class can supply the
grid template and item placement when these arguments are omitted. Explicit layout arguments override
ordinary class rules, and `style={"grid-template-columns": ...}` or `style={"grid-column": ...}`
can override the corresponding argument. A `GridItem` with no placement uses CSS Grid's auto-placement.

## Customize tabs

Pass `label="Report sections"` to name the tab list for assistive technology. Tab enters the
list on the selected tab. Left and Right move focus between tabs and wrap at either end.
Home and End move to the first and last tab. Enter, Space or a click sends the selected key
to `onselect`. Tab moves on to the visible panel. Each tab and its panel have linked IDs.
Update existing tab styles that target `aria-pressed` to target `aria-selected`.

In `tabs(panels, selected, onselect, tab_class="report-tab", tab_style={"padding": "6px 10px"})`,
`tab_class` and `tab_style` apply to each tab button. The usual `props`, shorthands and `style`
apply to the wrapper. A selected tab uses the current scope's `card` background, a border and
heavier text. An unselected tab has a transparent background and uses `muted-foreground` for its text.
To customize the selected background and keep the hover tint, set
`--fleur-local-bg` on `.report-tab[aria-selected="true"]`. A class that sets `background` directly
controls the hover background too. For the same property, `tab_style` overrides ordinary class rules.
The Button focus ring follows keyboard focus independently of selection.
