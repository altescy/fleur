const assert = require("node:assert/strict");
const { chromium, webkit } = require("playwright-core");

async function run() {
  const [, , executable, url, engine] = process.argv;
  const browser = engine === "webkit" ? await webkit.launch() : await chromium.launch({ executablePath: executable });
  try {
    const page = await browser.newPage();
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.clock.install({ time: new Date("2026-01-01T12:00:00Z") });
    await page.clock.pauseAt(new Date("2026-01-01T12:01:00Z"));
    await page.goto(url);

    const show = page.getByRole("button", { name: "Show", exact: true });
    const unlimited = page.getByRole("button", { name: "No timeout" });
    const timed = page.getByRole("button", { name: "1.2 seconds" });
    const immediate = page.getByRole("button", { name: "Zero milliseconds" });
    const toast = page.locator("#toast");
    const dismiss = toast.getByRole("button", { name: "Dismiss" });
    const closed = page.locator("#closed");
    const reason = page.locator("#reason");

    await show.press("Enter");
    const originalToast = await toast.elementHandle();
    const originalDismiss = await dismiss.elementHandle();
    await page.clock.runFor(10000);
    assert(await toast.isVisible());
    assert.equal(
      await dismiss.evaluate(button => document.getElementById(button.getAttribute("aria-describedby"))?.textContent),
      "Saved",
    );

    await dismiss.focus();
    // Change the duration without moving focus out of the toast.
    await timed.evaluate(button => button.click());
    assert(await toast.evaluate((current, original) => current === original, originalToast));
    assert(await dismiss.evaluate(
      (current, original) => current === original && current === document.activeElement,
      originalDismiss,
    ));
    await page.clock.runFor(10000);
    assert(await toast.isVisible());
    await show.focus();
    await page.clock.runFor(1100);
    assert(await toast.isVisible());
    await page.clock.runFor(200);
    assert(await toast.isHidden());
    assert.equal(await closed.textContent(), "1");
    assert.equal(await reason.textContent(), "timeout");

    await show.press("Enter");
    await page.clock.runFor(500);
    await unlimited.press("Enter");
    await page.clock.runFor(2000);
    assert(await toast.isVisible());
    assert.equal(await closed.textContent(), "1");
    await immediate.press("Enter");
    await page.clock.runFor(10);
    assert(await toast.isHidden());
    assert.equal(await closed.textContent(), "2");
    assert.equal(await reason.textContent(), "timeout");

    await unlimited.press("Enter");
    await show.press("Enter");
    await dismiss.press("Space");
    assert(await toast.isHidden());
    assert.equal(await closed.textContent(), "3");
    assert.equal(await reason.textContent(), "dismiss");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
