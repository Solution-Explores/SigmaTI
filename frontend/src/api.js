export const BASE_URL = (import.meta.env?.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(status) {
    const messages = {
      401: 'Sessão ausente, expirada ou credenciais inválidas. Entre novamente.',
      403: 'Seu perfil não tem permissão para esta operação.',
      409: 'O registro mudou ou a decisão não é permitida. Atualize os dados antes de tentar novamente.',
      422: 'Confira os dados informados.',
      429: 'Muitas tentativas. Aguarde antes de tentar novamente.',
    };
    super(messages[status] || 'A API está indisponível no momento. Tente novamente.');
    this.status = status;
  }
}

export async function apiRequest(path, { method = 'GET', body, token, signal } = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: {
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(18000)]) : AbortSignal.timeout(18000),
      credentials: 'omit',
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new Error('Não foi possível conectar à API. Confira a conexão e tente novamente.', { cause: error });
  }
  if (!response.ok) throw new ApiError(response.status);
  try {
    return await response.json();
  } catch {
    throw new Error('A API retornou uma resposta inválida. Tente novamente.');
  }
}


export async function readEventStream({ token, cursor, signal, onEvent, onReady }) {
  const connection = new AbortController();
  let timer;
  let reader;
  const renew = () => { clearTimeout(timer); timer = setTimeout(() => connection.abort(), 15000); };
  renew();
  try {
    const response = await fetch(`${BASE_URL}/api/eng/eventos`, {
      headers: { Authorization: `Bearer ${token}`, ...(cursor ? { 'Last-Event-ID': cursor } : {}) },
      signal: AbortSignal.any([signal, connection.signal]), credentials: 'omit', cache: 'no-store',
    });
    if (!response.ok) throw new ApiError(response.status);
    if (!response.headers.get('content-type')?.includes('text/event-stream') || !response.body)
      throw new Error('Fluxo de eventos inválido.');
    onReady(); renew();
    reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) throw new Error('Fluxo encerrado.');
      renew();
      buffer += decoder.decode(value, { stream: true });
      buffer = buffer.replace(/\r\n/g, '\n');
      if (buffer.length > 65536) throw new Error('Evento excedeu o limite.');
      let boundary;
      while ((boundary = buffer.indexOf('\n\n')) >= 0) {
        const raw = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const fields = {};
        for (const line of raw.split('\n')) {
          if (!line || line.startsWith(':')) continue;
          const i = line.indexOf(':');
          if (i < 0) continue;
          fields[line.slice(0, i)] = line.slice(i + 1).replace(/^ /, '');
        }
        if (fields.event === 'session.closed') throw new ApiError(401);
        if (fields.event === 'stream.error') throw new ApiError(503);
        if (fields.event === 'incidente' && /^\d+$/.test(fields.id || '') && fields.data)
          onEvent(fields.id, JSON.parse(fields.data));
      }
    }
  } finally {
    clearTimeout(timer);
    await reader?.cancel().catch(() => {});
    reader?.releaseLock();
  }
}
