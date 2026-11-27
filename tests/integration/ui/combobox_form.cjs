const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const search = page.getByRole("combobox", { name: "Book" });
    const results = page.getByRole("listbox", { name: "Book" });
    const submitted = () => page.locator("#submitted").textContent();

    // An open popup without an active option keeps the native implicit submission.
    await search.fill("e");
    assert(await results.isVisible());
    await page.keyboard.press("Enter");
    assert.equal(await submitted(), "1");

    // With an active option, Enter selects it instead of submitting.
    await search.fill("e");
    await page.keyboard.press("ArrowDown");
    await page.keyboard.press("Enter");
    assert.equal(await search.inputValue(), "Emma");
    assert.equal(await submitted(), "1");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
