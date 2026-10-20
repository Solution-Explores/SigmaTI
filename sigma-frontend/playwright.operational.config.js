import { defineConfig } from '@playwright/test';
import base from './playwright.config.js';
export default defineConfig({ ...base, testDir: './e2e-operational', timeout: 45000,
  use: { ...base.use, viewport: { width: 1440, height: 1000 } },
  reporter: [['list'], ['junit', { outputFile: '../test-results/panel-browser.xml' }]],
  outputDir: '../test-results/panel-playwright',
});
