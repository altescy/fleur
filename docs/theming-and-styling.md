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
from fleur.ui import Button, ButtonBackground, ThemeMode, ThemeScope

class Appearance(Model):
    mode: State[ThemeMode]

view = ThemeScope(
    Button("Parent"),
    ThemeScope(
        Button("Child"),
        ThemeScope(Button("Grandchild"), colors={"primary": "#21854a"}),
        button_bg=ButtonBackground.PRIMARY,
    ),
    button_bg="#824399",
    mode=Appearance.mode,
)
```

Here the parent button stays purple. The child uses the current light or dark primary, and the
grandchild uses green in both modes. Omitting `button_bg` inherits the enclosing Button override.

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
the same mode. Explicit scope overrides such as `colors` and `button_bg` continue to apply.
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
Start with view arguments such as `p="lg"`, `gap="sm"`, and `bg="card"`. Use `css(...)` when
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

## Customize grids

`Grid(columns=3)` sets three equal tracks. `Grid(min_col=120)` fits as many tracks of at least 120px
as the available width allows. If both are given, `columns` takes precedence. A class can supply the
grid template and item placement when these arguments are omitted. Explicit layout arguments override
ordinary class rules, and `style={"grid-template-columns": ...}` or `style={"grid-column": ...}`
can override the corresponding argument. A `GridItem` with no placement uses CSS Grid's auto-placement.

## Customize tabs

In `tabs(panels, selected, onselect, tab_class="report-tab", tab_style={"padding": "6px 10px"})`,
`tab_class` and `tab_style` apply to each tab button. The usual `props`, shorthands and `style`
apply to the wrapper. A selected tab uses the current scope's `card` background, a border and
heavier text. An unselected tab has a transparent background and uses `muted-foreground` for its text.
To customize the selected background and keep the hover tint, set
`--fleur-local-bg` on `.report-tab[aria-pressed="true"]`. A class that sets `background` directly
controls the hover background too. For the same property, `tab_style` overrides ordinary class rules.
The Button focus ring follows keyboard focus independently of selection.
