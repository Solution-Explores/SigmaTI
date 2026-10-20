# Issue #8 — coleta contínua e SSE

## Base e integração autorizada

O usuário autorizou o próximo passo depois do plano explícito de integrar #36/#37 e desenvolver #8. Conferidos heads, destino develop e os quatro checks aprovados antes de cada merge, com proteção pelo SHA esperado:

- PR #36: head 86375d9; merge 51c21f778912f3f85661735e1dd8e8e415d786bc.
- PR #37: head d42edac; merge c288afd363f772d337139551534cba76b1175a7b.
- CI da base combinada: https://github.com/Solution-Explores/SigmaTI/actions/runs/39349464975 e https://github.com/Solution-Explores/SigmaTI/actions/runs/39349465078, ambos aprovados.

Trabalho #8 em feature/8-coleta-sse, saindo da develop integrada. Revisão técnica Codex, sem revisão independente atribuída. Nenhuma issue encerrada automaticamente; main preservada.

## Entrega

Scheduler opt-in no lifespan, fase distribuída e jitter ±10%, configuração por alvo, limite de trabalhos, descarte de ciclos perdidos, prazo lógico e retenção da vaga até terminar uma thread atrasada. DNS sem decisão de política não produz falso incidente. Persistência tem executor próprio limitado, sem bloquear o relógio nem disputar threads padrão com autenticação/SSE. Liderança por advisory lock PostgreSQL, com drenagem das gravações antes de liberar o lock no desligamento.

Migração 003_collection acrescenta intervalo/timeout/detector e índice parcial de incidentes para o SSE. Medição, agregados, snapshot EWMA/MAD, incidente e eventos de incidente confirmam atomicamente. Reinício recupera o detector e mantém incidente ativo único por alvo/tipo. Telemetria contínua permanece em medicoes sem duplicar um measurement.recorded por amostra no cursor global; operações administrativas e incidentes permanecem auditados. Ingestão anterior conserva seu evento.

GET /api/eng/eventos usa Bearer no cabeçalho, cursor Last-Event-ID persistido, projeção sem ator/texto livre/comandos e revalidação antes de cada evento. Expiração/revogação encerra o stream; erro do banco é genérico. Limites por processo de 32 clientes e 100 eventos/lote. Controle de alvos ativos e métricas com RBAC.

Guia: engenharia/docs/09-coleta-eventos.md. Metodologia E2 e riscos atualizados. A ligação com a tela fica na #15; sem IA externa ou comando arbitrário neste fluxo.

## Verificação local — PostgreSQL 17 / Windows / loopback

```powershell
.venv/Scripts/python.exe -m pytest engenharia/tests/test_scheduler.py tests/test_event_stream.py -q -p no:cacheprovider
.venv/Scripts/python.exe scripts/validate_postgres.py --image postgres:17-bookworm@sha256:3645570cccdfa447589da9f57dd740faa29b30938e861289a5574b6ca6b03826 --tests "tests/test_postgres_collection.py tests/test_postgres_operational.py tests/test_collection_e2.py"
```

- 10 testes de scheduler/stream aprovados em 7,21 s; incluem timeout com vaga retida, DNS bloqueado, saturação sem fila, inventário lento, erro de persistência, drenagem antes de liberar liderança, revogação entre eventos e falha segura do banco.
- 25 testes PostgreSQL/E2 aprovados em 90,32 s. Atomicidade/rollback, aquecimento recuperado, incidente único concorrente, lock exclusivo, RBAC e replay, mais toda a regressão operacional anterior.
- pip check sem dependências quebradas; git diff --check aprovado.

### E2: falha → SSE real, 30 repetições, semente 0

| Medida | Resultado local |
|---|---:|
| Mediana | 0,690 s |
| p95 (interpolação linear, recalculado do CSV) | 0,831 s |
| Máximo | 0,869 s |
| Proporção ≤5 s | 30/30 (100%) |

O script comprova sonda disponível antes da injeção e registra t0 antes de fechar o listener. t1 é a recepção do evento em cliente HTTP/SSE real. Reinicia Uvicorn, reutiliza a sessão persistida, mantém o mesmo incidente aberto, reconecta com Last-Event-ID e encerra o stream após logout.

### Carga: 200 alvos lógicos em um serviço TCP local

Intervalo 2 s, timeout 0,5 s, concorrência máxima 32, janela estável de 6 s após a primeira medição de todos. Sem mock de sonda, banco ou SSE.

- completed: 596 → 1198 (602 confirmações durante a janela).
- missed: 200 → 200 (zero novas perdas na janela); os descartes anteriores pertencem às quedas sintéticas de intervalo curto.
- errors: 0 → 0; timeouts: 62 → 62 (sem novos timeouts na carga).
- atraso máximo: 0,0319 s; fila de sondas: 0; pico global de trabalhos: 32.
- 1231 medições dos alvos de carga observadas ao final (inclui aquecimento e consultas após a janela).

Após essa execução, o ensaio foi reforçado para exigir pelo menos duas medições de CADA alvo dentro da janela e delta mínimo de 400 confirmações. O CI do head final validará também essas condições; os números locais acima descrevem a execução aprovada anterior a esse reforço, sem inventar contagens por alvo que ela não exportava.

## Achados corrigidos durante a medição

A primeira carga revelou atraso ao aguardar inventário no laço; atualização foi desacoplada. Atraso caiu para dezenas de milissegundos, mas persistiam perdas. Foram reduzidos round-trips, agrupados agregados minuto/hora e removida duplicação de telemetria em eventos de domínio. O perfil revelou concorrência limitada pelo executor padrão de oito threads compartilhado com outros serviços neste host. Executor de persistência próprio resolveu a carga mantida em 200 alvos/2 s, sem relaxar o limite de atraso ou a exigência de zero novas perdas.

## Limites

Não comprova 200 equipamentos físicos, rede hospitalar, DROP/firewall, renderização no painel ou cenário de múltiplos proxies. DNS bloqueado não pode ser interrompido em thread Python: limita-se a ocupação e descartam-se resultados tardios. Persistência/consumidor lento ainda podem atrasar o evento; calibrar intervalo/timeout/capacidade no ambiente real. Failover de conexão pode concluir gravações já iniciadas; unicidade do incidente continua protegida no banco. Sem âncora/rotação criptográfica #13, backup/restore #25 ou fechamento automático de issue.

CSV/JSON do experimento são produzidos em test-results e publicados no artefato postgres-test-results do CI. Estado final do CI será registrado no PR após conferência do SHA e logs.


## Revisão da classificação HTTP

Na revisão foi corrigida a classificação de uma resposta 5xx como disponível apenas porque o socket abriu. A coleta agora considera HTTP ilegível/5xx como falha e distingue achado de segurança em HTTP 200 de indisponibilidade. Três casos de regressão acrescentados ao grupo scheduler/stream; a medição E2 local acima continua sendo da execução anterior a esta correção HTTP, com alvos TCP. O CI do head final revalida todo o conjunto.


## Revisão de contrapressão durante failover

Um teste com liderança alternante e gravação bloqueada reproduziu seis novas sondas para limite de dois trabalhos: cancelar o wrapper liberava a vaga enquanto a gravação protegida ainda aguardava. Corrigido mantendo a reserva até terminar, suspendendo novos ciclos sem liderança e descartando resultado de sonda se a liderança já se perdeu antes da gravação. Transações já iniciadas continuam sendo drenadas. A regressão passa sem ampliar a fila, inclusive quando a liderança oscila repetidamente.
