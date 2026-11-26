const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const slider = page.getByRole("slider", { name: "Level" });
    const click = name => page.getByRole("button", { name, exact: true }).click();
    assert.equal(await slider.inputValue(), "132");
    await click("Limit");
    assert.equal(await slider.inputValue(), "136");
    await click("Restore");
    assert.equal(await slider.inputValue(), "132");
    await click("Shift");
    assert.equal(await slider.inputValue(), "228");
    await click("Coarse");
    assert.equal(await slider.inputValue(), "230");
    await click("Fine");
    assert.equal(await slider.inputValue(), "228");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
