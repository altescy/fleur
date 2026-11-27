const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const form = page.getByRole("form", { name: "Add an expense" });
    for (const [name, amount, day, category] of [
      ["Train", "1200", "2026-11-23", "Travel"],
      ["Lunch", "700", "2026-11-22", "Meals"],
      ["Bus", "900", "2026-11-25", "Travel"],
    ]) {
      await form.getByLabel("Date").fill(day);
      await form.getByLabel("Description").fill(name);
      await form.getByLabel("Amount (JPY)").fill(amount);
      await form.getByLabel("Category", { exact: true }).selectOption(category);
      await form.getByRole("button", { name: "Add expense" }).click();
    }

    const table = page.getByRole("table", { name: "Expenses" });
    const amount = table.getByRole("columnheader", { name: "Amount", exact: true });
    const date = table.getByRole("columnheader", { name: "Date", exact: true });
    const descriptions = table.locator("tbody tr td:first-child");
    const filter = page.getByLabel("Filter by category");
    const filters = page.getByRole("button", { name: /^Filter: / });
    const subtotal = page.getByRole("status");
    assert.deepEqual(await descriptions.allTextContents(), ["Train", "Lunch", "Bus"]);
    assert.equal(await table.locator("[aria-sort]").count(), 0);
    await filters.click();
    await filter.selectOption("Travel");
    await page.keyboard.press("Escape");
    async function checkFilteredRows(expected) {
      assert.deepEqual(await descriptions.allTextContents(), expected);
      assert.equal(await filter.inputValue(), "Travel");
      assert.equal(await subtotal.textContent(), "Shown subtotal: ¥2,100");
      assert.equal(await table.locator("th[aria-sort]").count(), 1);
    }

    await amount.getByRole("button").press("Enter");
    await checkFilteredRows(["Bus", "Train"]);
    assert.equal(await amount.getAttribute("aria-sort"), "ascending");
    assert.equal(await amount.locator('[aria-hidden="true"]').textContent(), "↑");
    await date.getByRole("button").press("Space");
    await checkFilteredRows(["Train", "Bus"]);
    assert.equal(await amount.getAttribute("aria-sort"), null);
    assert.equal(await amount.locator('[aria-hidden="true"]').textContent(), "↕");
    assert.equal(await date.getAttribute("aria-sort"), "ascending");
    assert.equal(await date.locator('[aria-hidden="true"]').textContent(), "↑");
    await date.getByRole("button").click();
    await checkFilteredRows(["Bus", "Train"]);
    assert.equal(await date.getAttribute("aria-sort"), "descending");
    assert.equal(await date.locator('[aria-hidden="true"]').textContent(), "↓");
    await filters.click();
    await filter.selectOption("All categories");
    assert.deepEqual(await descriptions.allTextContents(), ["Bus", "Train", "Lunch"]);
    assert.equal(await subtotal.textContent(), "Shown subtotal: ¥2,800");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
