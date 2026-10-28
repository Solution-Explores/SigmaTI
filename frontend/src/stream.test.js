import { afterEach, expect, it, vi } from 'vitest';
import { readEventStream } from './api';
afterEach(() => vi.unstubAllGlobals());
function response(text) {
  const bytes = new TextEncoder().encode(text);
  const body = new ReadableStream({ start(controller) {
    for (let i = 0; i < bytes.length; i += 3) controller.enqueue(bytes.slice(i, i + 3));
    controller.close();
  } });
  return { ok: true, headers: new Headers({ 'content-type': 'text/event-stream' }), body };
}
it('interpreta UTF-8/CRLF fragmentados e conserva cursor sem perder precisão', async () => {
  const fetch = vi.fn().mockResolvedValue(response('id: 9007199254740993\r\nevent: incidente\r\ndata: {"acao":"ação"}\r\n\r\n'));
  vi.stubGlobal('fetch', fetch);
  const onEvent = vi.fn();
  await expect(readEventStream({ token: 'synthetic', cursor: '9007199254740992', signal: new AbortController().signal,
    onReady: vi.fn(), onEvent })).rejects.toThrow('Fluxo encerrado');
  expect(onEvent).toHaveBeenCalledWith('9007199254740993', { acao: 'ação' });
  const [url, options] = fetch.mock.calls[0];
  expect(url).not.toContain('synthetic');
  expect(options.headers['Last-Event-ID']).toBe('9007199254740992');
  expect(options.credentials).toBe('omit');
});
it('encerra sessão quando servidor revoga o stream', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response('event: session.closed\ndata: {}\n\n')));
  await expect(readEventStream({ token: 'synthetic', signal: new AbortController().signal,
    onReady: vi.fn(), onEvent: vi.fn() })).rejects.toMatchObject({ status: 401 });
});
