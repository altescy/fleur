const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const left = page.getByRole("group", { name: "Left" });
    const right = page.getByRole("group", { name: "Right" });
    const openItems = group => group.locator("details[open] > summary").allTextContents();
    assert.deepEqual(await openItems(left), ["First"]);
    assert.deepEqual(await openItems(right), ["First"]);
    const second = left.locator("summary", { hasText: "Second" });
    await second.click();
    assert.deepEqual(await openItems(left), ["Second"]);
    assert.deepEqual(await openItems(right), ["First"]);

    await page.getByRole("button", { name: "Add a section" }).click();
    assert.deepEqual(await openItems(left), ["Second"]);
    const third = left.locator("summary", { hasText: "Third" });
    await second.press("ArrowDown");
    assert(await third.evaluate(el => el === document.activeElement));
    await page.keyboard.press("Enter");
    assert.deepEqual(await openItems(left), ["Third"]);
    assert.deepEqual(await openItems(right), ["First"]);
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
