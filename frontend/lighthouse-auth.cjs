module.exports = async (browser) => {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:3000", { waitUntil: "domcontentloaded" });
  await page.evaluate(() => {
    localStorage.setItem("nexus_token", "demo_token");
    localStorage.setItem("nexus_has_real_data", "true");
  });
  await page.setCookie({
    name: "nexus_token",
    value: "demo_token",
    domain: "127.0.0.1",
    path: "/",
  });
  await page.close();
};
