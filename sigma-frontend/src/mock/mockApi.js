// API simulada para trabalhar no visual sem Python, PostgreSQL ou chave de IA.
// Mantém o mesmo contrato de apiRequest/readEventStream: erros viram ApiError e
// o RBAC da API é reproduzido. Cenários pela URL: ?cenario=vazio|erro|lento|falha-trilha
import { ApiError } from '../api';
import { initialState, metricas, roles } from './data';

const level = { suporte_n1: 1, analista_redes: 2, gestor_ti: 3 };
const scenario = () => new URLSearchParams(globalThis.location?.search || '').get('cenario') || 'normal';
let state = initialState();
let lastEvent = 3;

export function resetMock() { state = initialState(); lastEvent = 3; }

function wait(ms, signal) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener('abort', () => { clearTimeout(timer); reject(new DOMException('Cancelado', 'AbortError')); }, { once: true });
  });
}

function session(token) {
  const [, papel, ...name] = (token || '').split(':');
  if (!level[papel]) throw new ApiError(401);
  return { usuario: name.join(':'), papel };
}

function allow(token, minimum) {
  const user = session(token);
  if (level[user.papel] < level[minimum]) throw new ApiError(403);
  return user;
}

function log(ator, acao, recurso) {
  state.eventos.unshift({ id: ++lastEvent, ts: new Date().toISOString(), ator, acao, recurso });
}

const routes = [
  ['POST', /^\/api\/auth\/login$/, ({ body }) => {
    const key = Object.keys(roles).find(prefix => body?.username?.toLowerCase().startsWith(prefix));
    if (!key || !body?.password) throw new ApiError(401);
    const papel = roles[key];
    return { access_token: `mock:${papel}:${body.username}`, token_type: 'bearer', expires_in: 3600, usuario: body.username, papel };
  }],
  ['GET', /^\/api\/auth\/me$/, ({ token }) => session(token)],
  ['POST', /^\/api\/auth\/logout$/, ({ token }) => { session(token); return { revogado: true }; }],
  ['GET', /^\/api\/eng\/saude$/, ({ token }) => {
    allow(token, 'suporte_n1');
    return { servicos: scenario() === 'vazio' ? [] : state.servicos, gerado_em: new Date().toISOString(), limite: 500 };
  }],
  ['GET', /^\/api\/eng\/incidentes\/resumo$/, ({ token }) => {
    allow(token, 'analista_redes');
    return scenario() === 'vazio' ? { incidentes: [], metricas: {}, limite: 500 }
      : { incidentes: state.incidentes, metricas, limite: 500 };
  }],
  ['POST', /^\/api\/eng\/incidentes\/([^/]+)\/(reconhecer|resolver)$/, ({ token, match }) => {
    const user = allow(token, 'analista_redes');
    const item = state.incidentes.find(row => row.id === match[1]);
    if (!item) throw new ApiError(404);
    const field = match[2] === 'resolver' ? 'resolvido_em' : 'reconhecido_em';
    if (item.resolvido_em || item[field]) throw new ApiError(409);
    item[field] = new Date().toISOString();
    log(user.usuario, match[2] === 'resolver' ? 'incident.resolve' : 'incident.ack', item.id);
    return item;
  }],
  ['GET', /^\/api\/eng\/aprovacoes$/, ({ token }) => {
    allow(token, 'analista_redes');
    return { aprovacoes: scenario() === 'vazio' ? [] : state.aprovacoes.filter(item => item.estado === 'pending') };
  }],
  ['POST', /^\/api\/eng\/aprovacoes$/, ({ token, body }) => {
    const user = allow(token, 'analista_redes');
    if (!body?.acao?.trim()) throw new ApiError(422);
    const item = { id: `aprov-${Date.now()}`, acao: body.acao, solicitante: user.usuario, criada_em: new Date().toISOString(),
      expira_em: new Date(Date.now() + 15 * 60000).toISOString(), papel_minimo: body.papel_minimo || 'analista_redes', estado: 'pending' };
    state.aprovacoes.push(item);
    log(user.usuario, 'approval.requested', item.id);
    return item;
  }],
  ['POST', /^\/api\/eng\/aprovacoes\/([^/]+)\/decidir$/, ({ token, body, match }) => {
    const user = allow(token, 'analista_redes');
    const item = state.aprovacoes.find(row => row.id === match[1]);
    if (!item) throw new ApiError(404);
    if (item.estado !== 'pending' || item.solicitante === user.usuario || level[user.papel] < level[item.papel_minimo])
      throw new ApiError(409);
    Object.assign(item, { estado: body?.aprovar ? 'approved' : 'rejected', decidida_por: user.usuario, justificativa: body?.justificativa });
    log(user.usuario, body?.aprovar ? 'approval.approved' : 'approval.rejected', item.id);
    return item;
  }],
  ['GET', /^\/api\/eng\/auditoria\/verificar$/, ({ token }) => {
    allow(token, 'gestor_ti');
    if (scenario() === 'vazio') return { integra: true, primeira_invalida: null, entradas: 0 };
    return scenario() === 'falha-trilha' ? { integra: false, primeira_invalida: 57, entradas: 128 } : state.trilha;
  }],
  ['GET', /^\/api\/eng\/auditoria\/recentes$/, ({ token }) => {
    allow(token, 'gestor_ti');
    return { eventos: scenario() === 'vazio' ? [] : state.eventos.slice(0, 100) };
  }],
  ['POST', /^\/api\/alertas$/, ({ token, body }) => {
    allow(token, 'suporte_n1');
    const texto = (body?.descricao_erro || '').replace(/\b(\d{1,3}\.\d{1,3}\.\d{1,3})\.\d{1,3}\b/g, '$1.0/24');
    return { status: 'Incidente Registrado',
      dados_enviados_nuvem: `Equipamento: Equipamento de rede | Erro: ${texto}. Forneça um diagnóstico de rede curto e direto.`,
      diagnostico_ia: '[Resposta simulada] Verifique o enlace físico e os contadores de erro da interface; '
        + 'perda de pacotes persistente costuma indicar cabo ou porta com defeito, ou saturação do uplink.' };
  }],
];

export async function mockRequest(path, { method = 'GET', body, token, signal } = {}) {
  await wait(scenario() === 'lento' ? 2500 : 250, signal);
  const isAuth = path.startsWith('/api/auth/');
  if (scenario() === 'erro' && !isAuth) throw new ApiError(503);
  const pathname = path.split('?')[0];
  for (const [verb, pattern, handler] of routes) {
    const match = pathname.match(pattern);
    if (verb === method && match) return structuredClone(handler({ token, body, match }));
  }
  throw new ApiError(404);
}

// Simula o SSE: conecta e permanece aberto até a sessão sair da tela.
export async function mockEventStream({ token, signal, onReady }) {
  await wait(300, signal);
  session(token);
  if (scenario() === 'erro') throw new ApiError(503);
  onReady();
  await new Promise((resolve, reject) => {
    if (signal.aborted) reject(new DOMException('Cancelado', 'AbortError'));
    signal.addEventListener('abort', () => reject(new DOMException('Cancelado', 'AbortError')), { once: true });
  });
}
