const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    let deliverPhoto;
    let failReplacement;
    const pendingPhoto = new Promise(resolve => { deliverPhoto = resolve; });
    const pendingReplacement = new Promise(resolve => { failReplacement = resolve; });
    await page.route("https://avatars.example.test/portrait.gif", async route => {
      await pendingPhoto;
      await route.fulfill({
        contentType: "image/gif",
        body: Buffer.from("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7", "base64"),
      });
    });
    await page.route("https://avatars.example.test/missing.gif", async route => {
      await pendingReplacement;
      await route.fulfill({ status: 404 });
    });
    await page.goto(process.argv[3], { waitUntil: "domcontentloaded" });

    const avatar = page.getByRole("img", { name: "Lead reviewer", exact: true });
    const photo = avatar.locator("img");
    const initials = avatar.getByText("LR", { exact: true });
    const caption = page.getByText("The Secret Garden");
    const layout = async () => [await avatar.boundingBox(), await caption.boundingBox()];
    const originalLayout = await layout();
    assert.equal(await page.getByRole("img").count(), 1);
    assert(await page.getByText("Second reviewer", { exact: true }).isVisible());
    assert(await initials.isVisible());
    assert(await photo.isHidden());
    assert.equal(await photo.evaluate(img => img.complete), false);

    deliverPhoto();
    await photo.waitFor();
    assert(await initials.isHidden());
    assert.equal(await photo.evaluate(img => img.naturalWidth), 1);
    assert.deepEqual(await layout(), originalLayout);
    assert.equal(await page.getByRole("img").count(), 1);

    await page.getByRole("button", { name: "Replace photo" }).click();
    assert(await initials.isVisible());
    assert(await photo.isHidden());
    assert.deepEqual(await layout(), originalLayout);
    failReplacement();
    await page.waitForFunction(() => document.querySelector("img[src$='missing.gif']").complete);
    assert(await initials.isVisible());
    assert(await photo.isHidden());
    assert.deepEqual(await layout(), originalLayout);
    assert.equal(await page.getByRole("img").count(), 1);

    await page.getByRole("button", { name: "Remove photo" }).click();
    assert.equal(await photo.getAttribute("src"), null);
    assert(await initials.isVisible());
    assert.deepEqual(await layout(), originalLayout);
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
