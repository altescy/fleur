const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const prevented = await page.evaluate(() =>
      Array.from(document.forms, form => {
        const event = new SubmitEvent("submit", { bubbles: true, cancelable: true });
        form.dispatchEvent(event);
        return event.defaultPrevented;
      })
    );
    assert.deepEqual(prevented, [false, true]);

    const result = page.locator("output");
    await page.locator("dialog").evaluate(dialog => dialog.close());
    await result.filter({ hasText: /^Book$/ }).waitFor({ timeout: 3000 });

    await page.getByRole("button", { name: "Book / Essay", exact: true }).click();
    assert.equal(await result.textContent(), "Book / Essay");
    await page.getByRole("button", { name: "Dismiss", exact: true }).click();
    assert.equal(await result.textContent(), "Book");

    const disposed = await page.evaluate(async () => {
      const probe = document.querySelector("#probe");
      document.dispatchEvent(new Event("probe"));
      document.dispatchEvent(new Event("probe"));
      document.querySelector("#remove-probe").click();
      document.dispatchEvent(new Event("probe"));
      await new Promise(resolve => setTimeout(resolve, 0));
      return [probe.isConnected, probe.dataset.count, probe.hasAttribute("data-fired")];
    });
    assert.deepEqual(disposed, [false, "2", false]);
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
