const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const theme = page.getByRole("radiogroup", { name: "Theme", exact: true });
    const mode = page.getByRole("radiogroup", { name: "Color mode" });
    const scope = page.locator("[data-fleur-theme]");
    const font = () => scope.evaluate(el => getComputedStyle(el).fontFamily);
    const basicFont = await font();
    const input = page.getByRole("textbox", { name: "Your name" });
    await input.fill("Hayashi");
    await page.keyboard.press("Shift+Tab");
    await page.keyboard.press("Shift+Tab");
    assert(await theme.getByRole("radio", { name: "Basic" }).evaluate(el => el === document.activeElement));
    await page.keyboard.press("ArrowRight");
    assert(await theme.getByRole("radio", { name: "Zen" }).isChecked());
    assert.notEqual(await font(), basicFont);
    assert(await mode.getByRole("radio", { name: "Light" }).isChecked());
    assert.equal(await scope.getAttribute("data-fleur-mode"), "light");
    assert.equal(await input.inputValue(), "Hayashi");
    await page.keyboard.press("Tab");
    await page.keyboard.press("ArrowRight");
    assert(await mode.getByRole("radio", { name: "Dark" }).isChecked());
    assert.equal(await scope.getAttribute("data-fleur-mode"), "dark");
    assert(await theme.getByRole("radio", { name: "Zen" }).isChecked());
    assert.equal(await input.inputValue(), "Hayashi");
    assert(await page.getByText("Hello, Hayashi", { exact: true }).isVisible());
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
