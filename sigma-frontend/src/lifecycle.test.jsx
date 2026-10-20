import { act, renderHook, waitFor } from '@testing-library/react';
import { expect, it, vi, beforeEach } from 'vitest';
import { apiRequest } from './api';
import { useResource } from './useResource';
import { useActionRequest } from './useActionRequest';
vi.mock('./api', () => ({ apiRequest: vi.fn() }));
beforeEach(() => { vi.mocked(apiRequest).mockReset(); });
it('resposta 401 da sessão anterior não expira uma sessão nova', async () => {
  const pending = {};
  vi.mocked(apiRequest).mockImplementation((path, options) => new Promise((resolve, reject) => { pending[options.token] = { resolve, reject }; }));
  const expire = vi.fn();
  const hook = renderHook(({ token }) => useResource('/synthetic', token, expire), { initialProps: { token: 'old' } });
  hook.rerender({ token: 'new' });
  await act(async () => pending.new.resolve({ marker: 'new' }));
  await act(async () => pending.old.reject(Object.assign(new Error('expired'), { status: 401 })));
  await waitFor(() => expect(hook.result.current.data).toEqual({ marker: 'new' }));
  expect(expire).not.toHaveBeenCalled();
});
it('ação pendente é cancelada ao sair da página, mesmo com resposta tardia', async () => {
  let reject;
  vi.mocked(apiRequest).mockImplementation(() => new Promise((resolve, fail) => { reject = fail; }));
  const hook = renderHook(() => useActionRequest('old'));
  const result = hook.result.current('/synthetic').catch(error => error);
  hook.unmount();
  reject(Object.assign(new Error('expired'), { status: 401 }));
  expect(await result).toMatchObject({ name: 'AbortError' });
});
