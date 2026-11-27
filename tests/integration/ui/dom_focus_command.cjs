const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const edit = page.getByRole("button", { name: "Edit", exact: true });
    const status = page.locator("#status");
    const waitForStatus = text => status.filter({ hasText: new RegExp(`^${text}$`) }).waitFor({ timeout: 3000 });
    const prevented = await edit.evaluate(el => {
      // A plain event has the same name but does not supply keyboard data.
      const malformed = new Event("keydown", { bubbles: true, cancelable: true });
      el.dispatchEvent(malformed);
      return malformed.defaultPrevented;
    });
    assert.equal(prevented, false);
    assert.equal(await status.textContent(), "idle");
    await edit.press("Space");
    assert.equal(await status.textContent(), "idle");

    await edit.press("Enter");
    await waitForStatus("focused");
    assert.equal(await page.locator("#key").textContent(), "Enter");
    assert(await page.locator("#editor").evaluate(el => document.activeElement === el));

    await page.getByRole("button", { name: "Missing" }).click();
    await waitForStatus("not_found");
    await page.getByRole("button", { name: "Unfocusable" }).click();
    await waitForStatus("not_focusable");

    const recovery = await page.evaluate(() => {
      const runtime = globalThis.__fleur;
      const mount = document.createElement("div");
      document.body.append(mount);
      let send;
      runtime.program({
        init: () => [0, dispatch => { send = dispatch; }],
        update(model, message) {
          if (message.type === "FAIL") throw new Error("update failed");
          return [model + 1, runtime.Cmd.none()];
        },
        view: model => runtime.h("output", {}, model),
      })(mount);
      let failure;
      try {
        send({ type: "FAIL" });
      } catch (error) {
        failure = error.message;
      }
      send({ type: "NEXT" });
      return { failure, rendered: mount.textContent };
    });
    assert.deepEqual(recovery, { failure: "update failed", rendered: "1" });
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
