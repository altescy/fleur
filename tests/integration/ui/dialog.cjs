const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const dialog = page.getByRole("dialog", { name: "Profile" });
    const name = dialog.getByRole("textbox", { name: "Name" });
    const edit = page.getByRole("button", { name: "Edit profile" });
    const again = page.getByRole("button", { name: "Edit again" });
    const focused = locator => locator.evaluate(el => el === document.activeElement);

    async function checkOpen() {
      await dialog.waitFor({ state: "visible" });
      assert(await dialog.evaluate(el => el instanceof HTMLDialogElement && el.matches(":modal")));
      assert(await focused(name));
      assert.equal(await page.locator("#model-state").textContent(), "Open");
    }
    async function checkClosed() {
      await page.locator("#model-state", { hasText: "Closed" }).waitFor();
      await dialog.waitFor({ state: "hidden" });
      assert.equal(await page.locator("dialog").evaluate(el => el.open), false);
    }

    // Initial model state opens the modal after its children are mounted.
    await checkOpen();
    await dialog.getByRole("button", { name: "Done" }).click();
    await checkClosed();

    for (const trigger of [edit, again]) {
      await trigger.click();
      await checkOpen();
      await page.keyboard.press("Tab");
      assert(await focused(dialog.getByRole("button", { name: "Cancel" })));
      await page.keyboard.press("Escape");
      await checkClosed();
      assert(await focused(trigger));
    }

    await edit.click();
    await dialog.getByRole("button", { name: "Cancel" }).click();
    await checkClosed();
    assert(await focused(edit));

    // Reopen before the browser delivers the previous close event.
    await edit.press("Enter");
    await checkOpen();
    await page.evaluate(async () => {
      const modal = document.querySelector("dialog");
      const closed = new Promise(resolve => modal.addEventListener("close", resolve, { once: true }));
      modal.querySelector("button").click();
      await Promise.resolve();
      document.activeElement.click();
      await closed;
    });
    await checkOpen();
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
