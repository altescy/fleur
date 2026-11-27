const assert = require("node:assert/strict");
const { chromium, webkit } = require("playwright-core");

async function run() {
  const [, , executable, url, engine] = process.argv;
  const browser = engine === "webkit" ? await webkit.launch() : await chromium.launch({ executablePath: executable });
  try {
    const page = await browser.newPage();
    await page.goto(url);
    const search = page.getByRole("combobox", { name: "Book" });
    const results = page.getByRole("listbox", { name: "Book" });
    const persuasion = results.getByRole("option", { name: "Persuasion" });
    const jane = results.getByRole("option", { name: "Jane Eyre" });
    const jamaica = results.getByRole("option", { name: "Jamaica Inn" });
    const active = () => search.getAttribute("aria-activedescendant");
    // Simulate an external model update while leaving focus in the combobox.
    const changeModel = name => page.getByRole("button", { name }).evaluate(button => button.click());

    assert.equal(await search.inputValue(), "Emma");
    await search.press("ArrowUp");
    assert.equal(await active(), await persuasion.getAttribute("id"));
    await changeModel("Reorder");
    assert.equal(await search.inputValue(), "Emma (1815)");
    assert.equal(await active(), await persuasion.getAttribute("id"));
    assert(await search.evaluate(el => el === document.activeElement));
    await search.dispatchEvent("compositionstart");
    await page.keyboard.press("Enter");
    assert(await results.isVisible());
    assert.equal(await search.inputValue(), "Emma (1815)");
    await search.dispatchEvent("compositionend");
    await page.keyboard.press("Enter");
    assert(await results.isHidden());
    assert.equal(await search.inputValue(), "Persuasion");

    await search.fill("ja");
    await page.keyboard.press("ArrowDown");
    assert.equal(await active(), await jane.getAttribute("id"));
    const originalInput = await search.elementHandle();
    await search.evaluate(input => input.setSelectionRange(1, 2));
    async function checkEditing() {
      assert.deepEqual(await search.evaluate((input, original) => ({
        reused: input === original,
        focused: input === document.activeElement,
        text: input.value,
        selection: [input.selectionStart, input.selectionEnd],
      }), originalInput), { reused: true, focused: true, text: "ja", selection: [1, 2] });
      assert.equal(await search.getAttribute("aria-expanded"), "true");
    }

    await changeModel("Select Jane Eyre");
    await checkEditing();
    assert.equal(await jane.getAttribute("aria-selected"), "true");
    assert.equal(await active(), await jane.getAttribute("id"));

    await changeModel("Remove Jane Eyre");
    await checkEditing();
    assert.equal(await active(), null);
    assert.equal(await results.getByRole("option").count(), 0);
    assert(await page.getByRole("status").isVisible());
    await changeModel("Add Jamaica Inn");
    await checkEditing();
    assert.equal(await results.getByRole("option").count(), 1);
    await page.keyboard.press("ArrowDown");
    assert.equal(await active(), await jamaica.getAttribute("id"));
    await page.keyboard.press("Enter");
    assert(await results.isHidden());
    assert.equal(await search.inputValue(), "Jamaica Inn");
    assert.equal(await page.locator("#selection").textContent(), "jamaica");
    assert(await search.evaluate(el => el === document.activeElement));

    await search.fill("ja");
    await page.keyboard.press("Escape");
    assert.equal(await search.inputValue(), "Jamaica Inn");
    await search.fill("ja");
    await changeModel("Clear selection");
    assert.equal(await search.inputValue(), "ja");
    assert.equal(await jamaica.getAttribute("aria-selected"), "false");
    await page.keyboard.press("Escape");
    assert.equal(await search.inputValue(), "");
    assert(await search.evaluate(el => el === document.activeElement));
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
