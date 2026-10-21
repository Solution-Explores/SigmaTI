# 6. Contrato da API usado pelo front

Este é o "combinado" entre o visual e a integração: são as rotas que o painel chama e os campos que
ele lê. Enquanto esses nomes e formatos forem respeitados, a Joyce muda o visual com o mock e tudo
continua funcionando com a API real. Exemplos completos estão em [`src/mock/data.js`](../sigma-frontend/src/mock/data.js).

Todas as rotas (exceto o login) exigem `Authorization: Bearer <token>`. Datas vêm em ISO 8601 (UTC)
e o front as formata em `pt-BR` no fuso do navegador.

## Rotas

| Tela | Método e rota | Perfil mínimo | Envia | Recebe (campos usados) |
|---|---|---|---|---|
| Login | `POST /api/auth/login` | — | `{ username, password }` | `access_token`, `usuario`, `papel` |
| Login | `GET /api/auth/me` | qualquer | — | `usuario`, `papel` |
| Sair | `POST /api/auth/logout` | qualquer | — | — |
| Tempo real | `GET /api/eng/eventos` (SSE) | N1 | `Last-Event-ID` | eventos `incidente`, `session.closed`, `stream.error` |
| Saúde | `GET /api/eng/saude` | N1 | — | `servicos[]`, `gerado_em`, `limite` |
| Incidentes | `GET /api/eng/incidentes/resumo` | Analista | — | `incidentes[]`, `metricas`, `limite` |
| Incidentes | `POST /api/eng/incidentes/{id}/reconhecer` | Analista | — | incidente atualizado |
| Incidentes | `POST /api/eng/incidentes/{id}/resolver` | Analista | — | incidente atualizado |
| Aprovações | `GET /api/eng/aprovacoes` | Analista | — | `aprovacoes[]` (apenas pendentes) |
| Aprovações | `POST /api/eng/aprovacoes` | Analista | `{ acao, papel_minimo }` | aprovação criada |
| Aprovações | `POST /api/eng/aprovacoes/{id}/decidir` | Analista | `{ aprovar, justificativa }` | aprovação decidida |
| Auditoria | `GET /api/eng/auditoria/verificar` | Gestor | — | `integra`, `entradas`, `primeira_invalida` |
| Auditoria | `GET /api/eng/auditoria/recentes` | Gestor | — | `eventos[]` (até 100) |
| Diagnóstico | `POST /api/alertas` | N1 | `{ equipamento, ip_origem, descricao_erro }` | `dados_enviados_nuvem`, `diagnostico_ia` |

## Exemplos de resposta

### `GET /api/eng/saude`

```json
{
  "servicos": [{
    "id": "alvo-2", "nome": "Servidor de imagens (PACS)", "host": "192.0.2.31", "porta": 104,
    "kind": "tcp", "ativo": true, "status": "down", "ultima_em": "2026-10-21T15:59:46Z",
    "latencia_ms": null, "alvo_pct": 99.5, "janela_dias": 7,
    "orcamento": { "completo": true, "cobertura_pct": 100, "restante_max_min": 8.9,
                   "status": "at_risk", "esgota_em": "2026-10-22T11:59:52Z" }
  }],
  "gerado_em": "2026-10-21T16:00:00Z", "limite": 500
}
```

| Campo | Valores e significado visual |
|---|---|
| `status` | `up` Disponível · `down` Indisponível · `unknown` Sem dados recentes · `inactive` Desativado |
| `orcamento` | `null` = "SLO não configurado" |
| `orcamento.completo` | `false` = mostrar "Até X min" e "Observação parcial" (é só um limite máximo) |
| `orcamento.status` | `healthy` · `at_risk` (≤ 25% restante) · `partial` · `breaching` (esgotado) |
| `orcamento.esgota_em` | data prevista de esgotamento ou `null` |

### `GET /api/eng/incidentes/resumo`

```json
{
  "incidentes": [{
    "id": "7f3c2a10-…-0001", "alvo_id": "alvo-4", "nome_alvo": "Switch do bloco cirúrgico",
    "tipo": "indisponibilidade", "severidade": "P1",
    "detectado_em": "2026-10-21T15:35:00Z", "reconhecido_em": null, "resolvido_em": null
  }],
  "metricas": {
    "MTTD": { "n": 0 },
    "MTTA": { "n": 2, "media_s": 300, "mediana_s": 300, "p95_s": 354 },
    "MTTR": { "n": 1, "media_s": 2400, "mediana_s": 2400, "p95_s": 2400 }
  },
  "limite": 500
}
```

O estado do incidente não vem pronto: ele é **derivado** dos campos. Com `resolvido_em` preenchido, o
incidente está Resolvido; com `reconhecido_em`, está Reconhecido; sem os dois, está Aberto.
Quando `n` é 0, a métrica não pode ser exibida como número.

### `GET /api/eng/aprovacoes`

```json
{ "aprovacoes": [{
  "id": "aprov-1", "acao": "Reiniciar a porta 12 do switch do bloco cirúrgico",
  "solicitante": "maria.analista", "criada_em": "2026-10-21T15:57:00Z",
  "expira_em": "2026-10-21T16:12:00Z", "papel_minimo": "analista_redes", "estado": "pending"
}] }
```

### `GET /api/eng/auditoria/verificar` e `/recentes`

```json
{ "integra": true, "primeira_invalida": null, "entradas": 128 }
```

```json
{ "eventos": [{ "id": 3, "ts": "2026-10-21T15:35:00Z", "ator": "coletor",
  "acao": "incident.created", "recurso": "7f3c2a10-…-0001" }] }
```

### `POST /api/alertas`

```json
{ "status": "Incidente Registrado",
  "dados_enviados_nuvem": "Equipamento: Switch | Erro: Perda de pacotes na sub-rede 192.0.2.0/24…",
  "diagnostico_ia": "Verifique o enlace físico e os contadores de erro da interface…" }
```

Se a IA falhar, `diagnostico_ia` traz "Diagnóstico de IA indisponível no momento. Tente novamente mais tarde."

## Como pedir um dado novo

1. Acrescente o campo em `src/mock/data.js` com o nome e o formato desejados (em português, `snake_case`, como os demais).
2. Use o campo na tela e confira no `npm run dev:mock`.
3. Abra uma issue "API: incluir campo X em /rota" com o exemplo JSON e o motivo. Vinny e Iohan implementam na API.
4. Até a API enviar o campo, a tela deve funcionar sem ele (mostrar "—" ou esconder o elemento).

Campos que **já existem na API mas o painel ainda não usa**: `orcamento.consumido_min`, `orcamento.total_min`,
`orcamento.disponibilidade_observada_pct`, `aprovacao.criada_em`, `auditoria.primeira_invalida`, além das rotas
`GET /api/eng/alvos/{id}/medicoes` e `/agregados` (séries para gráficos de latência). São boas oportunidades
para o design.
