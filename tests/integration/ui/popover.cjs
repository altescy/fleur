const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage({ viewport: { width: 360, height: 600 } });
    await page.goto(process.argv[3]);
    const edit = page.getByRole("button", { name: "Edit", exact: true });
    const editor = page.getByRole("dialog", { name: "Edit", exact: true });
    const title = page.getByRole("textbox", { name: "Title" });
    const outside = page.getByRole("textbox", { name: "Outside" });
    const status = page.getByRole("status");
    const focused = locator => locator.evaluate(el => el === document.activeElement);
    await editor.waitFor();
    assert(await focused(title));
    const anchor = await edit.boundingBox();
    const panel = await editor.boundingBox();
    assert(panel.y >= anchor.y + anchor.height && panel.y < anchor.y + anchor.height + 16);
    assert(Math.abs(panel.x + panel.width - anchor.x - anchor.width) <= 1);
    assert(panel.x >= 0 && panel.x + panel.width <= 360);
    await outside.click();
    await status.filter({ hasText: /^Closed$/ }).waitFor();
    assert(await editor.isHidden());
    assert(await focused(outside));
    await page.getByRole("button", { name: "Open from model" }).click();
    await editor.waitFor();
    assert(await focused(title));

    await page.getByRole("button", { name: "Help" }).press("Space");
    const help = page.getByRole("dialog", { name: "Help" });
    await help.waitFor();
    await status.filter({ hasText: /^Closed$/ }).waitFor();
    assert(await editor.isHidden());
    await edit.press("Enter");
    await status.filter({ hasText: /^Editing$/ }).waitFor();
    assert(await help.isHidden());
    assert(await focused(title));
    await page.keyboard.press("Escape");
    await status.filter({ hasText: /^Closed$/ }).waitFor();
    assert(await focused(edit));
    await edit.press("Space");
    await status.filter({ hasText: /^Editing$/ }).waitFor();
    await edit.click();
    await status.filter({ hasText: /^Closed$/ }).waitFor();
    assert(await editor.isHidden());
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
