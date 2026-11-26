# Fleur examples

Run `uv sync` from the repository root, then choose an example.

| Example | What to try | Command |
| --- | --- | --- |
| [Counter](counter.py) | Increment or decrement a value using typed messages. | `uv run fleur dev examples/counter.py:app` |
| [Component composition](composition.py) | Enter different names in two instances of the same editor. Clear one and check the other. | `uv run fleur dev examples/composition.py:app` |
| [Theme switcher](theme_switcher.py) | Type a name, switch between Basic and Zen, and toggle light or dark mode. The input retains its value. | `uv run fleur dev examples/theme_switcher.py:app` |
| [Expense report](expense_report.py) | Add expenses, filter the table, check totals, and download a CSV. | `uv run fleur dev examples/expense_report.py:app` |

The development server opens at `http://127.0.0.1:8000`. To generate a standalone page, use
`uv run fleur build examples/counter.py:app -o dist/counter.html`.

## Expense report

Enter a date, description, category, and positive whole-yen amount. The table shows the
subtotal for the selected category. **Download all expenses** exports every entry, including
entries outside the current filter. Changes live in the current page, so download the CSV
before reloading or closing it.

Build the [expense report](expense_report.py) with
`uv run fleur build examples/expense_report.py:app -o dist/expense-report.html`.
The generated file opens directly in a browser.

## HTTP status

The [HTTP example](http_status/app.py) fetches a text file from the same server as the page.
Build the page and serve it alongside the included response file.

```bash
uv run fleur build examples/http_status/app.py:app -o dist/fleur-http/index.html
cp examples/http_status/status.txt dist/fleur-http/status.txt
uv run python -m http.server 8000 --bind 127.0.0.1 --directory dist/fleur-http
```

Open `http://127.0.0.1:8000` and click **Refresh**. To see the HTTP error state, rename
the generated copy of `status.txt` and click **Refresh** again.

See the [documentation index](../docs/README.md) for explanations of the APIs used here.
