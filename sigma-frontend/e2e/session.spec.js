import { test, expect } from '@playwright/test';

async function login(page) {
  await page.goto('/');
  await page.getByLabel('Usuário', { exact: true }).fill('browser.demo');
  await page.getByLabel('Senha', { exact: true }).fill(process.env.SIGMA_BROWSER_PASSWORD);
  await page.getByRole('button', { name: 'Entrar', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Sair', exact: true })).toBeVisible();
}

test('login → diagnóstico simulado → logout com revogação real', async ({ page, request }) => {
  let token;
  page.on('response', async response => {
    if (response.url().endsWith('/api/auth/login') && response.status() === 200) {
      token = (await response.json()).access_token;
    }
  });
  await login(page);
  await page.getByRole('button', { name: 'Solicitar diagnóstico' }).click();
  await expect(page.getByText('Diagnóstico K10 simulado', { exact: true })).toBeVisible();
  await expect(page.locator('pre')).toContainText('192.0.2.0/24');
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })))
    .toEqual({ local: 0, session: 0 });
  await page.screenshot({ path: '../test-results/painel-diagnostico.png', fullPage: true });
  await page.getByRole('button', { name: 'Sair', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Entrar', exact: true })).toBeVisible();
  expect(token).toBeTruthy();
  const response = await request.get('http://127.0.0.1:18000/api/status', {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(response.status()).toBe(401);
});

test('recarregar exige novo login', async ({ page }) => {
  await login(page);
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Entrar', exact: true })).toBeVisible();
});

test('401, 403 e falha de rede apresentam mensagens distintas', async ({ page }) => {
  await login(page);
  for (const [status, text] of [[403, 'Seu perfil não tem permissão'], [401, 'Sessão ausente']]) {
    await page.route('**/api/alertas', route => route.fulfill({
      status, contentType: 'application/json', body: JSON.stringify({ detail: 'genérico' }),
    }));
    await page.getByRole('button', { name: 'Solicitar diagnóstico' }).click();
    await expect(page.getByRole('alert')).toContainText(text);
  }
  await page.unroute('**/api/alertas');
  await login(page);
  await page.route('**/api/alertas', route => route.abort());
  await page.getByRole('button', { name: 'Solicitar diagnóstico' }).click();
  await expect(page.getByRole('alert')).toContainText('Não foi possível conectar');
});
