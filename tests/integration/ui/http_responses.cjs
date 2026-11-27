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
    const json = (status, body) => route => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
    // `note` is omitted from the second item, as Pydantic does with exclude_none.
    await page.route("http://fleur.test/todos", json(200, [{ id: 1, title: "Read", note: "chapter 2" }, { id: 2, title: "Write" }]));
    await page.route("http://fleur.test/broken", json(200, [{ id: 1, title: 42, note: null }]));
    await page.route("http://fleur.test/missing", json(404, { detail: "Not Found" }));
    await page.goto("http://fleur.test/");
    const todos = page.locator("#todos");
    const error = page.locator("#error");

    await page.getByRole("button", { name: "Load", exact: true }).click();
    await todos.getByText("Write /").waitFor();
    assert.deepEqual(await todos.locator("> *").allTextContents(), ["Read / chapter 2", "Write / "]);

    await page.getByRole("button", { name: "Load broken" }).click();
    await error.filter({ hasText: "decode" }).waitFor();
    assert.equal(await error.textContent(), "decode: body[0].title: expected string, got integer");
    assert.equal(await todos.locator("> *").count(), 2);

    await page.getByRole("button", { name: "Load missing" }).click();
    await error.filter({ hasText: "status" }).waitFor();
    assert.equal(await error.textContent(), "status: HTTP 404 Not Found");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
