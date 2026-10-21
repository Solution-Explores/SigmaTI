// Dados fictícios no mesmo formato das respostas da API real (routers/ e sigma_eng/).
// Usados somente com `npm run dev:mock`; nunca entram no build de produção.
const minutes = n => new Date(Date.now() - n * 60000).toISOString();
const later = n => new Date(Date.now() + n * 60000).toISOString();

export const roles = { suporte: 'suporte_n1', analista: 'analista_redes', gestor: 'gestor_ti' };

export function initialState() {
  return {
    servicos: [
      { id: 'alvo-1', nome: 'Prontuário eletrônico', host: '192.0.2.20', porta: 443, kind: 'https', ativo: true,
        status: 'up', ultima_em: minutes(0.2), latencia_ms: 42.7, alvo_pct: 99.9, janela_dias: 30,
        orcamento: { completo: true, cobertura_pct: 100, consumido_min: 12.4, total_min: 43.2, restante_max_min: 30.8,
          disponibilidade_observada_pct: 99.971, status: 'healthy', esgota_em: null } },
      { id: 'alvo-2', nome: 'Servidor de imagens (PACS)', host: '192.0.2.31', porta: 104, kind: 'tcp', ativo: true,
        status: 'down', ultima_em: minutes(0.1), latencia_ms: null, alvo_pct: 99.5, janela_dias: 7,
        orcamento: { completo: true, cobertura_pct: 100, consumido_min: 41.5, total_min: 50.4, restante_max_min: 8.9,
          disponibilidade_observada_pct: 99.588, status: 'at_risk', esgota_em: later(60 * 20) } },
      { id: 'alvo-3', nome: 'Portal do paciente', host: '192.0.2.40', porta: 80, kind: 'http', ativo: true,
        status: 'up', ultima_em: minutes(0.3), latencia_ms: 120.3, alvo_pct: 99.9, janela_dias: 30,
        orcamento: { completo: false, cobertura_pct: 18.5, consumido_min: 0, total_min: 43.2, restante_max_min: 43.2,
          disponibilidade_observada_pct: 100, status: 'partial', esgota_em: null } },
      { id: 'alvo-4', nome: 'Switch do bloco cirúrgico', host: '192.0.2.50', porta: 22, kind: 'tcp', ativo: true,
        status: 'down', ultima_em: minutes(0.1), latencia_ms: null, alvo_pct: 99, janela_dias: 1,
        orcamento: { completo: true, cobertura_pct: 100, consumido_min: 20, total_min: 14.4, restante_max_min: 0,
          disponibilidade_observada_pct: 98.611, status: 'breaching', esgota_em: null } },
      { id: 'alvo-5', nome: 'Impressora da farmácia', host: '192.0.2.60', porta: 9100, kind: 'tcp', ativo: true,
        status: 'unknown', ultima_em: minutes(45), latencia_ms: null, alvo_pct: null, janela_dias: null, orcamento: null },
      { id: 'alvo-6', nome: 'Servidor legado', host: '192.0.2.70', porta: 8080, kind: 'http', ativo: false,
        status: 'inactive', ultima_em: null, latencia_ms: null, alvo_pct: null, janela_dias: null, orcamento: null },
    ],
    incidentes: [
      { id: '7f3c2a10-0000-4000-8000-000000000001', alvo_id: 'alvo-4', nome_alvo: 'Switch do bloco cirúrgico',
        tipo: 'indisponibilidade', severidade: 'P1', detectado_em: minutes(25), reconhecido_em: null, resolvido_em: null },
      { id: '7f3c2a10-0000-4000-8000-000000000002', alvo_id: 'alvo-2', nome_alvo: 'Servidor de imagens (PACS)',
        tipo: 'latencia', severidade: 'P2', detectado_em: minutes(70), reconhecido_em: minutes(64), resolvido_em: null },
      { id: '7f3c2a10-0000-4000-8000-000000000003', alvo_id: 'alvo-1', nome_alvo: 'Prontuário eletrônico',
        tipo: 'indisponibilidade', severidade: 'P3', detectado_em: minutes(600), reconhecido_em: minutes(596), resolvido_em: minutes(560) },
    ],
    aprovacoes: [
      { id: 'aprov-1', acao: 'Reiniciar a porta 12 do switch do bloco cirúrgico', solicitante: 'maria.analista',
        criada_em: minutes(3), expira_em: later(12), papel_minimo: 'analista_redes', estado: 'pending' },
      { id: 'aprov-2', acao: 'Alterar regra de firewall da VLAN de imagens', solicitante: 'joao.analista',
        criada_em: minutes(5), expira_em: later(10), papel_minimo: 'gestor_ti', estado: 'pending' },
    ],
    eventos: [
      { id: 3, ts: minutes(25), ator: 'coletor', acao: 'incident.created', recurso: '7f3c2a10-0000-4000-8000-000000000001' },
      { id: 2, ts: minutes(64), ator: 'maria.analista', acao: 'incident.ack', recurso: '7f3c2a10-0000-4000-8000-000000000002' },
      { id: 1, ts: minutes(560), ator: 'joao.analista', acao: 'incident.resolve', recurso: '7f3c2a10-0000-4000-8000-000000000003' },
    ],
    trilha: { integra: true, primeira_invalida: null, entradas: 128 },
  };
}

export const metricas = { MTTD: { n: 0 }, MTTA: { n: 2, media_s: 300, mediana_s: 300, p95_s: 354 },
  MTTR: { n: 1, media_s: 2400, mediana_s: 2400, p95_s: 2400 } };
