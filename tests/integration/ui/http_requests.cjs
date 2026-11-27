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
    let sent;
    await page.route("http://fleur.test/todos/**", async route => {
      const request = route.request();
      sent = {
        method: request.method(),
        url: request.url(),
        authorization: request.headers()["authorization"],
        contentType: request.headers()["content-type"],
        body: request.postDataJSON(),
      };
      await route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    });
    await page.goto("http://fleur.test/");
    await page.getByRole("textbox", { name: "Title" }).fill("Read & write/ok?");
    await page.getByRole("button", { name: "Save" }).click();
    await page.locator("#result").filter({ hasText: "saved" }).waitFor();

    assert.deepEqual(sent, {
      method: "PUT",
      url: "http://fleur.test/todos/42?notify=true&source=Read+%26+write%2Fok%3F",
      authorization: "Bearer secret",
      contentType: "application/json",
      body: { title: "Read & write/ok?", tags: ["work", "Read & write/ok?"], done: false },
    });
    assert.equal(await page.locator("#result").textContent(), "saved 200");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
