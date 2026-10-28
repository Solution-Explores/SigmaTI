import { test, expect } from '@playwright/test';
import { createServer } from 'node:net';
import AxeBuilder from '@axe-core/playwright';

const API = 'http://127.0.0.1:18000';
async function accessible(page) {
  const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(result.violations).toEqual([]);
}

async function login(page, username) {
  await page.goto('/');
  await page.getByLabel('Usuário', { exact: true }).fill(username);
  await page.getByLabel('Senha', { exact: true }).fill(process.env.SIGMA_BROWSER_PASSWORD);
  const response = page.waitForResponse(r => r.url().endsWith('/api/auth/login') && r.status() === 200);
  await page.getByRole('button', { name: 'Entrar', exact: true }).click();
  const token = (await (await response).json()).access_token;
  await expect(page.getByRole('heading', { name: 'Saúde dos serviços', exact: true })).toBeVisible();
  return token;
}
async function unusedPort() {
  const server = createServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  await new Promise(resolve => server.close(resolve));
  return port;
}

test('operacional: N1 vê saúde sem ações privilegiadas, com temas e teclado', async ({ page, request }) => {
  const token = await login(page, 'browser.demo');
  await expect(page.getByRole('rowheader', { name: /^Portal de testes/ })).toBeVisible();
  await expect(page.getByText('Janela observada')).toBeVisible();
  await expect(page.getByText('Sem dados recentes')).toBeVisible();
  const nav = page.getByRole('navigation', { name: 'Áreas do painel' });
  await expect(nav.getByRole('button')).toHaveCount(2);
  for (const path of ['/api/eng/incidentes/resumo', '/api/eng/aprovacoes', '/api/eng/auditoria/recentes']) {
    expect((await request.get(API + path, { headers: { Authorization: `Bearer ${token}` } })).status()).toBe(403);
  }
  await accessible(page);
  await page.screenshot({ path: '../test-results/panel-health-dark-desktop.png', fullPage: true });
  await page.getByRole('button', { name: 'Tema claro' }).click();
  await expect(page.locator('.app-surface')).toHaveAttribute('data-theme', 'light');
  await accessible(page);
  await page.screenshot({ path: '../test-results/panel-health-light-desktop.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await accessible(page);
  await page.screenshot({ path: '../test-results/panel-health-light-mobile.png', fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.keyboard.press('Control+Home');
  await page.getByRole('button', { name: 'Diagnóstico', exact: true }).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Enviar alerta' })).toBeVisible();
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
});

test('operacional: dois integrantes aprovam com justificativa persistida e quatro olhos', async ({ browser, request }) => {
  const first = await browser.newContext();
  const second = await browser.newContext();
  try {
    const a = await first.newPage();
    const token = await login(a, 'browser.analyst');
    await a.getByRole('button', { name: 'Aprovações', exact: true }).click();
    await a.getByText('Nova solicitação', { exact: true }).click();
    const action = `Mudança fictícia ${Date.now()}`;
    await a.getByLabel('Ação a revisar').fill(action);
    const created = a.waitForResponse(r => r.url().endsWith('/api/eng/aprovacoes') && r.request().method() === 'POST');
    await a.getByRole('button', { name: 'Solicitar revisão' }).click();
    const approval = await (await created).json();
    const own = a.getByRole('article', { name: `Solicitação: ${action}` });
    await expect(own.getByRole('button', { name: 'Aprovar' })).toBeDisabled();
    const forbidden = await request.post(`${API}/api/eng/aprovacoes/${approval.id}/decidir`, {
      headers: { Authorization: `Bearer ${token}` }, data: { aprovar: true, justificativa: 'tentativa própria' },
    });
    expect(forbidden.status()).toBe(409);
    const b = await second.newPage();
    const reviewerToken = await login(b, 'browser.reviewer');
    await b.getByRole('button', { name: 'Aprovações', exact: true }).click();
    const row = b.getByRole('article', { name: `Solicitação: ${action}` });
    await row.getByLabel('Justificativa da decisão').fill('Revisado com evidência sintética');
    await row.getByRole('button', { name: 'Aprovar' }).click();
    await expect(b.getByText('Solicitação aprovada.', { exact: true })).toBeVisible();
    const persisted = await request.get(`${API}/api/eng/aprovacoes/${approval.id}`, { headers: { Authorization: `Bearer ${reviewerToken}` } });
    expect(await persisted.json()).toMatchObject({ estado: 'approved', decidida_por: 'browser.reviewer', justificativa: 'Revisado com evidência sintética' });
    await accessible(b);
    await b.screenshot({ path: '../test-results/panel-approvals-desktop.png', fullPage: true });
  } finally { await first.close(); await second.close(); }
});

test('operacional: falha real chega ao painel via SSE, reconecta com cursor e logout encerra', async ({ page, request, context }) => {
  const token = await login(page, 'browser.manager');
  await expect(page.getByText('Tempo real ativo', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Incidentes', exact: true }).click();
  const name = `Alvo derrubado ${Date.now()}`;
  const started = Date.now();
  const targetResponse = await request.post(API + '/api/eng/alvos', { headers: { Authorization: `Bearer ${token}` },
    data: { nome: name, host: '127.0.0.1', porta: await unusedPort(), intervalo_s: .2, timeout_s: .3 } });
  expect(targetResponse.status()).toBe(200);
  await expect(page.getByText(name, { exact: true })).toBeVisible({ timeout: 5000 });
  expect(Date.now() - started).toBeLessThanOrEqual(5000);
  await accessible(page);
  await page.screenshot({ path: '../test-results/panel-incidents-desktop.png', fullPage: true });
  await context.setOffline(true);
  await expect(page.getByText(/Reconectando ao tempo real/)).toBeVisible({ timeout: 18000 });
  const reconnect = page.waitForRequest(r => r.url().endsWith('/api/eng/eventos') && !!r.headers()['last-event-id']);
  await context.setOffline(false);
  await reconnect;
  await expect(page.getByText('Tempo real ativo', { exact: true })).toBeVisible();
  await request.post(API + '/api/auth/logout', { headers: { Authorization: `Bearer ${token}` } });
  await expect(page.getByRole('heading', { name: 'Entrar', exact: true })).toBeVisible({ timeout: 5000 });
  await expect(page.getByRole('button', { name: 'Incidentes', exact: true })).toHaveCount(0);
});

test('operacional: auditoria restrita ao gestor distingue trilhas e mostra eventos reais', async ({ page }) => {
  await login(page, 'browser.manager');
  await page.getByRole('button', { name: 'Auditoria', exact: true }).click();
  await expect(page.getByText(/Integridade consistente/)).toBeVisible();
  await expect(page.getByText(/armazenamento separado/)).toBeVisible();
  await expect(page.getByRole('cell', { name: 'target.created', exact: true }).first()).toBeVisible();
  await accessible(page);
  await page.screenshot({ path: '../test-results/panel-audit-desktop.png', fullPage: true });
});
