import { defineConfig } from '@playwright/test';
import { randomBytes } from 'node:crypto';
import { resolve } from 'node:path';

process.env.SIGMA_BROWSER_PASSWORD ||= randomBytes(24).toString('base64url');
const python = resolve(process.platform === 'win32' ? '../.venv/Scripts/python.exe' : '../.venv/bin/python');

export default defineConfig({
  testDir: './e2e',
  workers: 1,
  retries: 0,
  use: { baseURL: 'http://127.0.0.1:5173', trace: 'retain-on-failure' },
  reporter: [['list'], ['junit', { outputFile: '../test-results/browser.xml' }]],
  outputDir: '../test-results/playwright',
  webServer: [
    { command: `"${python}" ../scripts/serve_browser_acceptance.py`,
      url: 'http://127.0.0.1:18000/docs', reuseExistingServer: false, timeout: 30000 },
    { command: 'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 --strictPort',
      url: 'http://127.0.0.1:5173', reuseExistingServer: false,
      env: { VITE_API_URL: 'http://127.0.0.1:18000' } },
  ],
});
