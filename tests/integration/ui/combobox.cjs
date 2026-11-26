const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const search = page.getByRole("combobox", { name: "Book" });
    const results = page.getByRole("listbox", { name: "Book" });
    const persuasion = results.getByRole("option", { name: "Persuasion" });
    const active = () => search.getAttribute("aria-activedescendant");
    const changeModel = name => page.getByRole("button", { name }).evaluate(button => button.click());

    assert.equal(await search.inputValue(), "Emma");
    await search.press("ArrowUp");
    assert.equal(await active(), await persuasion.getAttribute("id"));
    await changeModel("Reorder");
    assert.equal(await search.inputValue(), "Emma (1815)");
    assert.equal(await active(), await persuasion.getAttribute("id"));
    assert(await search.evaluate(el => el === document.activeElement));
    await search.dispatchEvent("compositionstart");
    await page.keyboard.press("Enter");
    assert(await results.isVisible());
    assert.equal(await search.inputValue(), "Emma (1815)");
    await search.dispatchEvent("compositionend");
    await page.keyboard.press("Enter");
    assert(await results.isHidden());
    assert.equal(await search.inputValue(), "Persuasion");

    await search.fill("jane");
    await page.keyboard.press("ArrowDown");
    assert.equal(await active(), await results.getByRole("option", { name: "Jane Eyre" }).getAttribute("id"));
    await changeModel("Remove Jane Eyre");
    assert.equal(await active(), null);
    assert.equal(await results.getByRole("option").count(), 0);
    assert.equal(await search.inputValue(), "jane");
    await page.keyboard.press("Escape");
    assert.equal(await search.inputValue(), "Persuasion");
    await changeModel("Clear selection");
    assert.equal(await search.inputValue(), "");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
