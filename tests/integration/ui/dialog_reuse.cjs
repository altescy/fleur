const assert = require("node:assert/strict");
const { chromium, webkit } = require("playwright-core");

async function run() {
  const [, , executable, url, engine] = process.argv;
  const browser = engine === "webkit" ? await webkit.launch() : await chromium.launch({ executablePath: executable });
  try {
    const page = await browser.newPage();
    await page.goto(url);
    const panel = page.locator("#panel");
    await panel.and(page.locator("dialog:modal")).waitFor();
    const original = await panel.elementHandle();
    const expectedOpen = await page.locator("[data-expected-open]").getAttribute("data-expected-open") === "true";

    await page.getByRole("button", { name: "Swap" }).click();
    const replacement = await panel.evaluate((element, previous) => ({
      sameElement: element === previous,
      text: element.textContent,
      open: element.open,
      modal: element.matches(":modal"),
    }), original);
    assert.deepEqual(replacement, { sameElement: true, text: "Replacement", open: expectedOpen, modal: false });

    const outside = page.getByRole("button", { name: "Outside" });
    await outside.focus();
    assert(await outside.evaluate(element => element === document.activeElement));
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
