import { beforeEach, expect, it, vi } from 'vitest';
import { mockRequest, resetMock } from './mockApi';

beforeEach(() => { resetMock(); vi.useFakeTimers({ shouldAdvanceTime: true, advanceTimeDelta: 50 }); });
const call = (path, options) => mockRequest(path, options);
const login = async username => (await call('/api/auth/login', { method: 'POST', body: { username, password: 'x' } })).access_token;

it('reproduz o RBAC da API', async () => {
  const suporte = await login('suporte.ana');
  expect(await call('/api/auth/me', { token: suporte })).toEqual({ usuario: 'suporte.ana', papel: 'suporte_n1' });
  expect((await call('/api/eng/saude', { token: suporte })).servicos.length).toBeGreaterThan(0);
  await expect(call('/api/eng/incidentes/resumo', { token: suporte })).rejects.toMatchObject({ status: 403 });
  await expect(call('/api/eng/saude')).rejects.toMatchObject({ status: 401 });
});

it('impede autoaprovação e registra a decisão de outro integrante', async () => {
  const autor = await login('analista.maria');
  const pedido = await call('/api/eng/aprovacoes', { method: 'POST', token: autor, body: { acao: 'Reiniciar porta', papel_minimo: 'analista_redes' } });
  const decidir = token => call(`/api/eng/aprovacoes/${pedido.id}/decidir`, { method: 'POST', token, body: { aprovar: true, justificativa: 'ok' } });
  await expect(decidir(autor)).rejects.toMatchObject({ status: 409 });
  expect((await decidir(await login('gestor.joao'))).estado).toBe('approved');
});

it('não reconhece incidente já resolvido', async () => {
  const token = await login('analista.maria');
  const { incidentes } = await call('/api/eng/incidentes/resumo', { token });
  const resolvido = incidentes.find(item => item.resolvido_em);
  await expect(call(`/api/eng/incidentes/${resolvido.id}/reconhecer`, { method: 'POST', token })).rejects.toMatchObject({ status: 409 });
});
