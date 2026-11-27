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
    // The shape of FastAPI's validation error.
    await page.route("http://fleur.test/todos", route => route.fulfill({
      status: 422,
      contentType: "application/json",
      body: JSON.stringify({ detail: [{ type: "string_too_short", loc: ["body", "title"], msg: "String should have at least 1 character" }] }),
    }));
    await page.route("http://fleur.test/missing", route => route.fulfill({ status: 404, contentType: "text/html", body: "<h1>Not Found</h1>" }));
    await page.route("http://fleur.test/untyped", route => route.fulfill({ status: 400, contentType: "application/json", body: '{"detail":"Bad"}' }));
    await page.goto("http://fleur.test/");
    const status = page.locator("#status");

    await page.getByRole("button", { name: "Save", exact: true }).click();
    await status.filter({ hasText: "invalid" }).waitFor();
    assert.deepEqual(await page.locator("#issues > *").allTextContents(), ["String should have at least 1 character"]);

    // An error page of another shape has no typed body.
    await page.getByRole("button", { name: "Save missing" }).click();
    await status.filter({ hasText: "no body" }).waitFor();
    assert.equal(await page.locator("#issues > *").count(), 0);

    // Without an error type, the body is the decoded JSON.
    await page.getByRole("button", { name: "Save untyped" }).click();
    await page.locator("#raw").filter({ hasText: "json" }).waitFor();
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
