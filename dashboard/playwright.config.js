import { defineConfig } from '@playwright/test';

const liveURL = process.env.DASHBOARD_TEST_URL;
export default defineConfig({
  testDir: './e2e',
  workers: 1,
  timeout: 90000,
  expect: { timeout: 15000 },
  use: {
    baseURL: liveURL || 'http://127.0.0.1:4179',
    channel: 'chrome',
    launchOptions: {
      chromiumSandbox: true,
      args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
    },
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'desktop', use: { viewport: { width: 1440, height: 950 } } },
    { name: 'mobile-width', use: { viewport: { width: 390, height: 844 } } },
  ],
  webServer: liveURL ? undefined : {
    command: 'npm run dev -- --host 127.0.0.1 --port 4179 --strictPort',
    url: 'http://127.0.0.1:4179',
  },
});
