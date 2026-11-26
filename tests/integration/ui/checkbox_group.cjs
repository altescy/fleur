const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const form = page.getByRole("form", { name: "Filters" });
    const group = form.getByRole("group", { name: "Shelves" });
    const selection = page.getByRole("status");
    const values = () => form.evaluate(el => new FormData(el).getAll("shelf"));
    assert.deepEqual(await values(), ["reading"]);
    await group.getByText("Finished", { exact: true }).click();
    assert.deepEqual(await values(), ["reading", "finished"]);
    assert.equal(await selection.textContent(), "reading,finished");
    await page.getByRole("button", { name: "Refresh" }).click();
    assert.deepEqual(await values(), ["finished", "reading"]);
    await group.getByRole("checkbox", { name: "To read" }).press("Space");
    assert.equal(await selection.textContent(), "reading,finished,to-read");
    assert.deepEqual(await values(), ["finished", "reading", "to-read"]);
    await page.getByRole("button", { name: "Disable" }).click();
    for (const checkbox of await group.getByRole("checkbox").all()) {
      assert(await checkbox.isDisabled());
      assert(await checkbox.isChecked());
    }
    assert.deepEqual(await values(), []);
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
