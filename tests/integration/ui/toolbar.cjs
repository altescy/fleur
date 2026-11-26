const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const horizontal = page.getByRole("toolbar", { name: "Horizontal" });
    const start = horizontal.getByRole("button", { name: "Start" });
    const help = horizontal.getByRole("link", { name: "Help" });
    const more = horizontal.getByRole("button", { name: "More" });
    const menu = horizontal.getByRole("menu", { name: "More" });
    const insert = page.getByRole("button", { name: "Insert a control" });
    const focused = locator => locator.evaluate(el => el === document.activeElement);
    const press = key => page.keyboard.press(key);

    await page.getByRole("button", { name: "Before" }).press("Tab");
    assert(await focused(start));
    await press("ArrowLeft");
    assert(await focused(help));
    await press("ArrowLeft");
    assert(await focused(more));
    await press("Enter");
    await menu.waitFor();
    assert(await focused(menu.getByRole("menuitem", { name: "Apply", exact: true })));
    await press("ArrowDown");
    assert(await focused(menu.getByRole("menuitem", { name: "Apply again" })));
    await press("Escape");
    await menu.waitFor({ state: "hidden" });
    assert(await focused(more));
    await press("Tab");
    assert(await focused(insert));
    await press("Enter");
    await press("Shift+Tab");
    assert(await focused(more));
    await press("Home");
    assert(await focused(start));
    await press("ArrowLeft");
    const inserted = horizontal.getByRole("button", { name: "Inserted" });
    assert(await focused(inserted));
    assert.equal(await horizontal.locator('[tabindex="0"]').count(), 1);

    const vertical = page.getByRole("toolbar", { name: "Vertical" });
    const top = vertical.getByRole("button", { name: "Top" });
    const bottom = vertical.getByRole("button", { name: "Bottom" });
    await insert.press("Tab");
    assert(await focused(top));
    await press("ArrowDown");
    assert(await focused(bottom));
    await press("ArrowDown");
    assert(await focused(top));
    await press("End");
    assert(await focused(bottom));
    await press("Tab");
    assert(await focused(page.getByRole("button", { name: "After" })));
    assert.equal(await vertical.locator('[tabindex="0"]').count(), 1);
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
