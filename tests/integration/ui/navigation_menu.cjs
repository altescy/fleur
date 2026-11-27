const assert = require("node:assert/strict");
const { chromium, webkit } = require("playwright-core");

async function run() {
  const [, , executable, url, engine] = process.argv;
  const browser = engine === "webkit" ? await webkit.launch() : await chromium.launch({ executablePath: executable });
  try {
    const page = await browser.newPage();
    await page.goto(url);
    const books = page.getByRole("button", { name: "Books" });
    const emma = page.getByRole("link", { name: "Emma" });
    const expanded = () => books.getAttribute("aria-expanded");

    // WebKit does not focus a clicked button, so focus leaves the group without a related target.
    await books.click();
    await emma.focus();
    await books.click();
    assert.equal(await expanded(), "false");
    assert(await emma.isHidden());

    await books.click();
    await emma.focus();
    await page.getByRole("button", { name: "Outside" }).click();
    assert.equal(await expanded(), "false");

    await books.click();
    await emma.focus();
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    assert.equal(await expanded(), "false");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
