"""Prepare a yen expense report and download it as a CSV file."""

from collections.abc import Mapping, Sequence
from typing import Literal, cast

from fleur import Array, Boolean, Component, Cond, Expr, Model, Msg, MsgGroup, Number, State, String, Url, View
from fleur.core import InputEvent, PointerEvent, SubmitEvent, record
from fleur.ui import (
    Box,
    Button,
    Card,
    EmptyState,
    Form,
    Grid,
    Heading,
    HStack,
    Input,
    Link,
    NumberField,
    Option,
    Popover,
    Select,
    SortableTableHead,
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
    field,
)

Expense = Mapping[str, str | int]
SortColumn = Literal["amount", "date"]
CATEGORIES = ("Travel", "Meals", "Supplies", "Other")
ALL = "All categories"
MAX_AMOUNT = 999_999_999  # Whole yen.


class Report(Model):
    expenses: State[Sequence[Expense]]
    next_id: State[int]
    date: State[str]
    description: State[str]
    category: State[str]
    amount: State[str]
    category_filter: State[str]
    sort_column: State[SortColumn | None]
    descending: State[bool]


class Msgs(MsgGroup):
    DATE: Msg[InputEvent] = Msg()
    DESCRIPTION: Msg[InputEvent] = Msg()
    CATEGORY: Msg[InputEvent] = Msg()
    AMOUNT: Msg[InputEvent] = Msg()
    FILTER: Msg[InputEvent] = Msg()
    SORT: Msg[PointerEvent, SortColumn] = Msg()
    CLEAR_FILTER: Msg[PointerEvent] = Msg()
    ADD: Msg[SubmitEvent] = Msg()
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


def _valid_amount(model: Report) -> Expr[bool]:
    amount = Number.from_string(model.amount)
    return Cond.every(
        Number.is_finite(amount),
        amount > 0,
        amount <= MAX_AMOUNT,
        Cond.equal(Number.floor(amount), amount),
    )


def _entry_valid(model: Report) -> Expr[bool]:
    description = String.trim(model.description)
    return Cond.every(Cond.not_equal(model.date, ""), Cond.not_equal(description, ""), _valid_amount(model))


def _amount_error(model: Report) -> Expr[str | None]:
    return Cond.when(
        Cond.some(Cond.equal(model.amount, ""), _valid_amount(model)),
        None,
        f"Enter a whole number from 1 to {MAX_AMOUNT:,}.",
    )


def _new_expense(model: Report) -> Expr[Expense]:
    return record(
        {
            "id": model.next_id,
            "date": model.date,
            "description": String.trim(model.description),
            "category": model.category,
            "amount": Number.floor(Number.from_string(model.amount)),
        }
    )


def _entry_panel(model: Report) -> View[Report, Msgs]:
    valid = _entry_valid(model)
    amount_error = _amount_error(model)
    entry = Card(
        Heading("Add an expense", level=2, font_size="lg", props={"id": "entry-heading"}),
        field(
            id="expense-date",
            label="Date",
            control=lambda attrs: Input(
                type="date", value=model.date, oninput=Msgs.DATE, props={**attrs, "required": True}
            ),
        ),
        field(
            id="expense-description",
            label="Description",
            control=lambda attrs: Input(
                value=model.description,
                placeholder="e.g. Train to the client site",
                oninput=Msgs.DESCRIPTION,
                props={**attrs, "required": True, "pattern": r".*\S.*"},
            ),
        ),
        Grid(
            field(
                id="expense-category",
                label="Category",
                control=lambda attrs: Select(
                    *(Option(name) for name in CATEGORIES),
                    value=model.category,
                    onchange=Msgs.CATEGORY,
                    props=attrs,
                ),
            ),
            field(
                id="expense-amount",
                label="Amount (JPY)",
                error=amount_error,
                control=lambda attrs: NumberField(
                    value=model.amount,
                    oninput=Msgs.AMOUNT,
                    min=1,
                    max=MAX_AMOUNT,
                    step=1,
                    required=True,
                    decrease_label="Decrease amount",
                    increase_label="Increase amount",
                    input_props={**attrs, "inputmode": "numeric"},
                ),
            ),
            min_col=css("min(100%, 10.5rem)"),
            gap="sm",
        ),
        Button("Add expense", props={"type": "submit", "disabled": Boolean.negate(valid)}),
    )
    return Form(entry, onsubmit=Msgs.ADD, prevent_default=True, props={"aria-labelledby": "entry-heading"})


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


def _expenses_panel(model: Report) -> View[Report, Msgs]:
    visible = Array.filter(
        model.expenses,
        lambda expense: Cond.some(
            Cond.equal(model.category_filter, ALL),
            Cond.equal(model.category_filter, _text(expense, "category")),
        ),
    )
    empty = Cond.equal(Array.length(visible), 0)
    by_amount = Cond.equal(model.sort_column, "amount")
    by_date = Cond.equal(model.sort_column, "date")
    ordered = Cond.when(
        by_amount,
        Array.sort_by(visible, lambda expense: _number(expense, "amount"), descending=model.descending),
        Cond.when(
            by_date,
            Array.sort_by(visible, lambda expense: _text(expense, "date"), descending=model.descending),
            visible,
        ),
    )
    return Card(
        HStack(
            Heading("Expenses", level=2, font_size="lg", props={"id": "expenses-heading"}),
            Popover(
                field(
                    id="expense-filter",
                    label="Filter by category",
                    control=lambda attrs: Select(
                        *(Option(name) for name in (ALL, *CATEGORIES)),
                        value=model.category_filter,
                        onchange=Msgs.FILTER,
                        props={**attrs, "autofocus": True},
                    ),
                ),
                id="expense-filters",
                trigger=lambda attrs: Button("Filter: " + model.category_filter, variant="secondary", props=attrs),
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
                        SortableTableHead(
                            "Amount",
                            active=by_amount,
                            descending=model.descending,
                            onsort=Msgs.SORT.bind("amount"),
                            align="right",
                        ),
                        SortableTableHead(
                            "Date", active=by_date, descending=model.descending, onsort=Msgs.SORT.bind("date")
                        ),
                        TableHead("Category"),
                        TableHead("Actions", align="right"),
                    ),
                ),
                TableBody(Array.map(ordered, _row)),
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
        Cond.when(
            empty,
            Cond.when(
                Cond.equal(Array.length(model.expenses), 0),
                EmptyState("No expenses yet", "Add your first expense using the form."),
                EmptyState(
                    "No expenses in this category",
                    "Choose another category or show the full report.",
                    Button("Show all categories", onclick=Msgs.CLEAR_FILTER, variant="secondary"),
                ),
            ),
            None,
        ),
        Text(
            "Shown subtotal: " + _yen(_total(visible)),
            props={"role": "status"},
            w="fit",
            align_self="flex-end",
            font_weight=600,
        ),
        props={"role": "region", "aria-labelledby": "expenses-heading"},
    )


def app() -> Component[Report, Msgs]:
    return Component(
        Report(
            expenses=[],
            next_id=1,
            date="",
            description="",
            category=CATEGORIES[0],
            amount="",
            category_filter=ALL,
            sort_column=None,
            descending=False,
        ),
        update=lambda model: Msgs.cases(
            Msgs.DATE.then(lambda event: State.set(Report.date, event.value)),
            Msgs.DESCRIPTION.then(lambda event: State.set(Report.description, event.value)),
            Msgs.CATEGORY.then(lambda event: State.set(Report.category, event.value)),
            Msgs.AMOUNT.then(lambda event: State.set(Report.amount, event.value)),
            Msgs.FILTER.then(lambda event: State.set(Report.category_filter, event.value)),
            Msgs.SORT.then(
                lambda _, column: (
                    State.set(
                        Report.descending,
                        Cond.every(Cond.equal(model.sort_column, column), Boolean.negate(model.descending)),
                    )
                    & State.set(Report.sort_column, column)
                )
            ),
            Msgs.CLEAR_FILTER.then(State.set(Report.category_filter, ALL)),
            Msgs.ADD.then(
                State.set(Report.expenses, Array.concat(model.expenses, [_new_expense(model)]))
                & State.set(Report.next_id, model.next_id + 1)
                & State.set(Report.description, "")
                & State.set(Report.amount, "")
            ),
            Msgs.REMOVE.then(
                lambda _, expense_id: State.set(
                    Report.expenses,
                    Array.filter(model.expenses, lambda expense: Cond.not_equal(_number(expense, "id"), expense_id)),
                )
            ),
        ),
        view=lambda model: ThemeScope(
            View(
                VStack(
                    VStack(
                        Heading("Expense report", level=1, font_size=css("clamp(27px, 4vw, 38px)")),
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
                    Card(
                        VStack(
                            Text("Total expenses"),
                            Text(_yen(_total(model.expenses)), font_size="2xl", font_weight=700),
                        ),
                        Link(
                            "Download all expenses",
                            href=_csv_url(model.expenses),
                            download="expenses.csv",
                            disabled=Cond.equal(Array.length(model.expenses), 0),
                            variant="button",
                            bg="secondary",
                            fg="secondary-foreground",
                        ),
                        flex_direction="row",
                        align="center",
                        justify="space-between",
                        flex_wrap="wrap",
                        props={"className": "expense-total"},
                    ),
                    Grid(
                        _entry_panel(model),
                        _expenses_panel(model),
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
        .expense-layout { grid-template-columns:minmax(240px,1fr) minmax(0,2fr); }
        @media (max-width:760px) { .expense-layout { grid-template-columns:minmax(0,1fr); } }
        """
    ],
)
