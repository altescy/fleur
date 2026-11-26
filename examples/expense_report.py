"""Prepare a yen expense report and download it as a CSV file."""

from collections.abc import Mapping, Sequence
from typing import cast

from fleur import Array, Boolean, Component, Cond, Expr, Model, Msg, MsgGroup, Number, State, String, Url, View
from fleur.core import InputEvent, PointerEvent, record
from fleur.core.view import ViewChild
from fleur.ui import (
    Box,
    Button,
    Grid,
    HStack,
    Input,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    Text,
    Theme,
    ThemeScope,
    VStack,
    css,
)

Expense = Mapping[str, str | int]
CATEGORIES = ("Travel", "Meals", "Supplies", "Other")
ALL = "All categories"
MAX_AMOUNT = 999_999_999  # Whole yen.
PANEL_BORDER = "1px solid var(--fleur-color-border)"


class Report(Model):
    expenses: State[Sequence[Expense]]
    next_id: State[int]
    date: State[str]
    description: State[str]
    category: State[str]
    amount: State[str]
    category_filter: State[str]


class Msgs(MsgGroup):
    DATE: Msg[InputEvent] = Msg()
    DESCRIPTION: Msg[InputEvent] = Msg()
    CATEGORY: Msg[InputEvent] = Msg()
    AMOUNT: Msg[InputEvent] = Msg()
    FILTER: Msg[InputEvent] = Msg()
    ADD: Msg[PointerEvent] = Msg()
    REMOVE: Msg[PointerEvent, int] = Msg()


def _text(expense: Expr[Expense], field: str) -> Expr[str]:
    return cast(Expr[str], expense[field])


def _number(expense: Expr[Expense], field: str) -> Expr[int]:
    return cast(Expr[int], expense[field])


def _total(expenses: Expr[Sequence[Expense]]) -> Expr[int]:
    return Array.sum(Array.map(expenses, lambda expense: _number(expense, "amount")))


def _yen(amount: Expr[int]) -> Expr[str]:
    return "¥" + Number.format(amount, locale="ja-JP")


def _csv_cell(text: Expr[str]) -> Expr[str]:
    # Quote each field and keep spreadsheet apps from interpreting user text as a formula.
    formula = Cond.some(*(String.starts_with(text, prefix) for prefix in "=+-@\t\r\n"))
    safe = Cond.when(formula, "'" + text, text)
    escaped = String.replace_all(safe, '"', '""')
    return '"' + escaped + '"'


def _csv_url(expenses: Expr[Sequence[Expense]]) -> Expr[str]:
    def csv_row(expense: Expr[Expense]) -> Expr[str]:
        amount = String.from_number(_number(expense, "amount"))
        return (
            _csv_cell(_text(expense, "date"))
            + ","
            + _csv_cell(_text(expense, "description"))
            + ","
            + _csv_cell(_text(expense, "category"))
            + ","
            + amount
        )

    rows = Array.map(expenses, csv_row)
    joined = Array.join(rows, "\r\n")
    data = "\ufeffDate,Description,Category,Amount (JPY)\r\n" + joined + "\r\n"
    return "data:text/csv;charset=utf-8," + Url.encode_component(data)


def _panel(title_id: str, *children: ViewChild) -> VStack[Report, Msgs]:
    return VStack(
        *children,
        props={"role": "region", "aria-labelledby": title_id},
        bg="card",
        border=PANEL_BORDER,
        radius="lg",
        p="lg",
        min_w=0,
        gap="md",
    )


def _field(field_id: str, title: str, control: View[Report, Msgs]) -> View[Report, Msgs]:
    return VStack(
        View(title, tag="label", props={"for": field_id}),
        control,
        gap="xs",
        min_w=0,
        font_size="sm",
    )


def _options(names: Sequence[str]) -> list[View[Report, Msgs]]:
    return [View(name, tag="option", props={"value": name}) for name in names]


def _entry_panel(valid: Expr[bool]) -> View[Report, Msgs]:
    return _panel(
        "entry-heading",
        View(Text("Add an expense", font_size="lg"), tag="h2", props={"id": "entry-heading"}),
        _field(
            "expense-date",
            "Date",
            Input(type="date", value=Report.date, oninput=Msgs.DATE, props={"id": "expense-date"}),
        ),
        _field(
            "expense-description",
            "Description",
            Input(
                value=Report.description,
                placeholder="e.g. Train to the client site",
                oninput=Msgs.DESCRIPTION,
                props={"id": "expense-description"},
            ),
        ),
        Grid(
            _field(
                "expense-category",
                "Category",
                View(
                    *_options(CATEGORIES),
                    tag="select",
                    props={"id": "expense-category", "value": Report.category, "onchange": Msgs.CATEGORY},
                ),
            ),
            _field(
                "expense-amount",
                "Amount (JPY)",
                Input(
                    type="number",
                    value=Report.amount,
                    oninput=Msgs.AMOUNT,
                    props={"id": "expense-amount", "min": 1, "max": MAX_AMOUNT, "step": 1},
                ),
            ),
            columns=2,
            gap="sm",
        ),
        Button("Add expense", onclick=Msgs.ADD, props={"disabled": Boolean.negate(valid)}),
    )


def _row(expense: Expr[Expense]) -> View[Report, Msgs]:
    description = _text(expense, "description")
    return TableRow(
        TableCell(description, w="full", overflow_wrap="anywhere"),
        TableCell(_yen(_number(expense, "amount")), align="right", white_space="nowrap"),
        TableCell(_text(expense, "date"), white_space="nowrap"),
        TableCell(_text(expense, "category"), white_space="nowrap"),
        TableCell(
            Button(
                "Remove",
                variant="ghost",
                onclick=Msgs.REMOVE.bind(_number(expense, "id")),
                props={"aria-label": "Remove " + description},
            ),
            align="right",
            white_space="nowrap",
        ),
        props={"key": _number(expense, "id")},
    )


def _expenses_panel() -> View[Report, Msgs]:
    visible = Array.filter(
        Report.expenses,
        lambda expense: Cond.some(
            Cond.equal(Report.category_filter, ALL),
            Cond.equal(Report.category_filter, _text(expense, "category")),
        ),
    )
    empty = Cond.equal(Array.length(visible), 0)
    return _panel(
        "expenses-heading",
        HStack(
            View(Text("Expenses", font_size="lg"), tag="h2", props={"id": "expenses-heading"}),
            _field(
                "expense-filter",
                "Filter by category",
                View(
                    *_options((ALL, *CATEGORIES)),
                    tag="select",
                    props={
                        "value": Report.category_filter,
                        "onchange": Msgs.FILTER,
                        "id": "expense-filter",
                    },
                ),
            ),
            align="end",
            justify="space-between",
            flex_wrap="wrap",
            gap="md",
        ),
        Box(
            Table(
                TableHeader(
                    TableRow(
                        TableHead("Description"),
                        TableHead("Amount", align="right"),
                        TableHead("Date"),
                        TableHead("Category"),
                        TableHead("Actions", align="right"),
                    ),
                ),
                TableBody(Array.map(visible, _row)),
                props={"aria-label": "Expenses"},
                min_w=450,
            ),
            props={
                "hidden": empty,
                "tabindex": 0,
                "role": "region",
                "aria-label": "Expense table",
            },
            overflow_x="auto",
        ),
        Text(
            Cond.when(
                Cond.equal(Report.category_filter, ALL),
                "Add your first expense to start the report.",
                "No expenses in this category.",
            ),
            fg="muted-foreground",
            props={"hidden": Boolean.negate(empty)},
        ),
        Text(
            "Shown subtotal: " + _yen(_total(visible)),
            props={"role": "status"},
            w="fit",
            align_self="flex-end",
            font_weight=600,
        ),
    )


def app() -> Component[Report, Msgs]:
    amount = Number.from_string(Report.amount)
    whole_yen = Number.floor(amount)
    description = String.trim(Report.description)
    valid = Cond.every(
        Cond.not_equal(Report.date, ""),
        Cond.not_equal(description, ""),
        Number.is_finite(amount),
        amount > 0,
        amount <= MAX_AMOUNT,
        Cond.equal(whole_yen, amount),
    )
    entry: Expr[Expense] = record(
        {
            "id": Report.next_id,
            "date": Report.date,
            "description": description,
            "category": Report.category,
            "amount": whole_yen,
        }
    )
    has_expenses = Cond.not_equal(Array.length(Report.expenses), 0)

    return Component(
        Report(expenses=[], next_id=1, date="", description="", category=CATEGORIES[0], amount="", category_filter=ALL),
        Msgs.cases(
            Msgs.DATE.then(State.set(Report.date, Msgs.DATE.event.value)),
            Msgs.DESCRIPTION.then(State.set(Report.description, Msgs.DESCRIPTION.event.value)),
            Msgs.CATEGORY.then(State.set(Report.category, Msgs.CATEGORY.event.value)),
            Msgs.AMOUNT.then(State.set(Report.amount, Msgs.AMOUNT.event.value)),
            Msgs.FILTER.then(State.set(Report.category_filter, Msgs.FILTER.event.value)),
            Msgs.ADD.then(
                State.set(Report.expenses, Array.concat(Report.expenses, [entry]))
                & State.set(Report.next_id, Report.next_id + 1)
                & State.set(Report.description, "")
                & State.set(Report.amount, "")
            ),
            Msgs.REMOVE.then(
                State.set(
                    Report.expenses,
                    Array.filter(
                        Report.expenses, lambda expense: Cond.not_equal(_number(expense, "id"), Msgs.REMOVE.context)
                    ),
                )
            ),
        ),
        ThemeScope(
            View(
                VStack(
                    VStack(
                        View(Text("Expense report", font_size=css("clamp(27px, 4vw, 38px)")), tag="h1", props={}),
                        View(
                            Text(
                                "Enter whole yen amounts and download a CSV before leaving the page.",
                                fg="muted-foreground",
                            ),
                            tag="p",
                            props={},
                        ),
                        gap="xs",
                    ),
                    HStack(
                        VStack(
                            Text("Total expenses"),
                            Text(_yen(_total(Report.expenses)), font_size="2xl", font_weight=700),
                        ),
                        View(
                            Text(
                                "Download all expenses",
                                bg="secondary",
                                fg="secondary-foreground",
                                display="inline-block",
                                px="md",
                                py="sm",
                                radius="sm",
                                font_weight=600,
                            ),
                            tag="a",
                            props={
                                "className": "expense-download",
                                "href": Cond.when(has_expenses, _csv_url(Report.expenses), None),
                                "download": "expenses.csv",
                                "aria-disabled": Cond.when(has_expenses, "false", "true"),
                            },
                        ),
                        bg="card",
                        border=PANEL_BORDER,
                        radius="lg",
                        p="lg",
                        align="center",
                        justify="space-between",
                        flex_wrap="wrap",
                        gap="md",
                        props={"className": "expense-total"},
                    ),
                    Grid(
                        _entry_panel(valid),
                        _expenses_panel(),
                        align="start",
                        gap="md",
                        props={"className": "expense-layout"},
                    ),
                    gap="lg",
                    p=css("clamp(14px, 4vw, 44px)"),
                    mx="auto",
                    max_w=1200,
                ),
                tag="main",
                props={},
            ),
            theme=REPORT_THEME,
            mode="light",
            min_h=css("100dvh"),
        ),
    )


REPORT_THEME = Theme(
    colors={
        "background": "#f5f7fa",
        "foreground": "#202b3b",
        "card": "#fff",
        "primary": "#254f83",
        "primary-foreground": "#fff",
        "muted": "#eaf0f7",
        "muted-foreground": "#4d5e73",
        "border": "#d7e0eb",
        "ring": "#32649f",
    },
    # These rules handle viewport-dependent layout and properties without shorthand arguments.
    extra_css=[
        """
        .expense-download[aria-disabled="true"] { opacity:.55; }
        .expense-layout { grid-template-columns:minmax(240px,1fr) minmax(0,2fr); }
        @media (max-width:760px) { .expense-layout { grid-template-columns:minmax(0,1fr); } }
        """
    ],
)
