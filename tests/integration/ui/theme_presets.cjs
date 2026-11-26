const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

// Let the browser serialize literal reference colors (OKLCH, HSL and hex) the same
// way it serializes computed styles, without looking up any Fleur variables.
async function referenceColors(page, palette) {
  return page.evaluate(p => {
    const probe = document.createElement("span");
    document.body.append(probe);
    const color = value => {
      if (!CSS.supports("color", value)) throw new Error("Invalid reference color: " + value);
      probe.style.color = value;
      return getComputedStyle(probe).color;
    };
    const ring = strength => {
      probe.style.boxShadow = '0 0 0 3px color-mix(in srgb, ' + p.ring + ' ' + strength + '%, transparent)';
      return getComputedStyle(probe).boxShadow;
    };
    const colors = {};
    for (const key of ["primary", "primary-foreground", "card", "foreground", "border", "muted", "muted-foreground", "ring"]) {
      colors[key] = color(p[key]);
    }
    colors.buttonHover = color('color-mix(in srgb, ' + p.primary + ' 88%, ' + p["primary-foreground"] + ')');
    colors.inputFocus = ring(35);
    colors.buttonFocus = ring(40);
    probe.remove();
    return colors;
  }, palette);
}

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    const palettes = JSON.parse(await page.locator("#expected").textContent());
    let selected = "One";
    for (const mode of ["light", "dark", "light"]) {
      const switchMode = page.getByRole("button", { name: mode === "light" ? "Light" : "Dark", exact: true });
      await switchMode.click();
      for (const region of ["outside", "parent", "child"]) {
        const regionMode = region === "outside" ? "light" : mode;
        const palette = { ...palettes[regionMode] };
        if (region === "child") Object.assign(palette, { primary: "#704092", card: "#efdead", ring: "#157768" });
        const colors = await referenceColors(page, palette);
        const root = page.locator("#" + region);
        const check = async (el, key, expected) => {
          const actual = await el.evaluate((node, k) => getComputedStyle(node)[k], key);
          assert.equal(actual, expected, mode + "/" + region + " " + el + " " + key);
        };
        const button = root.getByRole("button", { name: "Action" });
        const input = root.getByRole("textbox");
        const tab = name => root.getByRole("button", { name, exact: true });
        async function checkSelection(name) {
          const other = name === "One" ? "Two" : "One";
          assert.equal(await tab(name).getAttribute("aria-pressed"), "true");
          assert.equal(await tab(other).getAttribute("aria-pressed"), "false");
          assert(await root.getByText("Panel " + name).isVisible());
          assert(!(await root.getByText("Panel " + other).isVisible()));
          await check(tab(name), "backgroundColor", colors.card);
          await check(tab(name), "color", colors.foreground);
          await check(tab(name), "borderTopColor", colors.border);
          await check(tab(name), "fontWeight", "600");
          await check(tab(other), "backgroundColor", "rgba(0, 0, 0, 0)");
          await check(tab(other), "color", colors["muted-foreground"]);
          await check(tab(other), "borderTopColor", "rgba(0, 0, 0, 0)");
        }

        await switchMode.hover();
        await check(root, "colorScheme", regionMode);
        await check(button, "backgroundColor", colors.primary);
        await check(button, "color", colors["primary-foreground"]);
        await check(input, "backgroundColor", colors.card);
        await check(input, "color", colors.foreground);
        await check(input, "borderTopColor", colors.border);
        await check(root.locator('[data-fleur-tabs="list"]'), "backgroundColor", colors.muted);
        await checkSelection(selected);

        await button.hover();
        await check(button, "backgroundColor", colors.buttonHover);
        await button.click();
        await input.hover();
        await check(input, "borderTopColor", colors.ring);
        await page.keyboard.press("Tab");
        await check(input, "boxShadow", colors.inputFocus);
        await page.keyboard.press("Shift+Tab");
        await check(button, "boxShadow", colors.buttonFocus);
        await page.keyboard.press("Tab");
        await page.keyboard.press("Tab");
        await check(tab("One"), "boxShadow", colors.buttonFocus);
      }
      // Switch a real tab in the child and keep its state through the next mode change.
      selected = selected === "One" ? "Two" : "One";
      const child = page.locator("#child");
      await child.getByRole("button", { name: selected, exact: true }).click();
      assert(await child.getByText("Panel " + selected).isVisible());
    }
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
