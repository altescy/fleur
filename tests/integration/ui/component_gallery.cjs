const assert = require("node:assert/strict");
const { readFile } = require("node:fs/promises");
const { chromium } = require("playwright-core");

const isFocused = locator => locator.evaluate(el => el === document.activeElement);
const previousExampleSummary = (page, id) => page.locator(`section.specimen:has(+ #${id}) > details > summary`);

async function checkNavigationKeyboard(page, index) {
  const foundations = index.getByRole("button", { name: "Foundations", exact: true });
  const inputs = index.getByRole("button", { name: "Inputs", exact: true });
  const formLink = index.getByRole("link", { name: "Form controls", exact: true });
  const controls = await inputs.getAttribute("aria-controls");
  const panel = index.locator("#" + controls);
  assert.equal(await inputs.getAttribute("aria-expanded"), "false");
  assert(await panel.isHidden());

  await page.getByRole("switch", { name: "Dark mode" }).focus();
  await page.keyboard.press("Tab");
  assert(await isFocused(foundations));
  await page.keyboard.press("Tab");
  assert(await isFocused(inputs));
  await foundations.press("Enter");
  await inputs.press("Enter");
  assert.equal(await foundations.getAttribute("aria-expanded"), "true");
  assert.equal(await inputs.getAttribute("aria-expanded"), "true");
  assert(await panel.isVisible());
  await page.keyboard.press("Tab");
  assert(await isFocused(formLink));
  await page.keyboard.press("Escape");
  assert.equal(await inputs.getAttribute("aria-expanded"), "false");
  assert(await panel.isHidden());
  assert(await isFocused(inputs));
  assert.equal(await foundations.getAttribute("aria-expanded"), "true");

  await page.keyboard.press("Enter");
  await page.keyboard.press("Tab");
  assert(await isFocused(formLink));
  await page.keyboard.press("Enter");
  assert.equal(new URL(page.url()).hash, "#forms");
  assert(await panel.isVisible());
  assert.equal(await inputs.getAttribute("aria-expanded"), "true");
  assert.equal(await foundations.getAttribute("aria-expanded"), "true");
  const form = page.getByRole("region", { name: "Form controls", exact: true });
  assert(await isFocused(form));
  await page.keyboard.press("Tab");
  assert(await isFocused(form.getByRole("switch", { name: "Lock book details", exact: true })));
  await page.keyboard.press("Tab");
  assert(await isFocused(form.getByRole("textbox", { name: "Book title", exact: true })));
  assert(await panel.isVisible());
}

async function checkNavigationTouch(browser, url) {
  const page = await browser.newPage({ viewport: { width: 360, height: 800 }, isMobile: true, hasTouch: true });
  try {
    await page.goto(url);
    const index = page.getByRole("navigation", { name: "Components" });
    const data = index.getByRole("button", { name: "Data display", exact: true });
    const inputs = index.getByRole("button", { name: "Inputs", exact: true });
    await inputs.tap();
    assert.equal(await inputs.getAttribute("aria-expanded"), "true");
    await data.tap();
    assert.equal(await inputs.getAttribute("aria-expanded"), "true");
    assert.equal(await data.getAttribute("aria-expanded"), "true");
    assert.equal(await page.evaluate(() => document.documentElement.clientWidth), 360);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    const meterLink = index.getByRole("link", { name: "Meter", exact: true });
    assert(await meterLink.evaluate(el => {
      const bounds = el.getBoundingClientRect();
      return bounds.left >= 0 && bounds.right <= innerWidth;
    }));
    await meterLink.tap();
    assert.equal(new URL(page.url()).hash, "#meters");
    assert.equal(await data.getAttribute("aria-expanded"), "true");
    assert(await isFocused(page.getByRole("region", { name: "Meter", exact: true })));
    await index.getByRole("link", { name: "Empty states", exact: true }).tap();
    assert.equal(new URL(page.url()).hash, "#empty_states");
    assert.equal(await data.getAttribute("aria-expanded"), "true");
    await inputs.tap();
    assert.equal(await inputs.getAttribute("aria-expanded"), "false");
    assert.equal(await data.getAttribute("aria-expanded"), "true");
  } finally {
    await page.close();
  }
}

async function checkMenubar(browser, url) {
  const page = await browser.newPage();
  try {
    await page.goto(url);
    const region = page.getByRole("region", { name: "Menubar", exact: true });
    const bar = region.getByRole("menubar", { name: "Reading note commands", exact: true });
    const note = bar.getByRole("menuitem", { name: "Note", exact: true });
    const view = bar.getByRole("menuitem", { name: "View", exact: true });
    const noteMenu = bar.getByRole("menu", { name: "Note", exact: true });
    const viewMenu = bar.getByRole("menu", { name: "View", exact: true });
    const edit = noteMenu.getByRole("menuitem", { name: "Edit notes…", exact: true });
    const standard = viewMenu.getByRole("menuitem", { name: "Standard text", exact: true });
    const large = viewMenu.getByRole("menuitem", { name: "Large text", exact: true });
    const preview = region.locator("#menubar-note-preview");
    const source = region.locator("summary");
    const focusedItem = async (trigger, item, closedMenu) => {
      await trigger.and(bar.locator('[aria-expanded="true"]')).waitFor();
      assert(await closedMenu.isHidden());
      assert(await isFocused(item));
    };
    const key = value => page.keyboard.press(value);

    await region.focus();
    await key("Tab");
    assert(await isFocused(note));
    assert.equal(await note.getAttribute("tabindex"), "0");
    assert.equal(await view.getAttribute("tabindex"), "-1");
    await key("Tab");
    assert(await isFocused(source));
    await key("Shift+Tab");
    assert(await isFocused(note));
    await key("ArrowRight");
    assert(await isFocused(view));
    assert(await viewMenu.isHidden());
    await key("ArrowLeft");
    assert(await isFocused(note));

    await key("Enter");
    await focusedItem(note, edit, viewMenu);
    await key("ArrowRight");
    await focusedItem(view, standard, noteMenu);
    await key("ArrowLeft");
    await focusedItem(note, edit, viewMenu);
    await key("ArrowRight");
    await focusedItem(view, standard, noteMenu);
    await key("Escape");
    await view.and(bar.locator('[aria-expanded="false"]')).waitFor();
    assert(await viewMenu.isHidden());
    assert(await isFocused(view));

    await key("ArrowDown");
    await focusedItem(view, standard, noteMenu);
    await key("Tab");
    assert(await viewMenu.isHidden());
    assert(await isFocused(source));
    await key("Shift+Tab");
    assert(await isFocused(view));
    await key("ArrowDown");
    await focusedItem(view, standard, noteMenu);
    // Close and reopen in one browser task so any previous Tab timer runs afterward.
    await view.evaluate(trigger => {
      document.activeElement.dispatchEvent(new KeyboardEvent("keydown", { key: "Tab", bubbles: true }));
      trigger.click();
    });
    await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 0)));
    await focusedItem(view, standard, noteMenu);
    await key("Shift+Tab");
    assert(await viewMenu.isHidden());
    assert(await isFocused(previousExampleSummary(page, "menubars")));
    await key("Tab");
    assert(await isFocused(view));
    await key("ArrowLeft");
    await key("ArrowDown");
    await focusedItem(note, edit, viewMenu);
    await key("ArrowDown");
    assert(await isFocused(noteMenu.getByRole("menuitem", { name: "Add to favorites", exact: true })));
    await key("Enter");
    assert.equal(await region.getByRole("status").textContent(), "In favorites");
    assert(await isFocused(note));
    await key("Enter");
    await focusedItem(note, edit, viewMenu);
    await key("Enter");
    const editor = page.getByRole("dialog", { name: "Edit reading notes", exact: true });
    await editor.waitFor();
    const input = editor.getByRole("textbox", { name: "Reading notes", exact: true });
    assert(await isFocused(input));
    await input.fill("Revisit the final chapter.");
    await editor.getByRole("button", { name: "Done", exact: true }).click();
    await editor.waitFor({ state: "hidden" });
    assert(await isFocused(note));
    assert.equal(await preview.textContent(), "Revisit the final chapter.");

    assert.equal(await preview.evaluate(el => getComputedStyle(el).fontSize), "18px");
    await key("ArrowRight");
    await key("ArrowDown");
    await focusedItem(view, standard, noteMenu);
    await key("ArrowDown");
    assert(await isFocused(large));
    await key("Enter");
    assert.equal(await preview.evaluate(el => getComputedStyle(el).fontSize), "24px");
    assert(await viewMenu.isHidden());
    assert(await isFocused(view));
    await key("ArrowDown");
    await focusedItem(view, standard, noteMenu);
    await key("Enter");
    assert.equal(await preview.evaluate(el => getComputedStyle(el).fontSize), "18px");
  } finally {
    await page.close();
  }
}

async function checkPreviewCard(browser, url) {
  const page = await browser.newPage({ viewport: { width: 360, height: 800 } });
  try {
    await page.goto(url);
    const note = "Revisit the final chapter.";
    const form = page.getByRole("region", { name: "Form controls", exact: true });
    await form.getByRole("textbox", { name: "Notes", exact: true }).fill(note);
    const example = page.getByRole("region", { name: "Preview card", exact: true });
    const link = example.getByRole("link", { name: "Reading notes", exact: true });
    const panel = example.locator('[data-fleur-part="preview-card-panel"]');
    const card = panel.locator('[data-fleur-ui="preview-card"]');
    const source = example.locator("summary");
    assert(await panel.isHidden());
    assert.equal(await panel.getAttribute("aria-hidden"), "true");
    assert(await card.evaluate(el => el.inert));

    await link.hover();
    await panel.waitFor();
    assert(await card.getByText(note, { exact: true }).isVisible());
    const bounds = await card.boundingBox();
    assert(bounds.x >= 0 && bounds.x + bounds.width <= 360);
    await panel.hover();
    // Allow the hover leave delay to expire before checking that the card stays open.
    await page.waitForTimeout(200);
    assert(await card.isVisible());
    await page.mouse.move(359, 0);
    await panel.waitFor({ state: "hidden" });

    await example.focus();
    await page.keyboard.press("Tab");
    assert(await isFocused(link));
    await panel.waitFor();
    assert(await card.getByText(note, { exact: true }).isVisible());
    await page.keyboard.press("Tab");
    assert(await isFocused(source));
    assert(await panel.isHidden());
    await page.keyboard.press("Shift+Tab");
    assert(await isFocused(link));
    await panel.waitFor();
    await page.keyboard.press("Escape");
    assert(await panel.isHidden());
    assert(await isFocused(link));
    await page.keyboard.press("Enter");
    assert.equal(new URL(page.url()).hash, "#menubars");
    const menubar = page.getByRole("region", { name: "Menubar", exact: true });
    assert(await isFocused(menubar));
    assert(await menubar.getByRole("heading", { name: "Reading notes", exact: true }).isVisible());
    assert(await menubar.getByText(note, { exact: true }).isVisible());
  } finally {
    await page.close();
  }
}

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    await checkNavigationTouch(browser, process.argv[3]);
    await checkMenubar(browser, process.argv[3]);
    await checkPreviewCard(browser, process.argv[3]);
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const index = page.getByRole("navigation", { name: "Components" });
    await checkNavigationKeyboard(page, index);
    for (const name of [
      "Mark as a favorite", "Include a sample expense",
      "Simulate a failure on the next save", "Include a sample book", "Finished books only",
    ]) {
      const checkbox = page.getByRole("checkbox", { name, exact: true });
      const caption = page.getByText(name, { exact: true });
      assert.equal(await checkbox.isChecked(), false, name);
      await caption.click();
      assert.equal(await checkbox.isChecked(), true, name);
      await page.keyboard.press("Shift+Tab");
      assert.equal(await checkbox.evaluate(el => el === document.activeElement), false, name);
      await page.keyboard.press("Tab");
      assert(await checkbox.evaluate(el => el === document.activeElement), name);
      await page.keyboard.press("Space");
      assert.equal(await checkbox.isChecked(), false, name);
    }

    const visited = [];
    for (const group of await index.getByRole("button").all()) {
      if (await group.getAttribute("aria-expanded") === "false") await group.click();
      const groupLinks = index.locator("#" + await group.getAttribute("aria-controls")).getByRole("link");
      const names = await groupLinks.allTextContents();
      assert(names.length > 0);
      for (const name of names) {
        const section = page.getByRole("region", { name, exact: true });
        await index.getByRole("link", { name, exact: true }).click();
        const exampleId = await section.getAttribute("id");
        assert.equal(new URL(page.url()).hash, "#" + exampleId);
        assert.equal(await group.getAttribute("aria-expanded"), "true");
        visited.push(exampleId);
        const summary = section.locator("details > summary", { hasText: "Python source" });
        const code = section.locator("pre > code");
        assert(await code.isHidden());
        await summary.press("Enter");
        assert(await code.isVisible());
        assert((await code.textContent()).startsWith(`def ${exampleId}(`));
      }
      await group.click();
    }
    assert.deepEqual(visited, await page.locator("section.specimen").evaluateAll(sections => sections.map(el => el.id)));

    const buttons = page.getByRole("region", { name: "Buttons" });
    const shelfTable = page.getByRole("table", { name: "Books by shelf" });
    const books = shelfTable.getByRole("columnheader", { name: "Books", exact: true });
    const counts = shelfTable.locator("tbody tr td:last-child");
    assert.deepEqual(await counts.allTextContents(), ["3", "4", "5"]);
    await books.getByRole("button").press("Enter");
    assert.equal(await books.getAttribute("aria-sort"), "descending");
    assert.deepEqual(await counts.allTextContents(), ["5", "4", "3"]);
    assert.equal(await shelfTable.locator("tfoot td").textContent(), "12");
    const links = page.getByRole("region", { name: "Links", exact: true });
    await buttons.getByRole("button", { name: "Add one" }).click();
    assert(await buttons.locator("code").isVisible());
    assert(await links.locator("code").isVisible());
    await buttons.getByRole("button", { name: "Reset" }).press("Tab");
    assert(await buttons.locator("summary").evaluate(el => el === document.activeElement));
    await page.keyboard.press("Space");
    assert(await buttons.locator("code").isHidden());
    assert(await links.locator("code").isVisible());
    await page.keyboard.press("Space");
    await links.locator("summary").press("Enter");
    assert(await links.locator("code").isHidden());
    assert(await buttons.locator("code").isVisible());
    const form = page.getByRole("region", { name: "Form controls", exact: true });
    const details = form.getByRole("group", { name: "Book details", exact: true });
    const lock = form.getByRole("switch", { name: "Lock book details", exact: true });
    const title = details.getByLabel("Book title", { exact: true });
    const shelf = details.getByLabel("Shelf", { exact: true });
    const formNotes = details.getByLabel("Notes", { exact: true });
    const favoriteBook = details.getByRole("checkbox", { name: "Mark as a favorite", exact: true });
    const saveBook = details.getByRole("button", { name: "Save book", exact: true });
    assert(await details.evaluate(el =>
      el instanceof HTMLFieldSetElement && el.firstElementChild instanceof HTMLLegendElement
    ));
    await title.fill("");
    assert.equal(await title.getAttribute("aria-invalid"), "true");
    await title.fill("Field guide");
    await shelf.selectOption("Finished");
    await formNotes.fill("Review chapter two.");
    await favoriteBook.check();
    const checkBookDetails = async () => {
      assert.equal(await title.inputValue(), "Field guide");
      assert.equal(await shelf.inputValue(), "Finished");
      assert.equal(await formNotes.inputValue(), "Review chapter two.");
      assert(await favoriteBook.isChecked());
    };
    const bookControls = [title, shelf, formNotes, favoriteBook, saveBook];
    await lock.press("Space");
    assert(await lock.isChecked());
    assert(await details.evaluate(el => el.disabled));
    for (const control of bookControls) assert(await control.isDisabled());
    await page.keyboard.press("Tab");
    assert(await isFocused(form.locator("summary")));
    await page.keyboard.press("Shift+Tab");
    assert(await isFocused(lock));
    await page.keyboard.press("Space");
    assert.equal(await lock.isChecked(), false);
    for (const control of bookControls) assert(await control.isEnabled());
    await page.keyboard.press("Tab");
    assert(await isFocused(title));
    await checkBookDetails();

    const theme = page.getByRole("combobox", { name: "Theme" });
    await theme.selectOption("Zen");
    const darkMode = page.getByRole("switch", { name: "Dark mode" });
    const track = darkMode.locator("..").locator('[data-fleur-part="track"]');
    const checkMode = async checked => {
      assert(await page.getByRole("switch", { name: "Dark mode", checked }).isVisible());
      assert.equal(await page.locator("[data-fleur-theme]").getAttribute("data-fleur-mode"), checked ? "dark" : "light");
      await checkBookDetails();
    };
    await checkMode(false);
    const offPosition = await track.evaluate(el => getComputedStyle(el, "::before").insetInlineStart);
    await page.getByText("Dark mode", { exact: true }).click();
    await checkMode(true);
    const onPosition = await track.evaluate(async el => {
      await Promise.all(el.getAnimations({ subtree: true }).map(animation => animation.finished));
      return getComputedStyle(el, "::before").insetInlineStart;
    });
    assert.notEqual(onPosition, offPosition);
    await theme.press("Tab");
    assert(await darkMode.evaluate(el => el === document.activeElement));
    assert.equal(await track.evaluate(el => getComputedStyle(el).outlineStyle), "solid");
    await page.keyboard.press("Space");
    await checkMode(false);
    await page.keyboard.press("Space");
    await checkMode(true);
    assert.equal(await buttons.getByRole("status").textContent(), "Count: 1");
    const formUrl = page.url();
    await title.press("Enter");
    assert.equal(await form.getByRole("status").textContent(), "Saved Field guide to Finished · Favorite");
    assert.equal(page.url(), formUrl);

    const radios = page.getByRole("region", { name: "Radio groups", exact: true });
    const size = radios.getByRole("radiogroup", { name: "Title size" });
    const alignment = radios.getByRole("radiogroup", { name: "Title alignment" });
    const small = size.getByRole("radio", { name: "Small" });
    const large = size.getByRole("radio", { name: "Large" });
    const center = alignment.getByRole("radio", { name: "Center" });
    const right = alignment.getByRole("radio", { name: "Right" });
    const preview = radios.getByText("Field guide", { exact: true });
    const fontSize = () => preview.evaluate(el => parseFloat(getComputedStyle(el).fontSize));
    const largeSize = await fontSize();
    const focused = radio => radio.evaluate(el => el === document.activeElement);
    assert(await large.isChecked());
    assert(await center.isChecked());
    await form.locator("summary").click();
    await page.keyboard.press("Tab");
    assert(await focused(large));
    await page.keyboard.press("ArrowLeft");
    assert(await focused(small));
    assert(await small.isChecked());
    assert(await center.isChecked());
    assert(await fontSize() < largeSize);
    await page.keyboard.press("Tab");
    assert(await focused(center));
    await page.keyboard.press("ArrowRight");
    assert(await focused(right));
    assert(await right.isChecked());
    assert(await small.isChecked());
    assert.equal(await preview.evaluate(el => getComputedStyle(el).textAlign), "right");

    const include = links.getByRole("checkbox");
    const csv = links.getByRole("link", { name: "Download sample CSV" });
    const downloads = [];
    page.on("download", download => downloads.push(download));
    const originalUrl = page.url();
    assert.equal(await csv.getAttribute("aria-disabled"), "true");
    assert.equal(await csv.getAttribute("href"), null);
    assert.equal(await csv.getAttribute("download"), null);
    await include.press("Tab");
    assert.equal(await csv.evaluate(el => el === document.activeElement), false);
    await csv.click({ force: true });
    await include.check();
    await include.press("Tab");
    assert(await csv.evaluate(el => el === document.activeElement));
    const [file] = await Promise.all([page.waitForEvent("download"), page.keyboard.press("Enter")]);
    assert.equal(file.suggestedFilename(), "sample-expenses.csv");
    assert.equal(await readFile(await file.path(), "utf8"), "Description,JPY\nTrain fare,420\n");
    await include.uncheck();
    assert.equal(await csv.getAttribute("href"), null);
    await csv.click({ force: true });
    assert.equal(page.url(), originalUrl);
    assert.equal(downloads.length, 1);

    const notices = page.getByRole("region", { name: "Notices", exact: true });
    const notice = notices.locator('[data-fleur-ui="notice"]');
    const message = notice.getByRole("status");
    const save = notice.getByRole("button", { name: "Save example" });
    assert.equal(await message.textContent(), "Ready to save.");
    await save.click();
    assert.equal(await message.textContent(), "Changes saved.");
    assert.equal(await notice.getAttribute("data-fleur-variant"), "success");
    await notices.getByRole("checkbox").check();
    await save.click();
    assert.equal(await message.textContent(), "Save failed. Your changes are still here.");
    assert.equal(await notice.getAttribute("data-fleur-variant"), "error");
    const retry = notice.getByRole("button", { name: "Retry" });
    assert(await retry.evaluate(el => el === document.activeElement));
    await retry.press("Enter");
    assert.equal(await message.textContent(), "Changes saved.");
    assert.equal(await notice.getAttribute("data-fleur-variant"), "success");
    assert(await save.isVisible());

    const progress = page.getByRole("region", { name: "Progress", exact: true });
    const bar = progress.getByRole("progressbar", { name: "Book review" });
    const known = progress.getByRole("checkbox", { name: "Total known" });
    const advance = progress.getByRole("button", { name: "Review one book" });
    const caption = value => progress.getByText(`${value} of 4 books reviewed`, { exact: true });
    const counting = progress.getByText("Counting books…", { exact: true });
    assert(await counting.isVisible());
    assert.equal(await bar.getAttribute("value"), null);
    assert.equal(await bar.evaluate(el => el.position), -1);
    await known.check();
    assert.equal(await bar.getAttribute("value"), "0");
    assert(await caption(0).isVisible());
    assert.equal(await bar.evaluate(el => el.max), 4);
    for (let value = 1; value <= 4; value++) {
      await advance.click();
      assert.deepEqual(await bar.evaluate(el => [el.value, el.position]), [value, value / 4]);
      assert(await caption(value).isVisible());
    }
    assert(await advance.isDisabled());
    await known.uncheck();
    assert(await counting.isVisible());
    assert.equal(await bar.getAttribute("value"), null);
    assert.equal(await bar.evaluate(el => el.position), -1);
    await known.check();
    assert.equal(await bar.evaluate(el => el.position), 1);
    assert(await caption(4).isVisible());
    await progress.getByRole("button", { name: "Reset count" }).click();
    assert.equal(await bar.evaluate(el => el.position), 0);
    assert(await caption(0).isVisible());

    const meterExample = page.getByRole("region", { name: "Meter", exact: true });
    const meter = meterExample.getByRole("meter", { name: "Storage usage", exact: true });
    const addStorage = meterExample.getByRole("button", { name: "Add 10 GB", exact: true });
    const freeStorage = meterExample.getByRole("button", { name: "Free 10 GB", exact: true });
    const usage = meterExample.getByRole("status");
    const checkStorage = async (value, condition) => {
      assert(await meter.isVisible());
      assert.equal(await meter.getAttribute("value"), String(value));
      assert.equal(await meter.evaluate(el => el.value), value);
      assert.equal(await usage.textContent(), `${value} / 100 GB`);
      assert(await usage.isVisible());
      if (condition) assert(await meterExample.getByText(condition, { exact: true }).isVisible());
    };
    assert.deepEqual(await meter.evaluate(el => [
      el instanceof HTMLMeterElement, el.min, el.max, el.low, el.high, el.optimum,
    ]), [true, 0, 100, 60, 85, 0]);
    await checkStorage(50, "Within capacity");
    await addStorage.click();
    await checkStorage(60, "Within capacity");
    await addStorage.click();
    await checkStorage(70, "Approaching capacity");
    await addStorage.click();
    await addStorage.click();
    await checkStorage(90, "Nearly full");
    await addStorage.click();
    await checkStorage(100, "Storage full");
    assert(await addStorage.isDisabled());
    await freeStorage.press("Enter");
    await checkStorage(90, "Nearly full");
    for (let value = 80; value >= 0; value -= 10) {
      await freeStorage.click();
      await checkStorage(value);
    }
    await checkStorage(0, "Within capacity");
    assert(await freeStorage.isDisabled());

    const emptyStates = page.getByRole("region", { name: "Empty states", exact: true });
    const finishedOnly = emptyStates.getByRole("checkbox", { name: "Finished books only" });
    const book = emptyStates.getByText("The Secret Garden · Reading", { exact: true });
    assert(await emptyStates.getByRole("heading", { name: "Your reading list is empty" }).isVisible());
    await emptyStates.getByRole("checkbox", { name: "Include a sample book" }).check();
    assert(await book.isVisible());
    await finishedOnly.check();
    assert(await book.isHidden());
    assert(await emptyStates.getByRole("heading", { name: "No finished books" }).isVisible());
    await emptyStates.getByRole("button", { name: "Show all books" }).click();
    assert.equal(await finishedOnly.isChecked(), false);
    assert(await book.isVisible());

    const first = page.getByRole("tab", { name: "Overview" });
    const next = page.getByRole("tab", { name: "Keyboard" });
    await first.press("ArrowRight");
    assert.equal(await first.getAttribute("aria-selected"), "true");
    assert(await next.evaluate(el => el === document.activeElement));
    await page.keyboard.press("Space");
    assert(await page.getByRole("tabpanel", { name: "Keyboard" }).isVisible());
    const trigger = page.getByRole("button", { name: "Open dialog" });
    await trigger.click();
    const dialog = page.getByRole("dialog", { name: "Reading notes" });
    await dialog.waitFor();
    assert(await dialog.getByRole("button", { name: "Done" }).evaluate(el => el === document.activeElement));
    await page.keyboard.press("Escape");
    await dialog.waitFor({ state: "hidden" });
    assert(await trigger.evaluate(el => el === document.activeElement));

    await page.setViewportSize({ width: 360, height: 800 });
    const editorTrigger = page.getByRole("button", { name: "Edit notes" });
    const editor = page.getByRole("dialog", { name: "Edit notes" });
    await editorTrigger.press("Enter");
    const notes = editor.getByRole("textbox", { name: "Reading notes" });
    assert(await focused(notes));
    await notes.fill("Compare with chapter two.");
    await page.keyboard.press("Escape");
    await editor.waitFor({ state: "hidden" });
    assert(await focused(editorTrigger));
    await editorTrigger.press("Space");
    assert.equal(await notes.inputValue(), "Compare with chapter two.");
    await editor.getByRole("button", { name: "Done" }).click();
    await editor.waitFor({ state: "hidden" });
    assert(await page.getByRole("region", { name: "Popover", exact: true }).getByText("Compare with chapter two.", { exact: true }).isVisible());

    const menus = page.getByRole("region", { name: "Menu", exact: true });
    const actions = menus.getByRole("button", { name: "Note actions" });
    const menu = menus.getByRole("menu", { name: "Note actions" });
    const editNotes = menu.getByRole("menuitem", { name: "Edit notes…" });
    const clearNotes = menu.getByRole("menuitem", { name: "Clear notes…" });
    const notePreview = menus.getByRole("status");
    const menuOpened = () => actions.and(menus.locator('[aria-expanded="true"]')).waitFor();
    assert.equal(await actions.getAttribute("aria-expanded"), "false");
    await actions.press("Enter");
    await menu.waitFor();
    await menuOpened();
    assert.equal(await actions.getAttribute("aria-controls"), await menu.getAttribute("id"));
    assert(await focused(editNotes));
    const menuBox = await menu.boundingBox();
    assert(menuBox.x >= 0 && menuBox.x + menuBox.width <= 360);
    await page.keyboard.press("ArrowDown");
    assert(await focused(menu.getByRole("menuitem", { name: "Remove from favorites" })));
    await page.keyboard.press("Enter");
    assert(await menu.isHidden());
    assert(await focused(actions));
    assert(await menus.getByText("Outside favorites", { exact: true }).isVisible());

    await actions.press("Space");
    await menuOpened();
    assert(await focused(editNotes));
    await page.keyboard.press("ArrowDown");
    assert(await focused(menu.getByRole("menuitem", { name: "Add to favorites" })));
    await page.keyboard.press("Space");
    assert(await menu.isHidden());
    assert(await menus.getByText("In favorites", { exact: true }).isVisible());

    await actions.press("ArrowUp");
    assert(await focused(clearNotes));
    await page.keyboard.press("ArrowDown");
    assert(await focused(editNotes));
    await page.keyboard.press("ArrowUp");
    assert(await focused(clearNotes));
    await page.keyboard.press("Home");
    assert(await focused(editNotes));
    await page.keyboard.press("Escape");
    assert(await menu.isHidden());
    assert(await focused(actions));
    await actions.and(menus.locator('[aria-expanded="false"]')).waitFor();

    await actions.press("ArrowDown");
    await page.keyboard.press("Enter");
    const noteDialog = menus.getByRole("dialog", { name: "Edit reading notes" });
    await noteDialog.waitFor();
    assert(await menu.isHidden());
    const noteInput = noteDialog.getByRole("textbox", { name: "Reading notes" });
    assert(await focused(noteInput));
    await noteInput.fill("Read the final chapter.");
    await noteDialog.getByRole("button", { name: "Done" }).click();
    await noteDialog.waitFor({ state: "hidden" });
    assert(await focused(actions));
    assert.equal(await notePreview.textContent(), "Read the final chapter.");

    const noteTarget = menus.getByRole("group", { name: "Reading note", exact: true });
    const contextMenu = menus.getByRole("menu", { name: "Reading note", exact: true });
    const contextEdit = contextMenu.getByRole("menuitem", { name: "Edit notes…" });
    await noteTarget.scrollIntoViewIfNeeded();
    const noteBox = await noteTarget.boundingBox();
    await noteTarget.click({ button: "right", position: { x: 20, y: 12 } });
    await contextMenu.waitFor();
    assert(await focused(contextEdit));
    assert(await menu.isHidden());
    const contextBox = await contextMenu.boundingBox();
    assert(Math.abs(contextBox.x - (noteBox.x + 20)) <= 2);
    assert(Math.abs(contextBox.y - Math.min(noteBox.y + 12, 800 - contextBox.height - 8)) <= 2);
    await page.keyboard.press("Escape");
    assert(await contextMenu.isHidden());
    assert(await focused(noteTarget));

    await noteTarget.press("Shift+F10");
    await contextMenu.waitFor();
    assert(await focused(contextEdit));
    assert(await contextEdit.evaluate(el => {
      const { outlineColor, outlineStyle } = getComputedStyle(el);
      return outlineStyle === "solid" && outlineColor !== "rgba(0, 0, 0, 0)";
    }));
    const keyboardBox = await contextMenu.boundingBox();
    assert(Math.abs(keyboardBox.x - noteBox.x) <= 2);
    assert(Math.abs(keyboardBox.y - Math.min(noteBox.y + noteBox.height, 800 - keyboardBox.height - 8)) <= 2);
    await page.keyboard.press("ArrowDown");
    assert(await focused(contextMenu.getByRole("menuitem", { name: "Remove from favorites" })));
    await page.keyboard.press("Enter");
    assert(await contextMenu.isHidden());
    assert(await focused(noteTarget));
    assert(await menus.getByText("Outside favorites", { exact: true }).isVisible());

    await noteTarget.click({ button: "right", position: { x: noteBox.width - 5, y: 12 } });
    await contextMenu.waitFor();
    const edgeBox = await contextMenu.boundingBox();
    assert(edgeBox.x >= 8 && edgeBox.x + edgeBox.width <= 352);
    await page.keyboard.press("ArrowDown");
    assert(await focused(contextMenu.getByRole("menuitem", { name: "Add to favorites" })));
    await page.keyboard.press("Enter");
    assert(await menus.getByText("In favorites", { exact: true }).isVisible());

    await noteTarget.press("Shift+F10");
    await contextMenu.waitFor();
    await page.keyboard.press("Enter");
    await noteDialog.waitFor();
    assert(await contextMenu.isHidden());
    assert(await focused(noteInput));
    await noteDialog.getByRole("button", { name: "Done" }).click();
    await noteDialog.waitFor({ state: "hidden" });
    assert(await focused(noteTarget));
    assert.equal(await notePreview.textContent(), "Read the final chapter.");

    await noteTarget.press("Shift+F10");
    await contextMenu.waitFor();
    await menus.getByRole("heading", { name: "Reading notes", exact: true }).click();
    await contextMenu.waitFor({ state: "hidden" });

    await actions.click();
    await menuOpened();
    await page.keyboard.press("End");
    assert(await focused(clearNotes));
    await clearNotes.click();
    const clearWarning = menus.getByRole("alertdialog", { name: "Clear reading notes?" });
    const cancelClearing = clearWarning.getByRole("button", { name: "Cancel" });
    const confirmClearing = clearWarning.getByRole("button", { name: "Clear notes" });
    async function checkClearWarning() {
      await clearWarning.waitFor();
      assert(await clearWarning.evaluate(el => el.matches(":modal")));
      assert.equal(await clearWarning.getAttribute("aria-modal"), "true");
      assert(await menu.isHidden());
      assert(await focused(cancelClearing));
      assert.equal(await notePreview.textContent(), "Read the final chapter.");
    }
    async function openClearWarning() {
      await actions.press("ArrowUp");
      await menuOpened();
      assert(await focused(clearNotes));
      await page.keyboard.press("Enter");
      await checkClearWarning();
    }
    async function dismissClearWarning(action, expectedNotes) {
      const closeEvent = await clearWarning.evaluateHandle(el => ({
        done: new Promise(resolve => el.addEventListener("close", () => resolve(), { once: true })),
      }));
      await action();
      await clearWarning.waitFor({ state: "hidden" });
      await closeEvent.evaluate(event => event.done);
      await closeEvent.dispose();
      assert(await focused(actions));
      assert.equal(await notePreview.textContent(), expectedNotes);
    }
    await checkClearWarning();
    assert.equal(await clearWarning.evaluate(el => {
      const id = el.getAttribute("aria-describedby");
      return el.ownerDocument.getElementById(id)?.textContent;
    }), "This will permanently remove the current reading notes.");
    await dismissClearWarning(() => page.keyboard.press("Enter"), "Read the final chapter.");
    await openClearWarning();
    await dismissClearWarning(() => page.keyboard.press("Escape"), "Read the final chapter.");
    await openClearWarning();
    await dismissClearWarning(() => cancelClearing.click(), "Read the final chapter.");
    await openClearWarning();
    await page.keyboard.press("Tab");
    assert(await focused(confirmClearing));
    await dismissClearWarning(() => page.keyboard.press("Space"), "No reading notes yet.");
    await actions.press("ArrowUp");
    assert(await focused(clearNotes));
    assert(await clearNotes.isDisabled());
    await page.keyboard.press("Enter");
    assert(await menu.isVisible());
    await clearNotes.click({ force: true });
    assert(await menu.isVisible());
    await page.keyboard.press("Tab");
    await menu.waitFor({ state: "hidden" });
    assert(await focused(noteTarget));
    await actions.press("Space");
    await menuOpened();
    await page.keyboard.press("Shift+Tab");
    await menu.waitFor({ state: "hidden" });
    assert(await focused(actions));
    await actions.click();
    await menuOpened();
    await menus.getByRole("heading", { name: "Reading notes", exact: true }).click();
    assert(await menu.isHidden());

    const tooltips = page.getByRole("region", { name: "Tooltip", exact: true });
    const favorite = tooltips.getByRole("button", { name: "Favorite", exact: true });
    const tooltip = tooltips.getByRole("tooltip");
    const hint = tooltips.getByText("Favorites appear in your saved reading list.", { exact: true });
    const source = tooltips.locator("summary");
    const checkFavorite = async pressed => {
      assert(await tooltips.getByRole("button", { name: "Favorite", exact: true, pressed }).isVisible());
      assert.equal(await favorite.getAttribute("aria-pressed"), String(pressed));
      assert(await menus.getByText(pressed ? "In favorites" : "Outside favorites", { exact: true }).isVisible());
    };
    const checkFavoriteMenuItem = async name => {
      await actions.press("ArrowDown");
      await menuOpened();
      assert(await menu.getByRole("menuitem", { name, exact: true }).isVisible());
      await page.keyboard.press("Escape");
    };
    assert.equal(await favorite.getAttribute("type"), "button");
    await checkFavorite(true);
    assert(await tooltip.isHidden());
    await favorite.hover();
    await tooltip.waitFor();
    assert.equal(await favorite.getAttribute("aria-describedby"), await tooltip.getAttribute("id"));
    const tooltipBox = await tooltip.boundingBox();
    assert(tooltipBox.x >= 0 && tooltipBox.x + tooltipBox.width <= 360);
    await hint.hover();
    // Wait beyond the pointer-leave grace period to catch an unintended dismissal.
    await page.waitForTimeout(200);
    assert(await tooltip.isVisible());
    await source.hover();
    await tooltip.waitFor({ state: "hidden" });

    await previousExampleSummary(page, "tooltips").press("Enter");
    await page.keyboard.press("Tab");
    assert(await focused(favorite));
    await tooltip.waitFor();
    await page.keyboard.press("Escape");
    assert(await tooltip.isHidden());
    assert(await focused(favorite));
    await page.keyboard.press("Tab");
    assert(await focused(source));
    await page.keyboard.press("Shift+Tab");
    await tooltip.waitFor();
    await page.keyboard.press("Tab");
    assert(await tooltip.isHidden());
    await favorite.hover();
    await tooltip.waitFor();
    await page.keyboard.press("Escape");
    assert(await tooltip.isHidden());
    assert(await focused(source));

    await favorite.click();
    await checkFavorite(false);
    assert(await focused(favorite));
    await page.keyboard.press("Space");
    await checkFavorite(true);
    assert(await focused(favorite));
    await checkFavoriteMenuItem("Remove from favorites");
    await favorite.press("Enter");
    await checkFavorite(false);
    assert(await focused(favorite));
    await checkFavoriteMenuItem("Add to favorites");

    const catalog = page.getByRole("region", { name: "Combobox", exact: true });
    const search = catalog.getByRole("combobox", { name: "Book title in catalog" });
    const results = catalog.getByRole("listbox", { name: "Book title in catalog" });
    const selectedBook = catalog.getByText(/^Selected book: /);
    const checkCatalogWidth = async () => {
      const previewWidth = await catalog.locator(".preview").evaluate(el => {
        const style = getComputedStyle(el);
        return el.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
      });
      assert(Math.abs((await search.boundingBox()).width - previewWidth) <= 1);
      const statusLines = await selectedBook.evaluate(el => {
        const range = document.createRange();
        range.selectNodeContents(el);
        return range.getClientRects().length;
      });
      assert.equal(statusLines, 1);
    };
    assert.equal(await search.inputValue(), "The Secret Garden");
    await checkCatalogWidth();
    assert(await results.isHidden());
    await search.fill("ＬＩＴＴＬＥ");
    assert.equal(await search.getAttribute("aria-expanded"), "true");
    assert.equal(await search.getAttribute("aria-controls"), await results.getAttribute("id"));
    assert.deepEqual(await results.getByRole("option").allTextContents(), ["A Little Princess", "Little Women"]);
    assert.equal(await selectedBook.textContent(), "Selected book: The Secret Garden");
    const searchBox = await search.boundingBox();
    const resultBox = await results.locator("..").boundingBox();
    assert(Math.abs(searchBox.width - resultBox.width) <= 2);
    assert(Math.abs(searchBox.x - resultBox.x) <= 1);
    assert(resultBox.x >= 0 && resultBox.x + resultBox.width <= 360);
    await page.keyboard.press("ArrowDown");
    const littlePrincess = results.getByRole("option", { name: "A Little Princess" });
    assert.equal(await search.getAttribute("aria-activedescendant"), await littlePrincess.getAttribute("id"));
    await page.keyboard.press("ArrowDown");
    const littleWomen = results.getByRole("option", { name: "Little Women" });
    assert.equal(await search.getAttribute("aria-activedescendant"), await littleWomen.getAttribute("id"));
    assert(await focused(search));
    await page.keyboard.press("Enter");
    assert(await results.isHidden());
    assert.equal(await search.inputValue(), "Little Women");
    assert.equal(await selectedBook.textContent(), "Selected book: Little Women");
    assert.equal(await search.getAttribute("aria-activedescendant"), null);
    assert(await focused(search));

    await search.fill("wind");
    assert.deepEqual(await results.getByRole("option").allTextContents(), ["The Wind in the Willows"]);
    await page.keyboard.press("ArrowDown");
    await page.keyboard.press("Escape");
    assert(await results.isHidden());
    assert.equal(await search.getAttribute("aria-expanded"), "false");
    assert.equal(await search.inputValue(), "Little Women");
    assert.equal(await selectedBook.textContent(), "Selected book: Little Women");
    assert(await focused(search));

    await search.fill("no such book");
    assert.equal(await results.getByRole("option").count(), 0);
    assert(await catalog.getByText("No books match that title.", { exact: true }).isVisible());
    await page.keyboard.press("ArrowDown");
    await page.keyboard.press("Enter");
    assert.equal(await selectedBook.textContent(), "Selected book: Little Women");
    await page.keyboard.press("Tab");
    assert(await results.isHidden());
    assert.equal(await search.inputValue(), "Little Women");
    await search.click();
    assert(await littleWomen.evaluate(el => el.getAttribute("aria-selected") === "true"));
    await results.getByRole("option", { name: "The Wind in the Willows" }).click();
    assert(await results.isHidden());
    assert.equal(await search.inputValue(), "The Wind in the Willows");
    assert.equal(await selectedBook.textContent(), "Selected book: The Wind in the Willows");
    assert(await focused(search));
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.setViewportSize({ width: 1000, height: 750 });
    await checkCatalogWidth();

    const sliders = page.getByRole("region", { name: "Slider", exact: true });
    const slider = sliders.getByRole("slider", { name: "Reading text size" });
    const reading = sliders.locator("#reading-preview");
    const checkReadingSize = async size => {
      assert.equal(await slider.inputValue(), String(size));
      assert.equal(await slider.getAttribute("aria-valuetext"), `${size} pixels`);
      assert.equal(await sliders.locator("#reading-size-value").textContent(), `${size} px`);
      assert.equal(await reading.evaluate(el => getComputedStyle(el).fontSize), `${size}px`);
    };
    await checkReadingSize(18);
    await slider.press("ArrowRight");
    await checkReadingSize(20);
    await slider.press("ArrowLeft");
    await checkReadingSize(18);
    await slider.press("Home");
    await slider.press("ArrowLeft");
    await checkReadingSize(14);
    await slider.press("End");
    await slider.press("ArrowRight");
    await checkReadingSize(30);

    await page.setViewportSize({ width: 360, height: 800 });
    await slider.scrollIntoViewIfNeeded();
    const sliderBox = await slider.boundingBox();
    const trackY = sliderBox.y + sliderBox.height / 2;
    const trackCenter = sliderBox.x + sliderBox.width / 2;
    await page.mouse.click(trackCenter, trackY);
    await checkReadingSize(22);
    await page.mouse.move(trackCenter, trackY);
    await page.mouse.down();
    await page.mouse.move(sliderBox.x + sliderBox.width * .75, trackY, { steps: 6 });
    await checkReadingSize(26);
    await page.mouse.up();
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));

    const accordion = page.getByRole("group", { name: "Reading list help" });
    const summaries = accordion.locator("details > summary");
    const [addTopic, statusTopic, notesTopic] = await summaries.all();
    const openTopics = accordion.locator("details[open] > summary");
    const addInstructions = accordion.getByText(/The book stays on the list/);
    const statusInstructions = accordion.getByText(/choose To read, Reading, or Finished/);
    assert.equal(await openTopics.textContent(), "Add a book to the reading list");
    assert(await addInstructions.isVisible());
    await addTopic.press("ArrowDown");
    assert(await focused(statusTopic));
    assert(await addInstructions.isVisible());
    await page.keyboard.press("Enter");
    assert.deepEqual(await openTopics.allTextContents(), ["Change a book’s reading status"]);
    assert(await statusInstructions.isVisible());
    assert(await addInstructions.isHidden());
    await page.keyboard.press("ArrowDown");
    assert(await focused(notesTopic));
    await page.keyboard.press("Space");
    assert.deepEqual(await openTopics.allTextContents(), ["Edit reading notes"]);
    assert(await statusInstructions.isHidden());
    await page.keyboard.press("Space");
    assert.equal(await openTopics.count(), 0);
    await page.keyboard.press("Home");
    assert(await focused(addTopic));
    await page.keyboard.press("End");
    assert(await focused(notesTopic));
    await page.keyboard.press("ArrowDown");
    assert(await focused(addTopic));
    await page.keyboard.press("ArrowUp");
    assert(await focused(notesTopic));
    await page.keyboard.press("Home");
    await page.keyboard.press("Tab");
    assert(await focused(statusTopic));
    assert(await page.getByRole("region", { name: "Accordion", exact: true }).locator("pre").isVisible());

    const alignmentToolbar = page.getByRole("toolbar", { name: "Reading title alignment" });
    const alignLeft = alignmentToolbar.getByRole("button", { name: "Left" });
    const alignCenter = alignmentToolbar.getByRole("button", { name: "Center" });
    const alignRight = alignmentToolbar.getByRole("button", { name: "Right" });
    const toolbarTitle = page.locator("#toolbar-reading-title");
    const toolbarSource = page.getByRole("region", { name: "Toolbar", exact: true }).locator("summary");
    const actualAlignment = () => toolbarTitle.evaluate(el => getComputedStyle(el).textAlign);
    const toolbarStops = () => alignmentToolbar.locator('button[tabindex="0"]').count();
    const accordionSource = page.getByRole("region", { name: "Accordion", exact: true }).locator("details.example-source > summary");
    await accordionSource.press("Enter");
    await page.keyboard.press("Tab");
    assert(await focused(alignLeft));
    assert.equal(await toolbarStops(), 1);
    assert.equal(await alignRight.getAttribute("aria-pressed"), "true");
    await page.keyboard.press("ArrowRight");
    assert(await focused(alignCenter));
    assert.equal(await actualAlignment(), "right");
    await page.keyboard.press("Space");
    assert.equal(await alignCenter.getAttribute("aria-pressed"), "true");
    assert.equal(await alignRight.getAttribute("aria-pressed"), "false");
    assert.equal(await actualAlignment(), "center");
    await page.keyboard.press("ArrowLeft");
    assert(await focused(alignLeft));
    await page.keyboard.press("Enter");
    assert.equal(await alignLeft.getAttribute("aria-pressed"), "true");
    assert.equal(await actualAlignment(), "left");
    assert.equal(await toolbarStops(), 1);
    await page.keyboard.press("Tab");
    assert(await focused(toolbarSource));
    await page.keyboard.press("Shift+Tab");
    assert(await focused(alignLeft));

    const emphasis = page.getByRole("group", { name: "Reading title emphasis" });
    const bold = emphasis.getByRole("button", { name: "Bold" });
    const italic = emphasis.getByRole("button", { name: "Italic" });
    const emphasisTitle = page.locator("#toggle-reading-title");
    const checkEmphasis = async (isBold, isItalic) => {
      assert.equal(await bold.getAttribute("aria-pressed"), String(isBold));
      assert.equal(await italic.getAttribute("aria-pressed"), String(isItalic));
      assert.deepEqual(
        await emphasisTitle.evaluate(el => {
          const style = getComputedStyle(el);
          return [style.fontWeight, style.fontStyle];
        }),
        [isBold ? "700" : "400", isItalic ? "italic" : "normal"]
      );
    };
    await checkEmphasis(false, false);
    await previousExampleSummary(page, "toggle_groups").press("Enter");
    await page.keyboard.press("Tab");
    assert(await focused(bold));
    await page.keyboard.press("ArrowRight");
    assert(await focused(italic));
    await checkEmphasis(false, false);
    await page.keyboard.press("Space");
    await checkEmphasis(false, true);
    await page.keyboard.press("ArrowLeft");
    assert(await focused(bold));
    await page.keyboard.press("Enter");
    await checkEmphasis(true, true);
    await page.keyboard.press("ArrowRight");
    await checkEmphasis(true, true);
    await page.keyboard.press("Space");
    await checkEmphasis(true, false);
    await page.keyboard.press("ArrowLeft");
    await page.keyboard.press("Enter");
    await checkEmphasis(false, false);

    const reviewers = page.getByRole("region", { name: "Avatar", exact: true });
    const leadReviewer = reviewers.getByRole("img", { name: "Lead reviewer", exact: true });
    const secondReviewer = reviewers.getByRole("img", { name: "Second reviewer", exact: true });
    await leadReviewer.locator("img").waitFor();
    assert(await leadReviewer.getByText("LR", { exact: true }).isHidden());
    assert(await secondReviewer.getByText("SR", { exact: true }).isVisible());
    assert(await secondReviewer.locator("img").isHidden());
    const leadBox = await leadReviewer.boundingBox();
    const secondBox = await secondReviewer.boundingBox();
    assert.equal(leadBox.width, secondBox.width);
    assert.equal(leadBox.height, secondBox.height);

    const shelfFilters = page.getByRole("region", { name: "Checkbox group", exact: true });
    const shelfChoices = shelfFilters.getByRole("group", { name: "Shelves to show" });
    const toRead = shelfChoices.getByRole("checkbox", { name: "To read", exact: true });
    const readingShelf = shelfChoices.getByRole("checkbox", { name: "Reading", exact: true });
    const finishedShelf = shelfChoices.getByRole("checkbox", { name: "Finished", exact: true });
    const shelfBooks = shelfFilters.getByRole("list", { name: "Books on selected shelves" }).getByRole("listitem");
    assert(await readingShelf.isChecked());
    assert.deepEqual(await shelfBooks.allTextContents(), ["The Secret Garden · Reading"]);

    await shelfChoices.getByText("To read", { exact: true }).click();
    assert(await toRead.isChecked());
    assert(await focused(toRead));
    assert.deepEqual(await shelfBooks.allTextContents(), ["Pride and Prejudice · To read", "The Secret Garden · Reading"]);
    await page.keyboard.press("Tab");
    assert(await focused(readingShelf));
    await page.keyboard.press("Tab");
    assert(await focused(finishedShelf));
    await page.keyboard.press("Space");
    assert(await finishedShelf.isChecked());
    assert.deepEqual(
      await shelfBooks.allTextContents(),
      ["Pride and Prejudice · To read", "The Secret Garden · Reading", "Little Women · Finished"]
    );
    await shelfChoices.getByText("Reading", { exact: true }).click();
    assert(!(await readingShelf.isChecked()));
    assert(await toRead.isChecked());
    assert(await finishedShelf.isChecked());
    assert.deepEqual(await shelfBooks.allTextContents(), ["Pride and Prejudice · To read", "Little Women · Finished"]);
    await shelfChoices.getByText("To read", { exact: true }).click();
    await shelfChoices.getByText("Finished", { exact: true }).click();
    assert(await shelfFilters.getByRole("heading", { name: "No shelves selected" }).isVisible());
    assert.equal(await shelfBooks.count(), 0);

    const numberFields = page.getByRole("region", { name: "Number field", exact: true });
    const readingGoal = numberFields.getByRole("spinbutton", { name: "Reading goal (hours per week)" });
    const increaseGoal = numberFields.getByRole("button", { name: "Increase reading goal" });
    const decreaseGoal = numberFields.getByRole("button", { name: "Decrease reading goal" });
    const goalEvents = await readingGoal.evaluateHandle(el => {
      const events = [];
      for (const type of ["input", "change"]) {
        el.addEventListener(type, event => events.push([event.type, el.value]));
      }
      return events;
    });
    assert.equal(await readingGoal.inputValue(), "3");
    await increaseGoal.click();
    assert.equal(await readingGoal.inputValue(), "3.5");
    assert.deepEqual(await goalEvents.jsonValue(), [["input", "3.5"], ["change", "3.5"]]);
    await goalEvents.dispose();
    await readingGoal.press("ArrowDown");
    assert.equal(await readingGoal.inputValue(), "3");
    await decreaseGoal.press("Space");
    assert.equal(await readingGoal.inputValue(), "2.5");
    await readingGoal.fill("19.75");
    assert(await readingGoal.evaluate(el => el.validity.stepMismatch));
    await increaseGoal.click();
    assert.equal(await readingGoal.inputValue(), "20");
    assert(await increaseGoal.isDisabled());

    const menuSource = menus.getByRole("region", { name: "Menu Python source", exact: true });
    const menuSourceSummary = menus.locator("details.example-source > summary");
    await menuSourceSummary.press("Enter");
    assert(await menuSource.isHidden());
    await menuSourceSummary.press("Enter");
    await page.keyboard.press("Tab");
    assert(await focused(menuSource));
    assert(await menuSource.evaluate(el => {
      const style = getComputedStyle(el);
      return el.scrollHeight > el.clientHeight && el.scrollWidth > el.clientWidth
        && style.outlineStyle === "solid" && style.outlineOffset === "-2px";
    }));
    const pageScroll = await page.evaluate(() => window.scrollY);
    await page.keyboard.press("ArrowDown");
    await page.waitForFunction(() => document.activeElement.scrollTop > 0);
    await page.keyboard.press("ArrowRight");
    await page.waitForFunction(() => document.activeElement.scrollLeft > 0);
    assert.equal(await page.evaluate(() => window.scrollY), pageScroll);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.keyboard.press("Shift+Tab");
    assert(await focused(menuSourceSummary));
    await page.keyboard.press("Space");
    assert(await menuSource.isHidden());
    assert(await buttons.locator("code").isVisible());

    const toasts = page.getByRole("region", { name: "Toast", exact: true });
    const addBook = toasts.getByRole("button", { name: "Add to reading list" });
    const removeBook = toasts.getByRole("button", { name: "Remove from reading list" });
    const toast = toasts.locator('[data-fleur-ui="toast"]');
    const announcement = toasts.getByRole("status");
    const dismiss = toast.getByRole("button", { name: "Dismiss" });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.clock.install({ time: new Date("2026-01-01T12:00:00Z") });
    await page.clock.pauseAt(new Date("2026-01-01T12:01:00Z"));
    assert(await toast.isHidden());
    assert.equal(await announcement.textContent(), "");

    async function addBookAndCheckToast() {
      await addBook.press("Enter");
      assert(await toast.isVisible());
      assert(await focused(removeBook));
      assert.equal(await announcement.textContent(), "Added The Secret Garden to your reading list.");
      assert.equal(await announcement.getAttribute("aria-atomic"), "true");
    }

    await addBookAndCheckToast();
    const toastBox = await toast.boundingBox();
    assert(toastBox.x >= 0 && toastBox.x + toastBox.width <= 360);
    assert(toastBox.y >= 0 && toastBox.y + toastBox.height <= 800);
    const dismissBox = await dismiss.boundingBox();
    assert.equal(dismissBox.width, dismissBox.height);
    assert(dismissBox.width >= 32 && dismissBox.width <= 40);
    assert.equal(await toast.evaluate(el => getComputedStyle(el).animationName), "none");
    await page.clock.runFor(2000);
    await toast.hover();
    await page.clock.runFor(5000);
    assert(await toast.isVisible());
    await page.mouse.move(1, 1);
    await page.clock.runFor(1700);
    assert(await toast.isVisible());
    await page.clock.runFor(400);
    assert(await toast.isHidden());
    assert(await focused(removeBook));
    assert.equal(await announcement.textContent(), "");

    await removeBook.press("Enter");
    await addBookAndCheckToast();
    await page.keyboard.press("Tab");
    assert(await focused(dismiss));
    await page.clock.runFor(5000);
    assert(await toast.isVisible());
    await page.keyboard.press("Shift+Tab");
    assert(await focused(removeBook));
    await page.clock.runFor(4100);
    assert(await toast.isHidden());

    await removeBook.press("Enter");
    await addBookAndCheckToast();
    await page.keyboard.press("Tab");
    await page.keyboard.press("Space");
    assert(await toast.isHidden());
    assert(await focused(removeBook));
    await page.clock.runFor(5000);
    assert(await toast.isHidden());
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
