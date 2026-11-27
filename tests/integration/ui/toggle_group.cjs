const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const tools = page.getByRole("toolbar", { name: "Tools" });
    const options = tools.getByRole("group", { name: "Options" });
    const a = options.getByRole("button", { name: "A", exact: true });
    const b = options.getByRole("button", { name: "B", exact: true });
    const refresh = tools.getByRole("button", { name: "Refresh" });
    const selection = page.getByRole("status");
    const focused = locator => locator.evaluate(el => el === document.activeElement);
    const press = key => page.keyboard.press(key);
    const stops = () => tools.locator('[tabindex="0"]').count();

    await page.getByRole("button", { name: "Before" }).press("Tab");
    assert(await focused(a));
    assert.equal(await a.getAttribute("aria-pressed"), "true");
    assert.equal(await stops(), 1);
    await press("ArrowRight");
    assert(await focused(b));
    assert.equal(await selection.textContent(), "a");
    await press("Space");
    assert.equal(await selection.textContent(), "a,b");
    await press("ArrowRight");
    assert(await focused(refresh));
    assert.equal(await stops(), 1);
    await press("Enter");
    assert(await focused(refresh));
    assert.equal(await stops(), 1);
    await press("ArrowLeft");
    assert(await focused(options.getByRole("button", { name: "C", exact: true })));
    await press("ArrowLeft");
    assert(await focused(a));
    await press("Enter");
    assert.equal(await selection.textContent(), "b");
    assert.equal(await b.getAttribute("aria-pressed"), "true");
    assert.equal(await stops(), 1);
    await press("Tab");
    assert(await focused(page.getByRole("button", { name: "After" })));
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
