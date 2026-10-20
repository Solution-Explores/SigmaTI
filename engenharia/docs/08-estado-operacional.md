> Atualização de 20/10/2026: [conferência das entregas integradas e pendências reais](../../doc/conferencia-issues-6-7-8-14.md). Descrições da primeira entrega abaixo preservam seu contexto histórico.

> Fundação integrada no PR #36. Para coleta opt-in, migração 003_collection, detector conectado e SSE, consulte [coleta e eventos](09-coleta-eventos.md).

# Persistência operacional (#7)

Incremento posterior ao PR #35. O núcleo `sigma_eng` não importa SQLAlchemy,
Psycopg ou FastAPI para gerenciar estado. `StateRepository` e
`MonitoringRepository` definem os contratos; `MemoryStateRepository` atende aos
testes puros de estado, e `PostgresOperationalStore` fornece persistência real.
`ApprovalService` e `RunbookRunner` recebem o repositório opcionalmente.

## Instalação e migração

Defina `SIGMA_DATABASE_URL` no ambiente do processo, conforme o
[guia de identidades](07-persistencia-identidades.md). Antes de iniciar a API:

```powershell
.venv/Scripts/python.exe -m alembic upgrade head
```

`002_operational` é posterior a `001_identity` e preserva usuários/sessões.
A API recusa banco com revisão antiga; nenhuma migração é executada
implicitamente ao importar a aplicação. O modo de arquivo de laboratório
continua disponível para as rotas anteriores; novas rotas operacionais retornam
503 nesse modo, em vez de aceitar dados em memória e perdê-los no reinício.

## Esquema

| Tabela | Conteúdo e garantias |
|---|---|
| alvos | UUID, nome, host, porta válida, tipo TCP/HTTP/HTTPS, ativo, criado_em UTC |
| medicoes | PK composta `(id, ts)`, FK alvo, sucesso, latência opcional; índice `(alvo_id, ts)`; partições mensais UTC |
| medicoes_agregadas | PK `(alvo_id, periodo, ts)`, contagem total/sucesso, soma/contagem/mínimo/máximo da latência |
| incidentes | UUID, alvo/tipo, severidade, detecção/reconhecimento/resolução UTC; índice único parcial por alvo/tipo quando não resolvido |
| aprovacoes | Documento, estado indexado e revisão para decisões concorrentes |
| execucoes_runbook | Snapshot de passos/resultados/variáveis, status, passo aguardando e passo em execução, com revisão |
| detectores | Configuração e aquecimento de EWMA/MAD, com revisão |
| slo | FK alvo, percentual e janela em dias validados |
| eventos_operacionais | ID crescente, instante UTC, ator, ação, recurso e metadados mínimos; confirma junto com a alteração |

Partições `medicoes_YYYYMM` são criadas sob lock transacional antes da inserção.
Nome e limites vêm exclusivamente de datetime UTC. A PK inclui `ts`, como exige
o [particionamento PostgreSQL](https://www.postgresql.org/docs/15/ddl-partitioning.html).
Não existe partição padrão escondendo dados fora do intervalo mensal.

## Ingestão e retenção

`record_measurement` grava amostra, atualiza agregados por minuto/hora e cria
incidente de disponibilidade na falha, na mesma transação. Falha no evento de
auditoria reverte tudo. O diagnóstico de IA não é necessário para persistir uma
falha. Repetir `(id, ts)` com os mesmos dados não incrementa contagens; reutilizar
com outros dados é conflito. O retry de falha retorna o incidente ativo existente.
A deduplicação da amostra vale enquanto o registro bruto é retido.

Ingestão e reconhecimento/resolução bloqueiam primeiro o alvo, depois o
incidente. Uma falha concorrente não cria dois incidentes ativos; depois da
resolução, uma nova amostra de falha pode abrir outro incidente. Reconhecer e
resolver são idempotentes. O repositório não resolve falhas automaticamente.

Manutenção explícita, no banco apontado pela variável de ambiente:

```powershell
.venv/Scripts/python.exe -m scripts.retain_measurements --days 30
```

`SIGMA_MEASUREMENT_RETENTION_DAYS` fornece o padrão, limitado a 1–3650 dias.
Dados brutos anteriores ao corte são removidos; partições completamente vencidas
são descartadas. Agregados minuto/hora permanecem. A média usa soma/contagem das
latências disponíveis, sem tratar falha sem latência como zero. Não há scheduler
de manutenção automático nesta etapa. Execute backup antes de manutenção em
banco operacional; o teste só usa bancos descartáveis.

## Recuperação segura

- Aprovações são relidas do repositório. Expiração persiste ao consultar/decidir;
  solicitante não decide sua própria aprovação. CAS impede sobrescrever uma
  decisão final feita por outro worker.
- Execuções gravam estado antes e depois de cada passo. `waiting_approval`
  preserva os resultados anteriores; retomar não os executa de novo.
- Se houver interrupção durante efeito externo, fica `running` com
  `passo_em_execucao`. Não é retomado automaticamente nem se promete execução
  exatamente uma vez de comandos externos. Exige conferência do operador.
- Snapshots EWMA/MAD preservam contagem, média/variância, sequência de anomalias
  ou janela MAD. A recuperação foi testada em outro processo Python.
- Eventos transacionais usam uma ordem de IDs serializada até o commit. Isso
  prepara leitura incremental sem ultrapassar eventos ainda não confirmados.
  O SSE é acrescentado na #8; os eventos não são uma cadeia criptográfica/âncora externa da issue #13.

## API e perfis

| Rotas em `/api/eng` | Perfil mínimo |
|---|---|
| GET alvos, medições, agregados, incidentes e SLO | suporte_n1 |
| POST alvos, reconhecer/resolver incidente, solicitar/decidir aprovação e configurar SLO | analista_redes |
| GET aprovações pendentes e execução por ID | analista_redes |
| GET auditoria/eventos, com after e limit | gestor_ti |

401 sem sessão, 403 por perfil, 409 por conflito de estado, 422 por entrada
inválida e 503 na indisponibilidade/configuração do banco. O ator vem da sessão.
A resposta da execução omite comandos, variáveis e saída bruta; expõe status
e resultados resumidos. Com coleta opt-in habilitada, alvos ativos passam a ser sondados pelo scheduler. Essas APIs não executam comandos arbitrários. A criação e
retomada de runbooks por interface ficam para #21/#22; os testes usam executor
simulado. O painel #15 já consome as rotas operacionais (PR #39).

## Aceite reproduzível

`python scripts/validate_postgres.py` aplica migrações e executa a regressão em
PostgreSQL 15 descartável no digest do Compose. O teste
`test_real_http_api_restart_preserves_session_and_pending_work` inicia Uvicorn,
faz login/cria alvo/aprovação via HTTP, encerra o processo e inicia outro,
confirmando o mesmo JWT, a aprovação pendente e a execução aguardando aprovação.
Nenhum comando externo ou IA real é executado. Também há testes de concorrência,
rollback, particionamento, agregação, retenção e detectores em outro processo.

Sondagem segura (#14) integrada no PR #37. A coleta/SSE (#8) está detalhada no guia 09; páginas #15 integradas no PR #39 e recuperação local #25 no PR #40; aceite em outra máquina permanece pendente.
