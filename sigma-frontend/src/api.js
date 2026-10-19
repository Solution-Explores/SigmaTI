const BASE_URL = (import.meta.env?.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(status) {
    const messages = {
      401: 'Sessão ausente, expirada ou credenciais inválidas. Entre novamente.',
      403: 'Seu perfil não tem permissão para esta operação.',
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
      signal: signal || AbortSignal.timeout(18000),
      credentials: 'omit',
    });
  } catch {
    throw new Error('Não foi possível conectar à API. Confira a conexão e tente novamente.');
  }
  if (!response.ok) throw new ApiError(response.status);
  try {
    return await response.json();
  } catch {
    throw new Error('A API retornou uma resposta inválida. Tente novamente.');
  }
}
