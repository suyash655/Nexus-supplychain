module.exports = {
  ci: {
    collect: {
      url: [
        "http://127.0.0.1:3000/dashboard",
        "http://127.0.0.1:3000/graph",
        "http://127.0.0.1:3000/mitigation",
        "http://127.0.0.1:3000/xai",
      ],
      numberOfRuns: 1,
      settings: {
        chromeFlags: "--no-sandbox --disable-dev-shm-usage",
        preset: "desktop",
      },
      puppeteerScript: "./lighthouse-auth.cjs",
    },
    assert: {
      assertions: {
        "categories:accessibility": ["error", { minScore: 0.9 }],
        "categories:best-practices": ["warn", { minScore: 0.85 }],
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
