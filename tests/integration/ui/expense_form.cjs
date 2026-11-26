const assert = require("node:assert/strict");
const { readFile } = require("node:fs/promises");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const navigations = [];
    page.on("framenavigated", frame => {
      if (frame === page.mainFrame()) navigations.push(frame.url());
    });
    const submissions = await page.evaluateHandle(() => {
      const prevented = [];
      document.addEventListener("submit", event => prevented.push(event.defaultPrevented));
      return prevented;
    });

    const form = page.getByRole("form", { name: "Add an expense" });
    const description = form.getByLabel("Description");
    const amount = form.getByLabel("Amount (JPY)");
    const decreaseAmount = form.getByRole("button", { name: "Decrease amount" });
    const increaseAmount = form.getByRole("button", { name: "Increase amount" });
    const add = form.getByRole("button", { name: "Add expense" });
    const table = page.getByRole("table", { name: "Expenses" });
    const rows = table.locator("tbody tr");
    const filter = page.getByRole("combobox", { name: "Filter by category" });
    const filters = page.getByRole("button", { name: /^Filter: / });
    const firstExpense = page.getByRole("heading", { name: "No expenses yet" });
    const noMatches = page.getByRole("heading", { name: "No expenses in this category" });
    const showAll = page.getByRole("button", { name: "Show all categories" });
    const csv = page.getByRole("link", { name: "Download all expenses" });
    assert.equal(await csv.getAttribute("href"), null);
    assert.equal(await csv.getAttribute("aria-disabled"), "true");
    assert(await firstExpense.isVisible());
    assert(await page.getByText("Add your first expense using the form.", { exact: true }).isVisible());
    assert(await table.isHidden());
    await filters.click();
    await filter.selectOption("Meals");
    assert(await firstExpense.isVisible());
    assert(await noMatches.isHidden());
    assert(await showAll.isHidden());
    await filter.selectOption("All categories");
    await page.keyboard.press("Escape");

    await form.getByLabel("Date").fill("2026-11-26");
    await description.fill("Train fare");
    for (const [invalid, reason] of [
      ["", "valueMissing"],
      ["0", "rangeUnderflow"],
      ["1.5", "stepMismatch"],
      ["1000000000", "rangeOverflow"],
    ]) {
      await amount.fill(invalid);
      assert(await amount.evaluate((el, key) => el.validity[key], reason));
      assert(await add.isDisabled());
      await amount.press("Enter");
      assert.equal(await rows.count(), 0);
    }
    await amount.fill("1");
    assert(await decreaseAmount.isDisabled());
    await amount.press("ArrowDown");
    assert.equal(await amount.inputValue(), "1");
    await amount.fill("999999999");
    assert(await increaseAmount.isDisabled());
    await amount.press("ArrowUp");
    assert.equal(await amount.inputValue(), "999999999");

    await amount.fill("419");
    await increaseAmount.click();
    assert.equal(await amount.inputValue(), "420");
    await decreaseAmount.press("Space");
    assert.equal(await amount.inputValue(), "419");
    await amount.press("ArrowUp");
    assert.equal(await amount.inputValue(), "420");
    assert(await add.isEnabled());
    assert.deepEqual(await submissions.jsonValue(), []);

    await amount.press("Enter");
    assert(await firstExpense.isHidden());
    assert.equal(await rows.count(), 1);
    assert.deepEqual(await rows.first().locator("td").allTextContents(), ["Train fare", "¥420", "2026-11-26", "Travel", "Remove"]);
    assert.equal(await description.inputValue(), "");
    assert.equal(await amount.inputValue(), "");
    assert.deepEqual(await submissions.jsonValue(), [true]);

    await description.fill("Lunch");
    await amount.fill("700");
    await add.click();
    assert.equal(await rows.count(), 2);
    assert.equal(await page.getByRole("status").textContent(), "Shown subtotal: ¥1,120");
    assert.deepEqual(await submissions.jsonValue(), [true, true]);
    const allRows = await rows.allTextContents();
    await filters.click();
    await filter.selectOption("Supplies");
    await page.keyboard.press("Escape");
    assert(await table.isHidden());
    assert(await noMatches.isVisible());
    assert(await firstExpense.isHidden());
    await showAll.press("Enter");
    assert.equal(await filters.textContent(), "Filter: All categories");
    assert.deepEqual(await rows.allTextContents(), allRows);
    assert.equal(await page.getByRole("status").textContent(), "Shown subtotal: ¥1,120");
    assert(await showAll.isHidden());
    assert(await noMatches.isHidden());
    const [file] = await Promise.all([page.waitForEvent("download"), csv.click()]);
    assert.equal(file.suggestedFilename(), "expenses.csv");
    assert.equal(await readFile(await file.path(), "utf8"),
      '\uFEFFDate,Description,Category,Amount (JPY)\r\n"2026-11-26","Train fare","Travel",420\r\n"2026-11-26","Lunch","Travel",700\r\n');
    await rows.first().getByRole("button").click();
    await rows.first().getByRole("button").click();
    assert(await firstExpense.isVisible());
    assert(await showAll.isHidden());
    assert.equal(await csv.getAttribute("href"), null);
    assert.equal(await csv.getAttribute("aria-disabled"), "true");
    assert.deepEqual(navigations, []);
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
