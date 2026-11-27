"""Interactive previews and their Python source, built from the same functions."""

from base64 import b64encode
from collections.abc import Callable, Sequence
from inspect import getsource
from pathlib import Path
from typing import Literal

from fleur import Array, Boolean, Component, Cond, Model, Msg, MsgGroup, Number, Object, State, String, View
from fleur.core import DialogCloseEvent, InputEvent, PointerEvent, SubmitEvent, ToastCloseEvent, ToggleEvent, record
from fleur.ui import (
    BASIC_THEME,
    ZEN_THEME,
    Accordion,
    AccordionItem,
    AlertDialog,
    Avatar,
    Box,
    Button,
    Card,
    CheckboxField,
    CheckboxGroup,
    Combobox,
    ContextMenu,
    Dialog,
    Disclosure,
    Divider,
    EmptyState,
    Fieldset,
    Form,
    Grid,
    GridItem,
    Heading,
    HStack,
    Input,
    Link,
    Menu,
    MenuItem,
    Menubar,
    Meter,
    NavigationMenu,
    NavigationMenuGroup,
    Notice,
    NoticeVariant,
    NumberField,
    Option,
    Popover,
    PreviewCard,
    Progress,
    RadioGroup,
    ScrollArea,
    Select,
    Slider,
    SortableTableHead,
    Switch,
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableFooter,
    TableHead,
    TableHeader,
    TableRow,
    Text,
    Textarea,
    Theme,
    ThemeScope,
    Toast,
    Toggle,
    ToggleGroup,
    Toolbar,
    Tooltip,
    VStack,
    css,
    field,
    tabs,
)


TitleSize = Literal["sm", "lg"]


class Gallery(Model):
    preset: State[str]
    dark: State[bool]
    count: State[int]
    title: State[str]
    shelf: State[str]
    notes: State[str]
    favorite: State[bool]
    book_details_locked: State[bool]
    title_size: State[TitleSize]
    title_align: State[str]
    title_emphasis: State[Sequence[str]]
    visible_shelves: State[Sequence[str]]
    books_descending: State[bool]
    total_known: State[bool]
    reviewed: State[int]
    storage_used: State[int]
    saved: State[str]
    include_expense: State[bool]
    fail_next_save: State[bool]
    notice: State[NoticeVariant]
    include_book: State[bool]
    finished_only: State[bool]
    tab: State[str]
    dialog_open: State[bool]
    notes_open: State[bool]
    menu_editor_open: State[bool]
    clear_notes_open: State[bool]
    catalog_book: State[str]
    reading_size: State[int | float]
    reading_goal: State[str]
    sample_in_reading_list: State[bool]
    book_added_toast: State[bool]


class Actions(MsgGroup):
    PRESET: Msg[InputEvent] = Msg()
    MODE: Msg[InputEvent] = Msg()
    ADD: Msg[PointerEvent] = Msg()
    SUBTRACT: Msg[PointerEvent] = Msg()
    RESET: Msg[PointerEvent] = Msg()
    TITLE: Msg[InputEvent] = Msg()
    SHELF: Msg[InputEvent] = Msg()
    NOTES: Msg[InputEvent] = Msg()
    FAVORITE: Msg[InputEvent] = Msg()
    LOCK_BOOK_DETAILS: Msg[InputEvent] = Msg()
    TITLE_SIZE: Msg[InputEvent, TitleSize] = Msg()
    TITLE_ALIGN: Msg[InputEvent, str] = Msg()
    ALIGN_TITLE: Msg[PointerEvent, str] = Msg()
    TITLE_EMPHASIS: Msg[PointerEvent, Sequence[str]] = Msg()
    FILTER_SHELVES: Msg[InputEvent, Sequence[str]] = Msg()
    SORT_BOOKS: Msg[PointerEvent] = Msg()
    TOTAL_KNOWN: Msg[InputEvent] = Msg()
    REVIEW_ONE: Msg[PointerEvent] = Msg()
    RESET_REVIEW: Msg[PointerEvent] = Msg()
    CHANGE_STORAGE: Msg[PointerEvent, int] = Msg()
    SAVE: Msg[SubmitEvent] = Msg()
    INCLUDE_EXPENSE: Msg[InputEvent] = Msg()
    FAIL_NEXT_SAVE: Msg[InputEvent] = Msg()
    TRY_SAVE: Msg[PointerEvent] = Msg()
    INCLUDE_BOOK: Msg[InputEvent] = Msg()
    FINISHED_ONLY: Msg[InputEvent] = Msg()
    SHOW_ALL_BOOKS: Msg[PointerEvent] = Msg()
    TAB: Msg[PointerEvent, str] = Msg()
    OPEN: Msg[PointerEvent] = Msg()
    CLOSED: Msg[DialogCloseEvent] = Msg()
    TOGGLE_NOTES: Msg[ToggleEvent] = Msg()
    DONE_EDITING: Msg[PointerEvent] = Msg()
    EDIT_NOTES: Msg[PointerEvent] = Msg()
    CLOSE_EDITOR: Msg[DialogCloseEvent] = Msg()
    TOGGLE_FAVORITE: Msg[PointerEvent, bool] = Msg()
    REQUEST_CLEAR_NOTES: Msg[PointerEvent] = Msg()
    CLOSE_CLEAR_NOTES: Msg[DialogCloseEvent] = Msg()
    CLEAR_NOTES: Msg[SubmitEvent] = Msg()
    SELECT_BOOK: Msg[PointerEvent, str] = Msg()
    READING_SIZE: Msg[InputEvent] = Msg()
    SET_READING_SIZE: Msg[PointerEvent, int] = Msg()
    READING_GOAL: Msg[InputEvent] = Msg()
    TOGGLE_READING_LIST: Msg[PointerEvent] = Msg()
    CLOSE_BOOK_TOAST: Msg[ToastCloseEvent] = Msg()


Preview = View[Gallery, Actions]


def buttons() -> Preview:
    empty = Cond.equal(Gallery.count, 0)
    return VStack(
        HStack(
            Button("Add one", onclick=Actions.ADD),
            Button("Subtract one", variant="secondary", onclick=Actions.SUBTRACT, props={"disabled": empty}),
            Button("Reset", variant="ghost", onclick=Actions.RESET),
            gap="sm",
            flex_wrap="wrap",
        ),
        Text(f"Count: {Gallery.count}", props={"role": "status"}),
        gap="md",
    )


def layout() -> Preview:
    return Card(
        Heading("Reading list", level=3),
        Text("A card with a heading, a divider and a two-column grid."),
        Divider(my=None),
        Grid(
            GridItem(Text("On the shelf", fg="muted-foreground")),
            GridItem(Text("12 books", font_weight=600)),
            GridItem(Box(Text("Updated today"), bg="muted", p="sm", radius="sm"), col_span=2),
            columns=2,
            gap="sm",
        ),
    )


def forms() -> Preview:
    blank = Cond.equal(String.trim(Gallery.title), "")
    return Form(
        VStack(
            Switch(
                "Lock book details",
                checked=Gallery.book_details_locked,
                onchange=Actions.LOCK_BOOK_DETAILS,
                align_self="flex-start",
            ),
            Fieldset(
                field(
                    id="book-title",
                    label="Book title",
                    error=Cond.when(blank, "Enter a book title.", None),
                    control=lambda attrs: Input(
                        value=Gallery.title, oninput=Actions.TITLE, props={**attrs, "required": True}
                    ),
                ),
                field(
                    id="book-shelf",
                    label="Shelf",
                    control=lambda attrs: Select(
                        Option("To read"),
                        Option("Reading"),
                        Option("Finished"),
                        value=Gallery.shelf,
                        onchange=Actions.SHELF,
                        props=attrs,
                    ),
                ),
                field(
                    id="book-notes",
                    label="Notes",
                    control=lambda attrs: Textarea(rows=2, value=Gallery.notes, oninput=Actions.NOTES, props=attrs),
                ),
                CheckboxField("Mark as a favorite", checked=Gallery.favorite, onchange=Actions.FAVORITE),
                Button("Save book", props={"type": "submit", "disabled": blank}, align_self="flex-start"),
                label="Book details",
                disabled=Gallery.book_details_locked,
            ),
            Notice(Gallery.saved, variant="success", props={"hidden": Cond.equal(Gallery.saved, "")}),
            gap="sm",
        ),
        onsubmit=Actions.SAVE,
        prevent_default=True,
    )


def radio_groups() -> Preview:
    sizes: dict[TitleSize, str] = {"sm": "Small", "lg": "Large"}
    return VStack(
        RadioGroup(
            sizes,
            name="book-title-size",
            label="Title size",
            value=Gallery.title_size,
            onselect=Actions.TITLE_SIZE,
        ),
        RadioGroup(
            {"left": "Left", "center": "Center", "right": "Right"},
            name="book-title-alignment",
            label="Title alignment",
            value=Gallery.title_align,
            onselect=Actions.TITLE_ALIGN,
        ),
        Text(Gallery.title, font_size=Gallery.title_size, text_align=Gallery.title_align),
        gap="md",
    )


def tables() -> Preview:
    counts = record({"To read": 5, "Reading": 3, "Finished": 4})
    shelves = Array.sort_by(Object.keys(counts), lambda shelf: counts[shelf], descending=Gallery.books_descending)
    return Table(
        TableCaption("Books by shelf"),
        TableHeader(
            TableRow(
                TableHead("Shelf"),
                SortableTableHead(
                    "Books",
                    active=True,
                    descending=Gallery.books_descending,
                    onsort=Actions.SORT_BOOKS,
                    align="right",
                ),
            )
        ),
        TableBody(
            Array.map(
                shelves,
                lambda shelf: TableRow(TableCell(shelf), TableCell(counts[shelf], align="right"), props={"key": shelf}),
            )
        ),
        TableFooter(
            TableRow(
                TableHead("Total", props={"scope": "row"}), TableCell(Array.sum(Object.values(counts)), align="right")
            )
        ),
    )


def links() -> Preview:
    return VStack(
        CheckboxField("Include a sample expense", checked=Gallery.include_expense, onchange=Actions.INCLUDE_EXPENSE),
        Link(
            "Download sample CSV",
            href="data:text/csv;charset=utf-8,Description%2CJPY%0ATrain%20fare%2C420%0A",
            download="sample-expenses.csv",
            disabled=Cond.equal(Gallery.include_expense, False),
            variant="button",
            align_self="flex-start",
        ),
        gap="sm",
    )


def notices() -> Preview:
    failed = Cond.equal(Gallery.notice, "error")
    return VStack(
        CheckboxField(
            "Simulate a failure on the next save", checked=Gallery.fail_next_save, onchange=Actions.FAIL_NEXT_SAVE
        ),
        Notice(
            Cond.when(
                failed,
                "Save failed. Your changes are still here.",
                Cond.when(Cond.equal(Gallery.notice, "success"), "Changes saved.", "Ready to save."),
            ),
            Button(Cond.when(failed, "Retry", "Save example"), onclick=Actions.TRY_SAVE, variant="secondary"),
            variant=Gallery.notice,
            announce="polite",
        ),
        gap="sm",
    )


def progress() -> Preview:
    total = 4
    return VStack(
        CheckboxField("Total known", checked=Gallery.total_known, onchange=Actions.TOTAL_KNOWN),
        Progress(label="Book review", value=Cond.when(Gallery.total_known, Gallery.reviewed, None), max=total),
        Text(
            Cond.when(
                Gallery.total_known,
                String.from_number(Gallery.reviewed) + f" of {total} books reviewed",
                "Counting books…",
            )
        ),
        HStack(
            Button(
                "Review one book",
                onclick=Actions.REVIEW_ONE,
                props={"disabled": Cond.some(Boolean.negate(Gallery.total_known), Gallery.reviewed >= total)},
            ),
            Button(
                "Reset count",
                onclick=Actions.RESET_REVIEW,
                variant="secondary",
                props={"disabled": Cond.equal(Gallery.reviewed, 0)},
            ),
            gap="sm",
        ),
        gap="sm",
    )


def meters() -> Preview:
    capacity, low, high, step = 100, 60, 85, 10
    used = Gallery.storage_used
    amount = String.from_number(used)
    return VStack(
        HStack(
            Text("Storage usage", font_weight=600, props={"id": "storage-usage-label"}),
            Text(amount + f" / {capacity} GB", props={"id": "storage-usage-value", "role": "status"}),
            justify="space-between",
            align="baseline",
            flex_wrap="wrap",
            gap="xs",
        ),
        Meter(
            value=used,
            min=0,
            max=capacity,
            low=low,
            high=high,
            optimum=0,
            w="full",
            props={
                "aria-labelledby": "storage-usage-label",
                "aria-describedby": "storage-usage-value storage-usage-status",
            },
        ),
        Text(
            Cond.when(
                used >= capacity,
                "Storage full",
                Cond.when(used > high, "Nearly full", Cond.when(used > low, "Approaching capacity", "Within capacity")),
            ),
            fg="muted-foreground",
            font_size="sm",
            props={"id": "storage-usage-status"},
        ),
        HStack(
            Button(f"Add {step} GB", onclick=Actions.CHANGE_STORAGE.bind(step), props={"disabled": used >= capacity}),
            Button(
                f"Free {step} GB",
                onclick=Actions.CHANGE_STORAGE.bind(-step),
                variant="secondary",
                props={"disabled": used <= 0},
            ),
            gap="sm",
            flex_wrap="wrap",
        ),
        gap="sm",
        max_w=css("22rem"),
    )


def empty_states() -> Preview:
    return VStack(
        CheckboxField("Include a sample book", checked=Gallery.include_book, onchange=Actions.INCLUDE_BOOK),
        CheckboxField("Finished books only", checked=Gallery.finished_only, onchange=Actions.FINISHED_ONLY),
        Cond.when(
            Gallery.include_book,
            Cond.when(
                Gallery.finished_only,
                EmptyState(
                    "No finished books",
                    "Your sample book is on the reading shelf.",
                    Button("Show all books", onclick=Actions.SHOW_ALL_BOOKS, variant="secondary"),
                ),
                Text("The Secret Garden · Reading"),
            ),
            EmptyState("Your reading list is empty", "Include a sample book to start your list."),
        ),
        gap="sm",
    )


def tab_list() -> Preview:
    panels: dict[str, Preview] = {
        "Overview": Text("Use the arrow keys to move focus, then press Enter or Space to select."),
        "Keyboard": Text("Home and End jump to the first and last tabs. Tab moves into the selected panel."),
    }
    return tabs(panels, Gallery.tab, Actions.TAB, label="Tab example", gap="md")


def dialogs() -> Preview:
    return Box(
        Button("Open dialog", onclick=Actions.OPEN),
        Dialog(
            VStack(
                Heading("Reading notes", level=3, props={"id": "dialog-title"}),
                Text("Close this dialog with Escape or Done to return to the button."),
                Form(Button("Done", props={"type": "submit", "autofocus": True}), props={"method": "dialog"}),
                gap="md",
            ),
            open=Gallery.dialog_open,
            onclose=Actions.CLOSED,
            labelledby="dialog-title",
        ),
    )


def popovers() -> Preview:
    return VStack(
        Text(Cond.when(Cond.equal(Gallery.notes, ""), "No reading notes yet.", Gallery.notes)),
        Popover(
            VStack(
                field(
                    id="popover-notes",
                    label="Reading notes",
                    control=lambda attrs: Textarea(
                        value=Gallery.notes, oninput=Actions.NOTES, props={**attrs, "autofocus": True}
                    ),
                ),
                Button("Done", onclick=Actions.DONE_EDITING, align_self="flex-end"),
                gap="sm",
            ),
            id="reading-notes-editor",
            trigger=lambda attrs: Button("Edit notes", variant="secondary", props=attrs),
            open=Gallery.notes_open,
            ontoggle=Actions.TOGGLE_NOTES,
        ),
        gap="sm",
    )


def menus() -> Preview:
    no_notes = Cond.equal(Gallery.notes, "")
    actions = (
        MenuItem("Edit notes…", onclick=Actions.EDIT_NOTES),
        MenuItem(
            Cond.when(Gallery.favorite, "Remove from favorites", "Add to favorites"),
            onclick=Actions.TOGGLE_FAVORITE.bind(Boolean.negate(Gallery.favorite)),
        ),
        MenuItem("Clear notes…", onclick=Actions.REQUEST_CLEAR_NOTES, disabled=no_notes),
    )
    return VStack(
        HStack(
            Heading("Reading notes", level=3, font_size="lg"),
            Menu(
                *actions,
                id="reading-notes-menu",
                trigger=lambda attrs: Button("Note actions", variant="secondary", props=attrs),
            ),
            justify="space-between",
            align="center",
            flex_wrap="wrap",
            gap="sm",
        ),
        ContextMenu(
            *actions,
            id="reading-notes-context",
            trigger=lambda attrs: Box(
                Text(Cond.when(no_notes, "No reading notes yet.", Gallery.notes), props={"role": "status"}),
                bg="muted",
                p="md",
                radius="sm",
                props={
                    **attrs,
                    "role": "group",
                    "aria-label": "Reading note",
                    "aria-describedby": "reading-note-shortcut",
                },
            ),
        ),
        Text(
            "Right-click the note or press Shift+F10 for actions.",
            font_size="sm",
            fg="muted-foreground",
            props={"id": "reading-note-shortcut"},
        ),
        Text(Cond.when(Gallery.favorite, "In favorites", "Outside favorites"), fg="muted-foreground"),
        Dialog(
            VStack(
                Heading("Edit reading notes", level=3, props={"id": "menu-editor-title"}),
                field(
                    id="menu-editor-notes",
                    label="Reading notes",
                    control=lambda attrs: Textarea(
                        value=Gallery.notes, oninput=Actions.NOTES, props={**attrs, "autofocus": True}
                    ),
                ),
                Form(
                    Button("Done", props={"type": "submit"}),
                    props={"method": "dialog"},
                    align_self="flex-end",
                ),
                gap="sm",
            ),
            open=Gallery.menu_editor_open,
            onclose=Actions.CLOSE_EDITOR,
            labelledby="menu-editor-title",
        ),
        AlertDialog(
            id="clear-reading-notes",
            title="Clear reading notes?",
            description="This will permanently remove the current reading notes.",
            confirm_label="Clear notes",
            open=Gallery.clear_notes_open,
            onclose=Actions.CLOSE_CLEAR_NOTES,
            onconfirm=Actions.CLEAR_NOTES,
        ),
        gap="sm",
    )


def menubars() -> Preview:
    return VStack(
        Menubar(
            Menu(
                MenuItem("Edit notes…", onclick=Actions.EDIT_NOTES),
                MenuItem(
                    Cond.when(Gallery.favorite, "Remove from favorites", "Add to favorites"),
                    onclick=Actions.TOGGLE_FAVORITE.bind(Boolean.negate(Gallery.favorite)),
                ),
                id="menubar-note-actions",
                trigger=lambda attrs: Button("Note", variant="ghost", props=attrs),
            ),
            Menu(
                MenuItem("Standard text", onclick=Actions.SET_READING_SIZE.bind(18)),
                MenuItem("Large text", onclick=Actions.SET_READING_SIZE.bind(24)),
                id="menubar-view-actions",
                trigger=lambda attrs: Button("View", variant="ghost", props=attrs),
            ),
            label="Reading note commands",
        ),
        VStack(
            HStack(
                Heading("Reading notes", level=3, font_size="sm"),
                Text(
                    Cond.when(Gallery.favorite, "In favorites", "Outside favorites"),
                    fg="muted-foreground",
                    font_size="sm",
                    props={"role": "status"},
                ),
                justify="space-between",
                align="baseline",
                flex_wrap="wrap",
                gap="sm",
            ),
            Text(
                Cond.when(Cond.equal(Gallery.notes, ""), "No reading notes yet.", Gallery.notes),
                font_size=Gallery.reading_size,
                white_space="pre-wrap",
                style={"overflow-wrap": "anywhere"},
                props={"id": "menubar-note-preview"},
            ),
            p="md",
            gap="sm",
            bg="muted",
            radius="md",
        ),
        gap="sm",
    )


def tooltips() -> Preview:
    return HStack(
        Tooltip(
            "Favorites appear in your saved reading list.",
            id="reading-favorites-hint",
            trigger=lambda attrs: Toggle(
                Text(Cond.when(Gallery.favorite, "★", "☆"), props={"aria-hidden": "true"}, w=css("1em")),
                "Favorite",
                pressed=Gallery.favorite,
                onchange=Actions.TOGGLE_FAVORITE,
                props=attrs,
            ),
        ),
        gap="sm",
        align="center",
    )


def preview_cards() -> Preview:
    return PreviewCard(
        Text("Reading notes", font_weight=600),
        Text(
            Cond.when(Cond.equal(Gallery.notes, ""), "No reading notes yet.", Gallery.notes),
            fg="muted-foreground",
            white_space="pre-wrap",
            style={
                "display": "-webkit-box",
                "-webkit-box-orient": "vertical",
                "-webkit-line-clamp": "4",
                "overflow": "hidden",
            },
        ),
        trigger=Link("Reading notes", href="#menubars"),
    )


def comboboxes() -> Preview:
    books = {
        "little-princess": "A Little Princess",
        "little-women": "Little Women",
        "secret-garden": "The Secret Garden",
        "wind-in-willows": "The Wind in the Willows",
    }
    return VStack(
        Combobox(
            books,
            id="catalog-title",
            label="Book title in catalog",
            value=Gallery.catalog_book,
            onselect=Actions.SELECT_BOOK,
            placeholder="Type part of a title",
            empty_text="No books match that title.",
        ),
        Text("Selected book: " + record(books)[Gallery.catalog_book], props={"role": "status"}),
        gap="sm",
    )


def sliders() -> Preview:
    size = String.from_number(Gallery.reading_size)
    return VStack(
        field(
            id="reading-size",
            label="Reading text size",
            control=lambda attrs: HStack(
                Slider(
                    min=14,
                    max=30,
                    step=2,
                    value=Gallery.reading_size,
                    oninput=Actions.READING_SIZE,
                    props={**attrs, "aria-valuetext": size + " pixels"},
                ),
                Text(size + " px", white_space="nowrap", font_weight=600, props={"id": "reading-size-value"}),
                gap="sm",
                align="center",
            ),
        ),
        Box(
            Text(
                "An open book rested beside the window. Outside, the rain softened the sound of the street.",
                font_size=Gallery.reading_size,
                props={"id": "reading-preview"},
            ),
            bg="muted",
            radius="md",
            p="md",
        ),
        gap="sm",
    )


def toasts() -> Preview:
    return HStack(
        Text("The Secret Garden", font_weight=600),
        Button(
            Cond.when(Gallery.sample_in_reading_list, "Remove from reading list", "Add to reading list"),
            onclick=Actions.TOGGLE_READING_LIST,
            variant="secondary",
        ),
        Toast(
            "Added The Secret Garden to your reading list.",
            open=Gallery.book_added_toast,
            onclose=Actions.CLOSE_BOOK_TOAST,
            duration_ms=4000,
        ),
        justify="space-between",
        align="center",
        flex_wrap="wrap",
        gap="sm",
    )


def accordions() -> Preview:
    return Accordion(
        AccordionItem(
            "Add a book to the reading list",
            Text(
                "Choose Add to reading list in the Toast example. The book stays on the list after the notice closes."
            ),
            initial_open=True,
        ),
        AccordionItem(
            "Change a book’s reading status",
            Text("In Form controls, choose To read, Reading, or Finished from Shelf, then save the book."),
        ),
        AccordionItem(
            "Edit reading notes",
            Text("Open Note actions in the Menu example and choose Edit notes. Select Done to close the editor."),
        ),
        props={"role": "group", "aria-label": "Reading list help"},
    )


def toolbars() -> Preview:
    return VStack(
        Toolbar(
            *(
                Button(
                    alignment.capitalize(),
                    variant="ghost",
                    onclick=Actions.ALIGN_TITLE.bind(alignment),
                    props={
                        "type": "button",
                        "aria-pressed": Cond.when(Cond.equal(Gallery.title_align, alignment), "true", "false"),
                    },
                )
                for alignment in ("left", "center", "right")
            ),
            label="Reading title alignment",
        ),
        Text(
            Gallery.title,
            text_align=Gallery.title_align,
            font_size="lg",
            font_weight=600,
            bg="muted",
            p="md",
            radius="md",
            props={"id": "toolbar-reading-title"},
        ),
        gap="sm",
    )


def toggle_groups() -> Preview:
    bold = Array.includes(Gallery.title_emphasis, "bold")
    italic = Array.includes(Gallery.title_emphasis, "italic")
    return VStack(
        ToggleGroup(
            {"bold": "Bold", "italic": "Italic"},
            label="Reading title emphasis",
            value=Gallery.title_emphasis,
            onchange=Actions.TITLE_EMPHASIS,
        ),
        Text(
            Gallery.title,
            font_size="lg",
            font_weight=Cond.when(bold, 700, 400),
            bg="muted",
            p="md",
            radius="md",
            style={"font-style": Cond.when(italic, "italic", "normal")},
            props={"id": "toggle-reading-title"},
        ),
        gap="sm",
    )


def avatars() -> Preview:
    image = (Path(__file__).with_name("assets") / "gallery-reviewer.jpg").read_bytes()
    illustration = "data:image/jpeg;base64," + b64encode(image).decode("ascii")
    reviewers = (
        ("Lead reviewer", "LR", illustration, "The Secret Garden"),
        ("Second reviewer", "SR", "data:image/jpeg;base64,AA==", "Little Women"),
    )
    return VStack(
        *(
            HStack(
                Avatar(name=name, fallback=initials, src=source),
                VStack(
                    Text(name, font_weight=600, props={"aria-hidden": True}),
                    Text(book, font_size="sm", fg="muted-foreground"),
                ),
                gap="md",
                align="center",
            )
            for name, initials, source, book in reviewers
        ),
        gap="md",
    )


def checkbox_groups() -> Preview:
    shelves = ("To read", "Reading", "Finished")
    books = (
        ("Pride and Prejudice", "To read"),
        ("The Secret Garden", "Reading"),
        ("Little Women", "Finished"),
    )
    return VStack(
        CheckboxGroup(
            {shelf: shelf for shelf in shelves},
            label="Shelves to show",
            value=Gallery.visible_shelves,
            onchange=Actions.FILTER_SHELVES,
        ),
        Cond.when(
            Cond.equal(Array.length(Gallery.visible_shelves), 0),
            EmptyState("No shelves selected", "Select a shelf to see its books."),
            View(
                *(
                    Cond.when(
                        Array.includes(Gallery.visible_shelves, shelf),
                        View(title, " · ", shelf, tag="li", props={}),
                        None,
                    )
                    for title, shelf in books
                ),
                tag="ul",
                props={"aria-label": "Books on selected shelves"},
            ),
        ),
        gap="md",
    )


def number_fields() -> Preview:
    return field(
        id="reading-goal",
        label="Reading goal (hours per week)",
        control=lambda attrs: NumberField(
            value=Gallery.reading_goal,
            min=0,
            max=20,
            step=0.5,
            oninput=Actions.READING_GOAL,
            decrease_label="Decrease reading goal",
            increase_label="Increase reading goal",
            input_props=attrs,
        ),
    )


# Each group supplies the same labels and order for the index and the previews.
EXAMPLES: tuple[tuple[str, str, tuple[tuple[str, Callable[[], Preview]], ...]], ...] = (
    (
        "foundations",
        "Foundations",
        (("Buttons", buttons), ("Links", links), ("Cards & layout", layout), ("Avatar", avatars)),
    ),
    (
        "inputs",
        "Inputs",
        (
            ("Form controls", forms),
            ("Radio groups", radio_groups),
            ("Checkbox group", checkbox_groups),
            ("Combobox", comboboxes),
            ("Number field", number_fields),
            ("Slider", sliders),
            ("Toggle group", toggle_groups),
        ),
    ),
    ("data", "Data display", (("Tables", tables), ("Meter", meters), ("Empty states", empty_states))),
    (
        "navigation",
        "Navigation",
        (("Tabs", tab_list), ("Menu", menus), ("Menubar", menubars), ("Accordion", accordions), ("Toolbar", toolbars)),
    ),
    (
        "overlays",
        "Overlays",
        (("Dialog", dialogs), ("Popover", popovers), ("Tooltip", tooltips), ("Preview card", preview_cards)),
    ),
    ("feedback", "Feedback", (("Notices", notices), ("Progress", progress), ("Toast", toasts))),
)


def _section(title: str, render: Callable[[], Preview]) -> Preview:
    return View(
        Heading(title, level=2),
        Box(render(), props={"className": "preview"}),
        Disclosure(
            "Python source",
            ScrollArea(
                View(View(getsource(render).rstrip(), tag="code", props={}), tag="pre", props={}),
                label=f"{title} Python source",
                max_h=css("28rem"),
                bg="code",
                fg="code-foreground",
                radius=0,
            ),
            props={"className": "example-source"},
        ),
        tag="section",
        props={"id": render.__name__, "className": "specimen", "aria-label": title, "tabindex": "-1"},
    )


GALLERY_CSS = """
.gallery { max-width: 72rem; margin: auto; padding: clamp(1rem, 4vw, 3.5rem); }
.gallery-header { padding-block: 1rem 2rem; border-bottom: 1px solid var(--fleur-color-border); }
.gallery-header h1 { font: 500 clamp(2.5rem, 6vw, 4.5rem)/1.05 Georgia, serif; letter-spacing: -.045em; }
.gallery-index { position: sticky; top: 1rem; align-self: start; max-block-size: calc(100dvh - 2rem);
  overflow: auto; padding: var(--fleur-space-xs); border: 1px solid var(--fleur-color-border);
  border-radius: var(--fleur-radius-lg); background: var(--fleur-color-card); }
.gallery-body { display: grid; grid-template-columns: minmax(11rem, 1fr) minmax(0, 4fr); gap: 2rem; padding-top: 2rem; }
.specimen { scroll-margin-top: 1rem; margin-bottom: 2.5rem; }
.specimen h2 { margin-bottom: .75rem; }
.preview { background: var(--fleur-color-card); padding: clamp(1rem, 3vw, 2rem);
  border: 1px solid var(--fleur-color-border); border-radius: var(--fleur-radius-lg) var(--fleur-radius-lg) 0 0; }
.example-source { border: 1px solid var(--fleur-color-border); border-top: 0;
  border-radius: 0 0 var(--fleur-radius-lg) var(--fleur-radius-lg); overflow: hidden; }
.example-source > summary { font: .875rem var(--fleur-font-mono); }
.example-source pre { inline-size: max-content; min-inline-size: 100%; overflow: visible; background: none; }
@media (max-width: 42rem) {
  .gallery-body { grid-template-columns: minmax(0, 1fr); gap: 1.5rem; }
  .gallery-index { position: static; max-block-size: none; overflow: visible; }
}
"""


def app() -> Component[Gallery, Actions]:
    presets = {"Basic": BASIC_THEME, "Zen": ZEN_THEME}
    controls = HStack(
        View(
            "Theme ",
            Select(*(Option(name) for name in presets), value=Gallery.preset, onchange=Actions.PRESET),
            tag="label",
            props={},
        ),
        Switch("Dark mode", checked=Gallery.dark, onchange=Actions.MODE),
        align="center",
        gap="md",
        flex_wrap="wrap",
    )
    nav = NavigationMenu(
        *(
            NavigationMenuGroup(
                group,
                *(Link(title, href="#" + render.__name__) for title, render in entries),
                id=f"index-{key}",
            )
            for key, group, entries in EXAMPLES
        ),
        label="Components",
        auto_close=False,
        multiple=True,
        props={"className": "gallery-index"},
    )
    return Component(
        Gallery(
            preset="Basic",
            dark=False,
            count=0,
            title="The Secret Garden",
            shelf="Reading",
            notes="",
            favorite=False,
            book_details_locked=False,
            title_size="lg",
            title_align="center",
            title_emphasis=[],
            visible_shelves=["Reading"],
            books_descending=False,
            total_known=False,
            reviewed=0,
            storage_used=50,
            saved="",
            include_expense=False,
            fail_next_save=False,
            notice="info",
            include_book=False,
            finished_only=False,
            tab="Overview",
            dialog_open=False,
            notes_open=False,
            menu_editor_open=False,
            clear_notes_open=False,
            catalog_book="secret-garden",
            reading_size=18,
            reading_goal="3",
            sample_in_reading_list=False,
            book_added_toast=False,
        ),
        Actions.cases(
            Actions.PRESET.then(State.set(Gallery.preset, Actions.PRESET.event.value)),
            Actions.MODE.then(State.set(Gallery.dark, Actions.MODE.event.checked)),
            Actions.ADD.then(State.set(Gallery.count, Gallery.count + 1)),
            Actions.SUBTRACT.then(State.set(Gallery.count, Gallery.count - 1)),
            Actions.RESET.then(State.set(Gallery.count, 0)),
            Actions.TITLE.then(State.set(Gallery.title, Actions.TITLE.event.value)),
            Actions.SHELF.then(State.set(Gallery.shelf, Actions.SHELF.event.value)),
            Actions.NOTES.then(State.set(Gallery.notes, Actions.NOTES.event.value)),
            Actions.FAVORITE.then(State.set(Gallery.favorite, Actions.FAVORITE.event.checked)),
            Actions.LOCK_BOOK_DETAILS.then(
                State.set(Gallery.book_details_locked, Actions.LOCK_BOOK_DETAILS.event.checked)
            ),
            Actions.TITLE_SIZE.then(State.set(Gallery.title_size, Actions.TITLE_SIZE.context)),
            Actions.TITLE_ALIGN.then(State.set(Gallery.title_align, Actions.TITLE_ALIGN.context)),
            Actions.ALIGN_TITLE.then(State.set(Gallery.title_align, Actions.ALIGN_TITLE.context)),
            Actions.TITLE_EMPHASIS.then(State.set(Gallery.title_emphasis, Actions.TITLE_EMPHASIS.context)),
            Actions.FILTER_SHELVES.then(State.set(Gallery.visible_shelves, Actions.FILTER_SHELVES.context)),
            Actions.SORT_BOOKS.then(State.set(Gallery.books_descending, Boolean.negate(Gallery.books_descending))),
            Actions.TOTAL_KNOWN.then(State.set(Gallery.total_known, Actions.TOTAL_KNOWN.event.checked)),
            Actions.REVIEW_ONE.then(State.set(Gallery.reviewed, Gallery.reviewed + 1)),
            Actions.RESET_REVIEW.then(State.set(Gallery.reviewed, 0)),
            Actions.CHANGE_STORAGE.then(
                State.set(Gallery.storage_used, Gallery.storage_used + Actions.CHANGE_STORAGE.context)
            ),
            Actions.INCLUDE_EXPENSE.then(State.set(Gallery.include_expense, Actions.INCLUDE_EXPENSE.event.checked)),
            Actions.FAIL_NEXT_SAVE.then(State.set(Gallery.fail_next_save, Actions.FAIL_NEXT_SAVE.event.checked)),
            Actions.INCLUDE_BOOK.then(State.set(Gallery.include_book, Actions.INCLUDE_BOOK.event.checked)),
            Actions.FINISHED_ONLY.then(State.set(Gallery.finished_only, Actions.FINISHED_ONLY.event.checked)),
            Actions.SHOW_ALL_BOOKS.then(State.set(Gallery.finished_only, False)),
            Actions.TRY_SAVE.then(
                State.set(Gallery.notice, Cond.when(Gallery.fail_next_save, "error", "success"))
                & State.set(Gallery.fail_next_save, False)
            ),
            Actions.SAVE.then(
                State.set(
                    Gallery.saved,
                    "Saved "
                    + String.trim(Gallery.title)
                    + " to "
                    + Gallery.shelf
                    + Cond.when(Gallery.favorite, " · Favorite", ""),
                )
            ),
            Actions.TAB.then(State.set(Gallery.tab, Actions.TAB.context)),
            Actions.OPEN.then(State.set(Gallery.dialog_open, True)),
            Actions.CLOSED.then(State.set(Gallery.dialog_open, False)),
            Actions.TOGGLE_NOTES.then(State.set(Gallery.notes_open, Actions.TOGGLE_NOTES.event.open)),
            Actions.DONE_EDITING.then(State.set(Gallery.notes_open, False)),
            Actions.EDIT_NOTES.then(State.set(Gallery.menu_editor_open, True)),
            Actions.CLOSE_EDITOR.then(State.set(Gallery.menu_editor_open, False)),
            Actions.TOGGLE_FAVORITE.then(State.set(Gallery.favorite, Actions.TOGGLE_FAVORITE.context)),
            Actions.REQUEST_CLEAR_NOTES.then(State.set(Gallery.clear_notes_open, True)),
            Actions.CLOSE_CLEAR_NOTES.then(State.set(Gallery.clear_notes_open, False)),
            Actions.CLEAR_NOTES.then(State.set(Gallery.notes, "")),
            Actions.SELECT_BOOK.then(State.set(Gallery.catalog_book, Actions.SELECT_BOOK.context)),
            Actions.READING_SIZE.then(
                State.set(Gallery.reading_size, Number.from_string(Actions.READING_SIZE.event.value))
            ),
            Actions.SET_READING_SIZE.then(State.set(Gallery.reading_size, Actions.SET_READING_SIZE.context)),
            Actions.READING_GOAL.then(State.set(Gallery.reading_goal, Actions.READING_GOAL.event.value)),
            Actions.TOGGLE_READING_LIST.then(
                State.set(Gallery.sample_in_reading_list, Boolean.negate(Gallery.sample_in_reading_list))
                & State.set(Gallery.book_added_toast, Boolean.negate(Gallery.sample_in_reading_list))
            ),
            Actions.CLOSE_BOOK_TOAST.then(State.set(Gallery.book_added_toast, False)),
        ),
        ThemeScope(
            View(GALLERY_CSS, tag="style", props={}),
            View(
                HStack(
                    Heading("Component gallery", level=1),
                    controls,
                    gap="md",
                    flex_wrap="wrap",
                    align="center",
                    justify="space-between",
                    props={"className": "gallery-header"},
                ),
                View(
                    nav,
                    Box(*(_section(title, render) for _, _, entries in EXAMPLES for title, render in entries), min_w=0),
                    tag="div",
                    props={"className": "gallery-body"},
                ),
                tag="main",
                props={"className": "gallery"},
            ),
            theme=Theme.select(Gallery.preset, presets),
            mode=Cond.when(Gallery.dark, "dark", "light"),
            min_h="full",
        ),
    )
