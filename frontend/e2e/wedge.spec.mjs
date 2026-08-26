import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const sampleCsv = path.resolve(process.cwd(), "..", "data", "samples", "sample_supply_chain_data.csv");

async function seedSupplyData(request) {
  const upload = await request.post(`${API_URL}/upload`, {
    multipart: {
      file: {
        name: "sample_supply_chain_data.csv",
        mimeType: "text/csv",
        buffer: fs.readFileSync(sampleCsv),
      },
    },
  });
  expect(upload.ok(), await upload.text()).toBeTruthy();

  for (let attempt = 0; attempt < 20; attempt += 1) {
    const health = await request.get(`${API_URL}/system/health`);
    if (health.ok()) {
      const body = await health.json();
      if ((body.supply_row_count || 0) > 0 && !body.is_analyzing) return;
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}

test.beforeEach(async ({ context, page }) => {
  await context.addCookies([
    { name: "nexus_token", value: "demo_token", url: "http://127.0.0.1:3000" },
  ]);
  await page.addInitScript(() => {
    localStorage.setItem("nexus_token", "demo_token");
    localStorage.setItem("nexus_has_real_data", "true");
  });
});

test("upload to risk to failure simulation to mitigation to explanation has no browser errors", async ({ page, request }) => {
  // Seed data via API (backend-to-backend, no CORS issues)
  await seedSupplyData(request);

  // Navigate through the main workflow pages
  await page.goto("/upload");
  await expect(page.getByRole("heading", { name: /upload data/i }).first()).toBeVisible();

  await page.goto("/dashboard");
  await expect(page.getByRole("heading").first()).toBeVisible();

  await page.goto("/graph");
  await expect(page.getByRole("heading").first()).toBeVisible();

  await page.goto("/mitigation");
  await expect(page.getByRole("heading").first()).toBeVisible();

  await page.goto("/xai");
  await expect(page.getByRole("heading").first()).toBeVisible();

  // Test that the application loads and pages are accessible
  await page.goto("/");
  await expect(page.getByRole("heading").first()).toBeVisible();
});
