# Coleta contínua e eventos — issue #8

## Ativação

1. Configure SIGMA_DATABASE_URL e execute `python -m alembic upgrade head` (003_collection). O banco deve ser PostgreSQL migrado; não há fallback para memória.
2. Ative `SIGMA_COLLECTION_ENABLED=1` e escolha `SIGMA_COLLECTION_CONCURRENCY` entre 1 e 128 (padrão 32).
3. Configure SIGMA_PROBE_NETS conforme a política do ambiente. O padrão permite RFC1918/loopback; o experimento restringe a loopback.
4. Inicie a API. Uma conexão PostgreSQL dedicada mantém advisory lock 7417003. Outros processos ficam em espera e assumem quando o líder sai. Não compartilhe o banco entre instalações independentes que devam coletar separadamente.

A coleta é opt-in: o padrão 0 conserva o uso sob demanda. Não habilitar automaticamente em ambiente com alvos ainda não revisados.

## Alvos e ciclo

POST /api/eng/alvos, por Analista/Gestor, aceita nome, host, porta, kind e:

| Campo | Padrão | Limites |
|---|---|---|
| intervalo_s | 1 s | 0,1–3600 s |
| timeout_s | 1 s | 0,05–10 s |
| detector | ewma | ewma ou mad |

PATCH /api/eng/alvos/{id} com `{"ativo":false}` suspende novos ciclos após a próxima atualização (1 s); uma medição já em andamento pode terminar. Reativar usa true. Para trocar os demais parâmetros, cadastrar outro alvo nesta versão.

Há jitter uniforme de ±10% e fase inicial distribuída pelo intervalo. O experimento fixa SIGMA_COLLECTION_SEED=0; fora dele a semente é aleatória por processo. O ciclo usa relógio monotônico; registros usam UTC. O IP é resolvido e validado uma vez por medição, usando a proteção da #14; Host/SNI são preservados. Uma resposta DNS recusada registra erro/perda de coleta, sem afirmar indisponibilidade do serviço.

No máximo N trabalhos simultâneos, sem fila de sondas ou ciclos de recuperação acumulados. Persistência usa executor próprio de até 12 threads, sem disputar as threads padrão com autenticação/SSE/inventário; a quantidade pendente continua limitada pelos N trabalhos. No desligamento, gravações já iniciadas terminam antes de liberar a liderança. Sob saturação os ciclos vencidos são descartados e contabilizados. Timeout lógico após validar o destino gera medição de falha; timeout durante DNS ainda sem decisão de política é perda de coleta, sem falso incidente. O timeout mantém a vaga ocupada até a função bloqueante terminar; resultado tardio nunca gera uma segunda medição. Python não interrompe uma resolução DNS bloqueada numa thread. Assim a concorrência fica limitada, mas esgotar todas as vagas causa perdas observáveis. Parar a aplicação cancela tarefas e descarta resultados tardios; o processo pode precisar de encerramento forçado se o resolvedor do sistema não retornar.

O prazo inclui resolução e sondagem, mas persistência/entrega SSE dependem do banco e do consumidor. Um intervalo ou timeout alto não garante RF01 ≤5 s. A configuração padrão visa essa janela; a comprovação é do ambiente de ensaio descrito nas evidências.

## Estado e incidentes

Cada medição, agregados, snapshot do detector, incidente novo e seus eventos confirmam na mesma transação. A telemetria contínua fica registrada em medicoes; não duplica cada amostra em measurement.recorded no cursor global. Isso evita serializar a coleta inteira no lock de ordenação de eventos. Incidentes e operações administrativas conservam os eventos transacionais; o caminho de ingestão anterior sem detector mantém measurement.recorded. O detector aquece com latências de sondas disponíveis, é recuperado após reinício e não aprende com perda/timeout. EWMA/MAD não substituem diagnóstico: alarme de latência abre tipo latency; queda abre availability. Para HTTP/HTTPS, resposta ilegível ou HTTP 5xx também conta como indisponível; resposta 200 com apenas achado de segurança não vira falsa queda de disponibilidade. Há um incidente aberto por alvo/tipo, protegido por índice único, inclusive entre processos e após reinício. Reconhecimento/resolução continuam explícitos pelo operador; retorno da conectividade não resolve automaticamente o incidente.

A liderança reduz sondagem duplicada entre workers. Perda da conexão do líder suspende novos ciclos na próxima verificação; trabalhos já em transação podem confirmar. O índice único continua impedindo duplicação de incidente nesse intervalo. Não há promessa de uma única medição durante failover de rede.

GET /api/eng/coleta/status, por Analista/Gestor, retorna liderança, started/completed, missed/timeouts/errors, active/peak_active, max_lag_seconds e queued=0. São métricas do processo desde a inicialização, não histórico global persistido. O máximo de atraso não cresce para tentar recuperar uma fila antiga: ciclos atrasados são descartados.

## SSE e reconexão

GET /api/eng/eventos permite Suporte N1/Analista/Gestor. Enviar Bearer no cabeçalho Authorization. Parâmetros de URL são recusados; não colocar tokens em URL. Um cliente browser deve usar fetch com leitura de stream, pois EventSource nativo não permite esse cabeçalho.

O CORS permite Authorization/Last-Event-ID e PATCH somente para as origens configuradas; as demais continuam recusadas. Enviar `Last-Event-ID: <inteiro>` para reconectar a partir do último evento recebido. Sem cursor, reproduz o histórico de incidentes. Eventos possuem id monotônico persistido; polling de 200 ms lê somente registros confirmados. Não há fila volátil por cliente: leitura em lotes de até 100 e limite de 32 conexões por processo. Heartbeats não avançam cursor. Clientes lentos podem atrasar a própria entrega; não existe garantia de 5 s sob rede/consumidor travados.

Formato:

```text
id: 123
event: incidente
data: {"id":123,"ts":"...","acao":"incident.created","incidente_id":"...","alvo_id":"..."}

```

Só incident.created, incident.ack e incident.resolve são publicados, com projeção explícita sem ator/texto livre/aprovações/comandos. IDs de eventos ocultos podem deixar lacunas. A auditoria completa mantém o endpoint exclusivo do Gestor.

A sessão é revalidada a cada polling e antes de cada evento, inclusive após espera por consumidor lento. Expiração, revogação ou mudança de usuário/perfil encerra o stream com event session.closed. Falha do banco antes da abertura retorna 503; após headers envia stream.error com código genérico e encerra. Cache-Control no-store e X-Accel-Buffering no evitam cache/buffering comum; verificar o proxy real no ambiente de entrega.

## Reprodução E2/carga

Na branch de correção, o status expõe `probe_finished`, `probe_seconds_total`,
`max_probe_seconds`, `write_finished`, `write_seconds_total`, `max_write_seconds`
e `pending_writes`. Os tempos vão da submissão ao executor até a conclusão real
do future, incluindo espera por trabalhador e resultados tardios de sondas.
Os contadores incluem futures que falharam; `completed` continua contando
coletas persistidas com sucesso. Isso permite separar sonda e persistência sem
registrar hosts, saídas ou credenciais. Não constitui correção de capacidade.

> Revisão de 20/10/2026: houve reprovação posterior da carga em VM no mesmo
> host (`missed` de 150 para 200 na janela). CI anterior aprovado não constitui
> correção dessa reprodução. Veja [achados e critérios de retomada](../../doc/revisao-achados-base-2026-10-20.md).

```powershell
.venv/Scripts/python.exe scripts/validate_postgres.py --tests tests/test_collection_e2.py
```

O runner usa PostgreSQL 15 fixado no Compose. `--image` permite ensaio adicional explícito com outra versão, sem mudar o padrão. `scripts/validate_collection.py` também pode rodar com SIGMA_TEST_DATABASE_URL apontando para banco descartável. Ele cria schema aleatório próprio, migra, inicia/encerra Uvicorn, executa 30 quedas TCP com SSE real, mede 200 alvos lógicos em loopback e prova reinício/replay/logout. Remove só o schema criado, sem alterar o restante do banco.

Saídas em test-results/collection-e2.json e CSV; log local sem token/senha/chave. A carga usa um serviço TCP local para 200 alvos cadastrados, intervalo 2 s, 32 vagas e observação estável de 6 s após a primeira medição de todos. Não representa 200 hosts físicos nem validação hospitalar. A chegada do SSE ao cliente é medida; o painel #15 já foi integrado no PR #39 e tem ensaio de navegador próprio. Não confundir suas medições.

Conferência de aceite da #8 e limites: [matriz das issues de base](../../doc/conferencia-issues-6-7-8-14.md).
