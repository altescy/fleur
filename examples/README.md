# Fleur examples

Run `uv sync` from the repository root, then choose an example.

| Example | What to try | Command |
| --- | --- | --- |
| [Counter](counter.py) | Increment or decrement a value using typed messages. | `uv run fleur dev examples/counter.py:app` |
| [Component composition](composition.py) | Enter different names in two instances of the same editor. Clear one and check the other. | `uv run fleur dev examples/composition.py:app` |
| [Theme switcher](theme_switcher.py) | Type a name, switch between Basic and Zen, and toggle light or dark mode. The input retains its value. | `uv run fleur dev examples/theme_switcher.py:app` |
| [Component gallery](component_gallery.py) | Try the built-in views, compare themes, and expand each preview's Python source. | `uv run fleur dev examples/component_gallery.py:app` |
| [Expense report](expense_report.py) | Add expenses, filter the table, check totals, and download a CSV. | `uv run fleur dev examples/expense_report.py:app` |

The development server opens at `http://127.0.0.1:8000`. To generate a standalone page, use
`uv run fleur build examples/counter.py:app -o dist/counter.html`.

## Component gallery

Open a group in the **Components** navigation to find a preview. Use Tab to reach a
group or link, Enter to activate it, and Escape to close an open group and return
focus to its button. Multiple groups can stay open as you move between previews.
Expand **Python source** below a preview to see the code.
Focus **Python source** and press Enter or Space to toggle it. Open several examples to compare their code.
Tab into an open code pane and use the arrow keys to scroll long sections and lines.
Try submitting the form with Enter, switching tabs with the arrow keys and Space, or closing
the dialog with Escape. The theme and dark mode controls apply to every preview.

In **Form controls**, fill in **Book details**, then turn on **Lock book details**.
Tab skips the locked fields. Unlock the group and press Enter in **Book title**
to save with the values you entered.

In **Radio groups**, use Tab to move between **Title size** and **Title alignment**.
The arrow keys change the focused setting, and the book title below shows the result.

Under **Links**, check **Include a sample expense** to enable the CSV download. Under
**Notices**, choose **Save example** for a successful save. Check **Simulate a failure on
the next save**, save again, and choose **Retry** to recover.

In **Empty states**, include the sample book and select **Finished books only**.
Choose **Show all books** to return to the reading list.

In **Progress**, select **Total known**, then **Review one book** to advance from zero
to four. Clear **Total known** to return the bar to indeterminate mode.

In **Meter**, choose **Add 10 GB** or **Free 10 GB** to change the storage used.
The gauge, numeric value, and capacity status update together.

In **Popover**, choose **Edit notes**, type a reading note, and press Escape. The
preview shows the note and focus returns to **Edit notes**. Reopen the editor to
continue editing or choose **Done** to close it from the model.

Under **Menu**, open **Note actions** and use the arrow keys to move between editing the
note, changing its favorite status and clearing it. Try Escape to return to the button.
Choose **Clear notes…** to open a confirmation. Cancel or Escape keeps the notes.
Right-click the note, or focus it and press Shift+F10, to open the same actions there.

Under **Menubar**, Tab to **Note** and open it with Enter. Use Left and Right Arrow
to switch between **Note** and **View**. Try editing the reading notes, changing
their favorite status, or choosing **Large text** to update the preview.

Under **Tooltip**, hover over **Favorite** or reach it with Tab. Move the
pointer onto the description, or press Escape to close it while focus stays on the button.
Click **Favorite** or use Space or Enter to toggle it. The **Menu** example
shows the same favorite state.

Under **Preview card**, hover over **Reading notes** or reach the link with Tab
to preview the current note. Escape dismisses the card while keeping focus on the
link. Enter takes you to the note in **Menubar**.

Try the **Dark mode** switch at the top of the gallery. Click its label or press Space
after reaching it with Tab. You can switch modes while keeping any text you have entered.

Under **Combobox**, type **little** to find two titles. Use the arrow keys and Enter to
choose one, or press Escape while editing to restore the selected title.

Under **Slider**, drag the thumb or use the arrow keys to change the reading text
size. The number and the preview update together.

Under **Toast**, choose **Add to reading list** to show a confirmation. Hover over
the confirmation or Tab to its close button to pause the timer.

In **Accordion**, use Up and Down Arrow to move between reading list topics. Press
Enter or Space to open one topic and close the previous one.

In **Toolbar**, Tab to the alignment controls, then use Left and Right Arrow to
move between them. Press Enter or Space to apply the focused alignment to the title.

In **Toggle group**, turn on **Bold**, **Italic**, or both and see the title update.
Use the arrow keys to move and Enter or Space to toggle the focused button.

In **Avatar**, the reviewer's illustration and fallback initials use the same space.
The second reviewer's sample image fails to load and displays their initials.

In **Checkbox group**, select which reading shelves to show. You can combine
several shelves, or clear every checkbox to see the empty state.

In **Number field**, adjust the reading goal by half an hour using the buttons or
arrow keys. In the expense report, **Amount (JPY)** advances in whole yen.

To add a preview, define a function returning `Preview` in
[component_gallery.py](component_gallery.py) and register its title and function in `EXAMPLES`.
The navigation and displayed source are generated from that entry. Interactive previews can
add fields to `Gallery` and messages to `Actions`.

Build a standalone copy with `uv run fleur build examples/component_gallery.py:app -o dist/component-gallery.html`.

## Expense report

Enter a date, description, category, and positive whole-yen amount. Open **Filter: All categories**
to select a category. The button shows the active filter, and the table shows the matching
expenses and subtotal. Select **Amount** or **Date** to sort the visible rows.
Select the same column again to reverse its order. **Download all expenses** exports every entry, including
entries outside the current filter. Changes live in the current page, so download the CSV
before reloading or closing it. If a category has no matching expenses, choose
**Show all categories** to restore the full list and subtotal.

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

Open `http://127.0.0.1:8000` and click **Refresh**. An indeterminate bar appears while
the request is pending, then the notice shows its result. To see the HTTP error state, rename
the generated copy of `status.txt` and click **Refresh** again. Restore the file and choose
**Retry** to see the successful response in the same notice.

See the [documentation index](../docs/README.md) for explanations of the APIs used here.
