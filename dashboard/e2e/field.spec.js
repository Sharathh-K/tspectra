import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { geometry } from '../src/layers/geometry.js';

const fixture = JSON.parse(readFileSync(new URL('../public/mock/risk.json', import.meta.url)));
const { cells } = geometry(fixture);
const flagged = cells.filter(cell => cell.label === 1);
const coordinate = cell => cell.center[1].toFixed(6) + '° N, ' + cell.center[0].toFixed(6) + '° E';
const frame = page => page.evaluate(() => new Promise(resolve =>
  requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));

test('renders the field, picks real cells, and updates map controls', async ({page}, info) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  await page.goto('/');
  await expect(page).toHaveTitle('TerraSpectra · Field monitor');
  await expect(page.getByText('21 flagged pixels · 4.67 acres')).toBeVisible();
  await expect(page.getByText('67 × 67')).toBeVisible();
  const map = page.getByRole('region', {name:'Interactive farm map'});
  const canvas = map.locator('canvas').first();
  await expect(canvas).toBeVisible();
  await frame(page);
  await expect.poll(async () => {
    await canvas.click();
    return page.locator('aside [aria-live]').textContent({timeout: 1500}).catch(() => '');
  }).toContain('Healthy');
  const pick = await page.locator('aside [aria-live]').innerText();
  const [,row,col] = pick.match(/Row (\d+) · Column (\d+)/);
  expect(pick).toContain(coordinate(cells[Number(row) * fixture.width + Number(col)]));

  await page.getByRole('button', {name:'Next flagged pixel'}).click();
  const next = flagged.find(cell => cell.id > Number(row) * fixture.width + Number(col)) ?? flagged[0];
  await expect(page.locator('aside [aria-live]')).toContainText(coordinate(next));
  const readMap = async () => { await frame(page); return canvas.screenshot(); };
  for (const label of ['Stress grid','Spectral composite','Farm boundary']) {
    const box = page.getByRole('checkbox', {name:label});
    const before = await readMap();
    await box.uncheck();
    await expect.poll(async () => !(await readMap()).equals(before)).toBe(true);
    await box.check();
  }
  for (const name of ['Zoom in','Zoom out','2D','3D','Fit']) {
    const before = await readMap();
    await map.getByRole('button', {name, exact:true}).click();
    await expect.poll(async () => !(await readMap()).equals(before)).toBe(true);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  expect(errors).toEqual([]);
  await page.screenshot({path:info.outputPath('field.png'), fullPage:true});
});

test('recovers from an unavailable scene when Retry succeeds', async ({page}) => {
  let first = true;
  await page.route(/\/(api\/risk|mock\/risk\.json)$/, route => {
    if (!first) return route.continue();
    first = false;
    return route.fulfill({status:503, body:'Unavailable'});
  });
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('503');
  await page.getByRole('button', {name:'Retry'}).click();
  await expect(page.getByText('21 flagged pixels · 4.67 acres')).toBeVisible();
});

test('uses clean text, navigates field sections and remembers the selected theme', async ({page}, info) => {
  await page.goto('/');
  await expect(page.getByText('67 \u00d7 67')).toBeVisible();
  const html = page.locator('html');
  const nav = page.getByRole('navigation', {name:'Field navigation'});
  const menu = page.getByRole('button', {name:'Menu', exact:true});
  const openMenu = async () => {
    if (await menu.isVisible() && !(await nav.isVisible())) await menu.click();
  };
  await expect(html).toHaveAttribute('data-theme','dark');
  await openMenu();
  const theme = page.getByRole('switch', {name:'Dark mode'});
  await expect(theme).toBeChecked();
  const darkBackground = await html.evaluate(el => getComputedStyle(el).backgroundColor);
  await theme.uncheck();
  await expect(html).toHaveAttribute('data-theme','light');
  expect(await html.evaluate(el => getComputedStyle(el).backgroundColor)).not.toBe(darkBackground);
  await page.reload();
  await expect(html).toHaveAttribute('data-theme','light');
  await page.getByText('67 \u00d7 67').waitFor();
  await openMenu();
  await expect(theme).not.toBeChecked();
  await theme.check();
  for (const [label,id] of [['Field map','field-map'],['Field summary','field-summary'],
    ['Map layers','map-layers'],['Pixel inspector','pixel-inspector']]) {
    await openMenu();
    await nav.getByRole('link', {name:label, exact:true}).click();
    await expect(page).toHaveURL(new RegExp('#'+id+'$'));
    await expect(page.getByRole('heading', {level:1, name:label, exact:true})).toBeVisible();
    await expect(page.locator('aside section:visible')).toHaveCount(id === 'field-map' ? 3 : 1);
    await expect(page.getByRole('region', {name:'Interactive farm map'})).toHaveCount(id === 'field-summary' ? 0 : 1);
    if (await menu.isVisible()) await expect(menu).toHaveAttribute('aria-expanded','false');
    await openMenu();
    await expect(nav.getByRole('link', {name:label, exact:true})).toHaveAttribute('aria-current','page');
  }
  if (await menu.isVisible()) {
    await page.keyboard.press('Escape');
    await expect(menu).toBeFocused();
    await expect(nav).toBeHidden();
  }
  await page.getByRole('button', {name:'Inspect flagged pixel'}).click();
  await expect(page.locator('aside [aria-live]')).toContainText(coordinate(flagged[0]));
  expect(await page.locator('body').innerText()).not.toMatch(/[\u00c2\u00c3\u00e2\ufffd\u0080-\u009f]/);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
