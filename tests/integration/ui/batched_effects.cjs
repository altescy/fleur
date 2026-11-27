const { chromium } = require("playwright-core");

async function run() {
  const browser = await chromium.launch({ executablePath: process.argv[2] });
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[3]);
    // The page replaces its default title with a JSON result once its timers have fired.
    await page.waitForFunction(() => document.title.startsWith("{"));
    process.stdout.write(await page.title());
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
