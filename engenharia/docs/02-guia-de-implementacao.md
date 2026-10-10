# 02 · Guia de implementação

Roteiro para levar o núcleo do protótipo à operação. Cada fase termina com um critério de aceite verificável.

## Fase 0 · Pré-requisitos (≈ 1 h)

1. Python 3.10+ (o ambiente de desenvolvimento usou 3.14).
2. Resolver os bloqueadores do repositório descritos em [05](05-seguranca-e-pendencias.md#bloqueadores-do-repositório), principalmente o `docker-compose.yml` com marcadores de conflito de merge.
3. Rodar a suíte:
   ```bash
   cd engenharia && python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt && pytest -q
   ```
   **Aceite:** 58 testes passando.

## Fase 1 · Integrar a API ao SIGMA (≈ 2 h)

No `main.py` do SIGMA:

```python
from engenharia.sigma_eng.api import router as eng_router
app.include_router(eng_router)
```

> `engenharia/` não tem `__init__.py` (pacote *namespace*). Se preferir, instale como pacote editável (issue "Empacotar sigma_eng") e importe `sigma_eng.api`.

Configure por variável de ambiente (nunca no código):

| Variável | Função | Exemplo |
|---|---|---|
| `SIGMA_AUDIT_PATH` | Arquivo da trilha | `/var/lib/sigma/audit.jsonl` (volume persistente) |
| `SIGMA_AUDIT_KEY` | Chave HMAC da trilha | gerar com `openssl rand -hex 32` |
| `SIGMA_PROBE_NETS` | Redes que a sonda pode alcançar | `10.20.0.0/16,10.30.0.0/16` |

**Aceite:** `GET /api/eng/auditoria/verificar` → `{"integra": true}`; `POST /api/eng/probe` para IP público → `403`.

## Fase 2 · Sondagem contínua (≈ 1 dia)

Hoje a sonda só roda sob demanda. Para vigilância contínua:

1. Tabela `alvos(id, nome, host, porta, tipo, intervalo_s, habilitado)` e `medicoes(alvo_id, ts, status, latencia_ms)` no PostgreSQL já existente (índice em `(alvo_id, ts)`; particionamento mensal se passar de ~10⁷ linhas).
2. Um *scheduler* assíncrono que, para cada alvo, chama `asyncio.to_thread(probe_service, ...)` no intervalo configurado, com *jitter* aleatório de ±10% para não sincronizar rajadas.
3. Cada medição alimenta um `EwmaDetector` ou `MadDetector` **por alvo**. Quando houver alarme, abrir incidente e emitir o evento SSE (RF01).
4. Persistir `inicio_real` apenas em testes com falha injetada; em produção ele é preenchido na análise pós-incidente.

**Aceite:** com um alvo desligado de propósito, o painel mostra o alerta em ≤ 5 s (experimento E2).

## Fase 3 · SLO e relatórios (≈ 1 dia)

1. Cadastrar um `SLO` por serviço crítico (ex.: prontuário eletrônico 99,9%/30 dias).
2. Alimentar `error_budget` e `burn_alerts` com os intervalos de indisponibilidade derivados dos incidentes (`Incidente.intervalo_indisponivel()`).
3. No n8n, um fluxo semanal chama `POST /api/eng/slo/avaliar` e `POST /api/eng/incidentes/metricas` e envia o relatório à coordenação (RF06).
4. Regra de roteamento: alerta `page` → notificação imediata; `ticket` → fila do dia seguinte.

**Aceite:** relatório semanal gerado automaticamente com MTTD/MTTA/MTTR e situação do orçamento.

## Fase 4 · Resposta controlada (≈ 2 dias)

1. Escrever runbooks em Markdown (`sigma:step`), por exemplo "Switch sem resposta" e "Certificado vencendo". Versionar em `engenharia/runbooks/`.
2. Definir a **allowlist** mínima (ex.: `ping`, `traceroute`, `nslookup`, `curl`). Comandos de alteração (`systemctl restart`) só com `requires_approval=true`.
3. Fluxo: `RunbookRunner.executar(..., dry_run=True)` mostra o que seria feito → o técnico confirma → `dry_run=False` → no passo com aprovação, o runner para em `waiting_approval` → `ApprovalService.solicitar("runbook:<exec>:<passo>", ...)` → o gestor aprova → `retomar`.
4. Passar a **mesma** `AuditChain` ao `ApprovalService`, para que solicitação, decisão e expiração entrem na trilha.

**Aceite:** tentativa de aprovar a própria solicitação e de executar binário fora da allowlist são recusadas e auditadas.

## Fase 5 · Frontend (≈ 2 dias)

Páginas sugeridas no `sigma-frontend` (React), inspiradas em painéis de SRE (saúde de serviços, incidentes, aprovações, auditoria):

| Página | Endpoint | Conteúdo |
|---|---|---|
| Saúde dos serviços | `/api/eng/slo/avaliar` | Cartões com status, orçamento restante, projeção de esgotamento |
| Incidentes | `/api/eng/incidentes/metricas` | MTTD/MTTA/MTTR com mediana e p95 |
| Aprovações | (a expor) | Fila de pendentes, aprovar/rejeitar com justificativa |
| Auditoria | `/api/eng/auditoria/verificar` | Selo "cadeia íntegra" e lista de eventos |

Autenticação e perfis (RF07) devem proteger **todas** as rotas `/api/eng/*` antes de qualquer uso fora do laboratório (ver pendências).

## Fase 6 · Validação

Executar os experimentos E1–E5 de [03](03-metodologia-experimental.md) no ambiente do hospital (ou em laboratório que o reproduza) e anexar os CSVs ao TCC.

## Checklist de produção

- [ ] `SIGMA_AUDIT_KEY` definida e guardada fora do repositório
- [ ] `SIGMA_PROBE_NETS` limitada às VLANs reais
- [ ] Rotas `/api/eng/*` atrás de autenticação e perfil
- [ ] Backup do arquivo de auditoria junto com o do PostgreSQL
- [ ] Allowlist de runbooks revisada pelo Gestor de TI
- [ ] Rotina de verificação diária da cadeia (alerta se `integra=false`)
