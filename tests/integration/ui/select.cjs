const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const select = page.getByRole("combobox", { name: "Choice", exact: true });
    const uncontrolled = page.getByRole("combobox", { name: "Uncontrolled" });
    const selectedIndex = () => select.evaluate(el => el.selectedIndex);
    const model = page.locator("#model-value");
    const error = page.locator('[data-fleur-part="error"]');

    assert.equal(await page.getByRole("heading", { name: "Preferences", level: 2 }).count(), 1);
    const card = page.locator('[data-fleur-ui="card"]');
    assert.equal(await card.evaluate(el => getComputedStyle(el).backgroundColor), "rgb(237, 240, 255)");
    assert.equal(await select.evaluate(el => getComputedStyle(el).borderTopLeftRadius), "9px");
    assert.equal(await select.inputValue(), "b");
    assert.equal(await selectedIndex(), 1);
    assert.equal(await select.getAttribute("aria-describedby"), "choice-description");
    assert.equal(await error.isVisible(), false);

    const appearance = () => select.evaluate(el => {
      const style = getComputedStyle(el);
      return {
        appearance: style.appearance,
        image: style.backgroundImage,
        position: style.backgroundPositionX.split(", "),
        start: style.paddingInlineStart,
        end: style.paddingInlineEnd,
      };
    });
    const ltr = await appearance();
    assert.equal(ltr.appearance, "none");
    assert.match(ltr.image, /linear-gradient/);
    assert.equal(ltr.position[1], `calc(100% - ${ltr.start})`);
    assert(parseFloat(ltr.end) > parseFloat(ltr.start) + 10);
    await select.evaluate(el => el.dir = "rtl");
    const rtl = await appearance();
    assert.equal(rtl.position[0], rtl.start);
    assert.equal(rtl.end, ltr.end);
    await select.evaluate(el => el.removeAttribute("dir"));
    await page.emulateMedia({ forcedColors: "active" });
    assert.equal((await appearance()).appearance, "auto");
    assert.equal((await appearance()).image, "none");
    await page.emulateMedia({ forcedColors: "none" });

    await page.getByRole("button", { name: "Remove" }).click();
    assert.equal(await model.textContent(), "b");
    assert.equal(await selectedIndex(), -1);
    assert.equal(await select.getAttribute("aria-invalid"), "true");
    assert.equal(await select.getAttribute("aria-describedby"), "choice-description choice-error");
    assert.equal(await error.isVisible(), true);
    await uncontrolled.selectOption("c");

    await page.getByRole("button", { name: "Restore" }).click();
    assert.equal(await select.inputValue(), "b");
    assert.equal(await selectedIndex(), 2);
    assert.equal(await uncontrolled.inputValue(), "c");
    assert.equal(await select.getAttribute("aria-invalid"), null);
    assert.equal(await select.getAttribute("aria-describedby"), "choice-description");
    assert.equal(await error.isVisible(), false);

    await select.selectOption({ label: "Label a" });
    assert.equal(await model.textContent(), "a");
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
