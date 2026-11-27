const assert = require("node:assert/strict");
const { chromium, webkit } = require("playwright-core");

async function run() {
  const engine = process.argv[4];
  const browser = engine === "webkit"
    ? await webkit.launch()
    : await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const button = name => page.getByRole("button", { name, exact: true });
    const outside = page.getByRole("textbox", { name: "Outside" });
    const paths = [
      ["Open dialog", "Profile", "Name", "#dialog-state"],
      ["Open dialog again", "Profile", "Name", "#dialog-state"],
      ["Edit", "Edit", "Title", "#popover-state"],
      ["Open editor from model", "Edit", "Title", "#popover-state"],
    ];

    for (const [openerName, panelName, fieldName, state] of paths) {
      const opener = button(openerName);
      const panel = page.getByRole("dialog", { name: panelName, exact: true });
      const field = panel.getByRole("textbox", { name: fieldName, exact: true });
      for (const activation of ["click", "Enter", "Space"]) {
        await outside.focus();
        if (activation === "click") {
          await opener.click();
        } else {
          await opener.focus();
          await page.keyboard.press(activation);
        }
        await page.locator(state).filter({ hasText: /^Open$/ }).waitFor({ timeout: 4000 });
        assert(await field.evaluate(el => document.activeElement === el), `${openerName} (${activation}) focuses the field`);
        await page.keyboard.press("Escape");
        await panel.waitFor({ state: "hidden", timeout: 4000 });
        await page.locator(state).filter({ hasText: /^Closed$/ }).waitFor({ timeout: 4000 });
        assert(await opener.evaluate(el => document.activeElement === el), `${openerName} (${activation}) regains focus`);
      }
    }
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
