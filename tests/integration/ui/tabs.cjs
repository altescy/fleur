const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1000 } });
    await page.goto(process.argv[3]);
    const css = (el, key) => el.evaluate((node, k) => getComputedStyle(node)[k], key);
    const clearHover = () => page.mouse.move(1099, 999);

    const list = page.getByRole("tablist", { name: "Page sections" });
    const one = list.getByRole("tab", { name: "One" });
    const two = list.getByRole("tab", { name: "Two" });
    const panel = page.locator("#page").getByRole("tabpanel", { name: "Two" });
    const focused = locator => locator.evaluate(el => document.activeElement === el);
    const tabIds = await page.getByRole("tab").evaluateAll(tabs => tabs.map(tab => {
      const panel = document.getElementById(tab.getAttribute("aria-controls"));
      if (!tab.id || panel?.getAttribute("aria-labelledby") !== tab.id) throw Error("Broken tab/panel association");
      return tab.id;
    }));
    assert.equal(new Set(tabIds).size, tabIds.length);
    await page.keyboard.press("Tab");
    assert(await focused(one));
    for (const [key, target] of [["ArrowLeft", two], ["ArrowRight", one], ["End", two], ["Home", one], ["ArrowRight", two]]) {
      await page.keyboard.press(key);
      assert(await focused(target));
      assert.equal(await one.getAttribute("aria-selected"), "true");
    }
    await page.keyboard.press("Space");
    assert.equal(await two.getAttribute("aria-selected"), "true");
    assert(await panel.isVisible());
    await page.keyboard.press("ArrowLeft");
    assert(await focused(one));
    await page.keyboard.press("Tab");
    assert(await focused(panel));
    await page.keyboard.press("Shift+Tab");
    assert(await focused(two));

    async function selection(root, active) {
      for (const name of ["One", "Two"]) {
        const button = root.getByRole("tab", { name, exact: true });
        assert.equal(await button.getAttribute("aria-selected"), String(name === active));
        assert.equal(await root.getByText("Panel " + name, { exact: true }).isVisible(), name === active);
        assert.equal(await css(button, "textDecorationLine"), "none");
        assert.equal(await css(button, "fontWeight"), name === active ? "600" : "500");
      }
    }

    for (const mode of ["light", "dark", "light"]) {
      await page.locator("#" + mode).click();
      const dark = mode === "dark";
      const card = dark ? "rgb(37, 53, 69)" : "rgb(224, 239, 255)";
      const strip = dark ? "rgb(21, 37, 53)" : "rgb(221, 238, 255)";
      for (const name of ["scoped", "tinted", "classed", "styled"]) {
        const root = page.locator("#" + name);
        const first = root.getByRole("tab", { name: "One", exact: true });
        const second = root.getByRole("tab", { name: "Two", exact: true });
        const fixedBackground = name === "classed" || name === "styled";
        const paint = name === "classed" ? "rgb(49, 105, 49)" : dark ? "rgb(102, 51, 34)" : "rgb(136, 68, 51)";
        const selectedBg = fixedBackground ? paint : name === "tinted" ? "rgb(170, 51, 68)" : card;
        const idleBg = fixedBackground ? paint : "rgba(0, 0, 0, 0)";
        const ring = "rgb(17, 119, 85) 0px 0px 0px 3px";

        await first.click();
        await clearHover();
        await selection(root, "One");
        assert.equal(await css(root.locator('[data-fleur-tabs="list"]'), "backgroundColor"), strip);
        assert.equal(await css(first, "backgroundColor"), selectedBg);
        assert.equal(await css(second, "backgroundColor"), idleBg);
        assert.equal(await css(first, "color"), dark ? "rgb(240, 244, 248)" : "rgb(17, 34, 51)");
        assert.equal(await css(second, "color"), "rgb(85, 119, 136)");
        assert.equal(await css(first, "borderTopColor"), "rgb(126, 141, 168)");
        assert.equal(await css(second, "borderTopColor"), "rgba(0, 0, 0, 0)");
        if (fixedBackground) assert.equal(await css(second, "padding"), name === "styled" ? "5px" : "7px");
        if (name === "styled") {
          assert.equal(await css(root, "padding"), "11px");
          assert.equal(await second.evaluate(el => el.classList.contains("night")), dark);
        }

        await first.hover();
        const selectedHover = await css(first, "backgroundColor");
        if (fixedBackground) assert.equal(selectedHover, paint);
        else assert.notEqual(selectedHover, selectedBg);
        await second.hover();
        const idleHover = await css(second, "backgroundColor");
        if (fixedBackground) {
          assert.equal(idleHover, paint);
          assert.equal(await css(second, "color"), "rgb(254, 239, 170)");
        } else {
          assert.notEqual(idleHover, idleBg);
          assert.notEqual(idleHover, selectedHover);
        }

        await page.keyboard.press("ArrowRight");
        assert(await second.evaluate(el => el.matches(":hover:focus-visible")));
        await selection(root, "One");
        assert.equal(await css(second, "boxShadow"), ring);
        assert.equal(await css(second, "backgroundColor"), idleHover);
        if (fixedBackground) assert.equal(await css(second, "outlineStyle"), "dashed");
        await clearHover();
        assert.equal(await css(second, "backgroundColor"), idleBg);
        assert.equal(await css(second, "boxShadow"), ring);
        await second.hover();
        await page.keyboard.press("Enter");
        await selection(root, "Two");
        assert(await second.evaluate(el => el.matches(":hover:focus-visible")));
        assert.equal(await css(second, "backgroundColor"), selectedHover);
        assert.equal(await css(second, "boxShadow"), ring);
        await clearHover();
        assert.equal(await css(second, "backgroundColor"), selectedBg);
        assert.equal(await css(second, "boxShadow"), ring);

        // The callbacks deliver the tab key to shared model state. The outside palette stays light.
        const outside = page.locator("#page");
        await selection(outside, "Two");
        const outsideTab = outside.getByRole("tab", { name: "Two", exact: true });
        assert.equal(await css(outsideTab, "backgroundColor"), "rgb(224, 239, 255)");
        assert.equal(await css(outsideTab, "borderTopColor"), "rgb(152, 165, 184)");
        await first.click();
        await selection(root, "One");
      }
    }
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
