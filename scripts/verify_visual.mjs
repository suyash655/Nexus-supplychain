import { chromium } from "d:/supex1/frontend/node_modules/playwright-core/index.mjs";
import fs from "fs";
import path from "path";

async function main() {
  const outDir = "d:/supex1/docs/assets/recreation";
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  console.log("Launching headless Chromium...");
  const browser = await chromium.launch({ headless: true });

  const viewports = [
    { name: "desktop_1440x900", width: 1440, height: 900 },
    { name: "tablet_768x1024", width: 768, height: 1024 },
    { name: "mobile_375x812", width: 375, height: 812 },
  ];

  for (const vp of viewports) {
    const page = await browser.newPage({
      viewport: { width: vp.width, height: vp.height },
    });
    console.log(`Navigating to http://localhost:3000 at ${vp.name}...`);
    try {
      await page.goto("http://localhost:3000", { waitUntil: "networkidle", timeout: 15000 });
      await page.waitForTimeout(1000);
      const filePath = path.join(outDir, `${vp.name}.png`);
      await page.screenshot({ path: filePath, fullPage: false });
      console.log(`[SUCCESS] Saved ${filePath}`);
    } catch (err) {
      console.error(`[ERROR] at ${vp.name}:`, err.message);
    } finally {
      await page.close();
    }
  }

  await browser.close();
  console.log("All visual screenshots captured successfully!");
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
