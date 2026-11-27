const assert = require("node:assert/strict");
const { fileURLToPath } = require("node:url");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.route("http://fleur.test/", route => route.fulfill({
      path: fileURLToPath(process.argv[3]), contentType: "text/html",
    }));
    await page.goto("http://fleur.test/");
    const message = page.getByRole("status");
    const bar = page.getByRole("progressbar", { name: "Checking service status" });
    const url = "http://fleur.test/status.txt";
    async function fetchStatus(button, status, body) {
      let release;
      const gate = new Promise(resolve => { release = resolve; });
      await page.route(url, async route => {
        await gate;
        await route.fulfill({ status, contentType: "text/plain", body });
      }, { times: 1 });
      await Promise.all([page.waitForRequest(url), button.click()]);
      try {
        assert(await bar.isVisible());
        assert(await bar.evaluate(el => el instanceof HTMLProgressElement && el.position === -1 && !el.hasAttribute("value")));
        assert(await message.isHidden());
        assert(await page.getByRole("button", { name: "Checking…" }).isDisabled());
      } finally {
        release();
      }
      await message.waitFor();
      assert(await bar.isHidden());
    }

    assert(await bar.isHidden());
    await fetchStatus(page.getByRole("button", { name: "Refresh" }), 503, "Unavailable");
    const retry = page.getByRole("button", { name: "Retry" });
    await retry.waitFor();
    assert.equal(await message.textContent(), "Could not load the service status.");
    await fetchStatus(retry, 200, "Service online");
    assert.equal(await message.textContent(), "Service online");
    assert(await page.getByRole("button", { name: "Refresh" }).isEnabled());
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
