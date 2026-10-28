# Conferência de #6, #7, #8 e #14 — entregas integradas

20/10/2026 (UTC−4). Base examinada: **develop@8cb1e23b0e83066e52d3f81dd7ef05ce82dfc93c**. Escopo: ler pedido completo, comparar código/testes/evidências e registrar pendências. Não alterar implementação nem encerrar issues nesta conferência. PR41 do planejamento de VM ainda não está integrado e não foi tratado como evidência de produto.

> **Nota de 28/10/2026 (atualizaÃ§Ã£o da branch).** Este registro vale para a base `8cb1e23`. Na `develop` atual (`b0bf3ac`), o script `docs/specs/019-conferencia-issues-base/reproduzir-auditoria.py` jÃ¡ nÃ£o reproduz a lacuna A1: a primeira asserÃ§Ã£o falha porque `disk_integrity` volta `True` e `cached_entries` volta 3. Os demais achados nÃ£o foram reavaliados.

## Resultado

| Issue | Conclusão no escopo original | O que realmente falta |
|---|---|---|
| #6 — autenticação/RBAC | [Certo] PostgreSQL/Argon2id, JWT com expiração/revogação, limite de login, dependências e matrizes da API implementados. **Entrega ainda tem lacuna confirmada na auditoria.** | Serializar gravação da trilha entre instâncias/processos; verificar o arquivo atual em vez de snapshot antigo; regressões desses casos. Distinguir RBAC dos endpoints da implementação funcional de serviços externos. |
| #7 — persistência | [Certo] Proposta e três critérios de aceite cobertos por código/testes PostgreSQL integrados. | Nenhuma implementação faltante identificada nos critérios originais. Atualizar registro/aceite e referências documentais antigas. Backup externo e interface de runbooks são outras issues. |
| #8 — coleta/SSE | [Certo] Três critérios comprovados no laboratório descrito:30quedas, reinício e200alvos lógicos. | Nenhuma implementação faltante identificada nesses critérios locais. Registrar aceite; calibração/capacidade de rede real continuam fora da evidência. |
| #14 — IP validado | [Certo] Ambos os critérios cobertos: DNS alternante e documentação de riscos. | Nenhuma implementação faltante identificada. Atualizar status editorial; confiança PKI não integra esta correção. |

Todas permanecem abertas nesta conferência. “Critérios cobertos” não é homologação hospitalar nem aprovação humana independente. A recomendação de encerramento de #7/#8/#14 depende da revisão desta matriz, não de novos recursos inventados.

## Base integrada e CI

| Entrega | PR e merge confirmados no GitHub |
|---|---|
| Identidades persistentes | [#35](https://github.com/Solution-Explores/SigmaTI/pull/35),27d2b552d361deceb3650ba2a47ead959b0ab6bd |
| Estado operacional | [#36](https://github.com/Solution-Explores/SigmaTI/pull/36),51c21f778912f3f85661735e1dd8e8e415d786bc |
| Sondagem fixada | [#37](https://github.com/Solution-Explores/SigmaTI/pull/37),c288afd363f772d337139551534cba76b1175a7b |
| Scheduler/SSE | [#38](https://github.com/Solution-Explores/SigmaTI/pull/38),98b129b90ab6006435a5a11bd56011d40abf2910 |
| Painel consumidor | [#39](https://github.com/Solution-Explores/SigmaTI/pull/39),f3f6edea9e7691868f2fe659e091a9c002ee8cc7 |

CI do commit integrado examinado: [API/pacote/PostgreSQL/recuperação](https://github.com/Solution-Explores/SigmaTI/actions/runs/39433266986) e [infraestrutura](https://github.com/Solution-Explores/SigmaTI/actions/runs/39433267189), todos os cinco checks aprovados. Job PostgreSQL:467aprovados em148,48s, sem falhas/ignorados. A contagem foi consultada nos logs após o merge40; não é nova execução de467testes nesta conferência. CI verde não cobre automaticamente as lacunas recém-reproduzidas abaixo.

## #6 — análise do pedido completo

| Pedido/critério | Implementação e evidência | Resultado |
|---|---|---|
| Usuários PostgreSQL, senha Argon2id e três papéis | auth.py, persistence/identity.py, migração001_identity; testes test_postgres_identity.py (bootstrap, rehash, concorrência, mudança de identidade) | Atendido no modo PostgreSQL; arquivo/PBKDF2 é legado explícito. |
| JWT de sessão com expiração; nunca devolver chave permanente | criar_token_sessao/decodificar_token_sessao; test_login_sucesso_retorna_jwt_e_nao_expoe_chave_permanente, test_token_expirado_rejeitado_com_401, test_expired_session_and_wrong_password | Atendido. Sessões/revogações sobrevivem a reinício quando mantido o segredo JWT. |
| exige_papel e401/403 para matriz | TestMatrizPermissoesRBAC (15rotas ×4condições); test_entire_operational_rbac_matrix_against_postgres; test_panel_read_routes_follow_role_matrix; testes de coleta/SSE | Atendido na fronteira das rotas implementadas. Não equivale a proteção do n8n fora da API. |
| Testes automatizados da matriz | Arquivos acima, executados no CI integrado | Atendido no escopo da matriz da API; suites separadas para rotas legadas/operacionais/painel. |
| Limite de tentativas | LoginRateLimiter e teste de5falhas/429, parâmetros validados | Implementado por processo. Distribuição entre workers/persistência do contador não foram exigidas no pedido original: limite operacional, não novo bloqueador inventado. |
| Login/logout na AuditChain | routers/auth.py chama obter_auditor/registrar; fluxo sequencial testado | Registro existe, mas integridade/visibilidade entre instâncias falham; corrigir antes de aceitar integralmente a auditoria da entrega. |

### Lacunas confirmadas: A1 e A2

**A1 — gravação por múltiplas instâncias pode invalidar a cadeia.** `obter_auditor()` cria uma AuditChain a cada chamada. Cada objeto carrega uma lista própria e possui um threading.Lock próprio. Duas instâncias obtidas antes das gravações usam a mesma sequência/hash anterior; o lock de uma não coordena a outra.

Reprodução determinística em arquivo temporário: seed→instânciasA/B→Aregistra login→Bregistra logout. Arquivo final:3entradas; verificação fresca:false, primeira inválidaíndice2. InstânciaA ainda relata2entradas e íntegra. Não é necessário inventar falha DNS, atacar rede ou alterar banco para reproduzir. [Provável] Logins concorrentes podem atingir essa intercalação; a reprodução confirma a falha do escritor compartilhado, não mede a frequência em tráfego real.

**A2 — GET auditoria/verificar lê snapshot desatualizado.** `main.py` constrói engineering_audit ao importar; create_router captura o objeto e usa sua lista em memória. Em API real(TestClient, modo laboratório, arquivo fictício), login200gravou1entrada, mas GET `/api/eng/auditoria/verificar` retornou200com `entradas:0, integra:true`. A cadeia no disco estava íntegra; o problema comprovado é omissão do evento novo. O mesmo código de auditoria é compartilhado pelo modo PostgreSQL; o experimento de endpoint não foi anunciado como ensaio com banco.

Correção a fazer em outra entrega:

1. Coordenar leitura do último hash+append+fsync entre todos os escritores/processos do arquivo, com fonte canônica atualizada. Um singleton apenas em um processo não resolve múltiplos processos.
2. Fazer a verificação refletir o arquivo corrente com leitura coerente; incluir os eventos auth já confirmados e detectar adulterações posteriores à inicialização.
3. Acrescentar regressões de instâncias concorrentes/processos e login→verificação atual; manter testes de sequência, reinício e sigilo. Regra de tratamento de indisponibilidade da auditoria deve ficar explícita.

Reprodução versionada, somente dados fictícios:

```powershell
.venv/Scripts/python.exe docs/specs/019-conferencia-issues-base/reproduzir-auditoria.py
```

Saída0com `gaps_reproduced_not_fixed` significa que as lacunas foram reproduzidas, **não** que a correção passou. O script não altera código nem arquivos operacionais; usa TemporaryDirectory e não publica tokens/senhas/chaves. Nesta conferência ambos os cenários reproduziram os resultados descritos.

A2 também afeta a informação de integridade exibida pelo painel #15, que consulta esse endpoint. Não demonstra falha do verificador fresco usado no backup/restore.

A1/A2 são consistência básica da trilha; não confundir com âncora externa/rotação criptográfica da #13. Eventos PostgreSQL transacionais são armazenamento separado e não foram demonstrados corrompidos por este diagnóstico.

### Fronteira de permissões versus funcionalidades

`/api/pacotes` e `/api/relatorios` devolvem listas vazias; `/api/chaves/rotacao` apenas devolve o texto chaves_rotacionadas, sem rotacionar; `/api/n8n/acesso` devolve URL/status, sem impor RBAC no serviço n8n. Os testes de401/403dessas rotas comprovam autorização da API, não essas funcionalidades. Rotação/cofre pertencem #13/#23, relatórios #16 e integração de serviços precisa de aceite próprio. Não expandir silenciosamente #6 para implementar todo o backlog, nem afirmar que essas linhas do produto já funcionam.

## #7 — persistência

| Pedido/critério | Evidência integrada | Resultado |
|---|---|---|
| Alembic: alvos, medições, incidentes, aprovações, execuções, SLO | migrations/versions, persistence/operational_models.py; test_schema_and_monthly_partition | Atendido. |
| Índice(alvo_id,ts) e partição mensal | test_schema_and_monthly_partition, particionamento sob lock em record_measurement | Atendido. |
| Protocol/núcleo puro/adaptador de memória | engenharia/sigma_eng/state.py, MemoryStateRepository, injeção em ApprovalService/RunbookRunner e instalação independente testada | Atendido para estado do núcleo; banco fica no adaptador persistence. |
| Retenção configurável/downsampling minuto/hora | scripts/retain_measurements.py; test_downsampling_and_repeated_measurement e test_retention_preserves_aggregates_and_drops_old_partition | Atendido. Execução manual é explícita; agendamento automático não foi exigido na #7. |
| API reiniciada preserva pendentes/waiting_approval | test_real_http_api_restart_preserves_session_and_pending_work encerra e inicia Uvicorn; test_execution_waiting_approval_recovers_without_repeating_steps | Atendido com PostgreSQL real e executor simulado, sem afirmar execução exatamente uma vez de efeitos externos. |
| Repositório PostgreSQL real no CI | job test-postgres e testes de transação/concorrência/rollback/SLO/detector | Atendido. |
| Documentar esquema em engenharia/docs | 07-persistencia-identidades.md,08-estado-operacional.md,09-coleta-eventos.md | Atendido; trechos antigos devem ser lidos como históricos. |

Pendência original identificada: **nenhuma**. APIs de criação/retomada de runbook e biblioteca operacional são #21/#22; restauração em outra máquina é #25. Não impedir o aceite de persistência exigindo essas outras entregas. Interrupção de efeito externo fica em running para conferência deliberada, conforme documentação.

## #8 — coleta e SSE

| Pedido/critério | Evidência integrada | Resultado |
|---|---|---|
| Scheduler por alvo, intervalo/jitter±10%, EWMA/MAD persistidos | engenharia/sigma_eng/scheduler.py, persistence/operational.py,003_collection; testes scheduler/collection | Atendido; executor limitado equivale ao offload proposto, sem depender do executor padrão. |
| Contrapressão/timeout/métricas de atraso/perdas | vagas retidas até fim da thread, descarte de ciclos atrasados, missed/timeouts/max_lag_seconds; testes de saturação/failover | Atendido. DNS travado não é cancelado à força; ocupação é limitada. |
| Queda→SSE≤5s pelo E2 | test_e2_thirty_failures_200_targets_restart_and_sse e scripts/validate_collection.py:30quedas reais, asserção de100%≤5s | Atendido no loopback descrito. |
| Reinício sem duplicar incidente aberto | mesmo experimento reinicia Uvicorn, exige1incidente ativo com o mesmo ID; índice único e testes concorrentes | Atendido. |
| Carga≥200sem acumular atraso |200alvos lógicos, intervalo2s, janela estável6s; fila0, pico≤32, atraso máximo<0,5s, sem novas perdas/erros, mínimo2medições por alvo na janela | Atendido nessa duração/configuração, não prova carga indefinida. |

Pendência original identificada: **nenhuma no laboratório medido**. #15 já integra o consumidor de tela e tem teste de renderização≤5s para uma falha sintética, distinto do E2 de30quedas até o cliente SSE. Não trocar a medição do cliente por uma alegação de30renderizações. Hospital/200equipamentos físicos, proxy real e longas durações são limites de validade, não resultados produzidos aqui. A auditoria JSONL A1/A2 não invalida automaticamente os eventos SSE persistidos em PostgreSQL: são caminhos diferentes.

## #14 — conexão ao IP validado

| Pedido/critério | Evidência integrada | Resultado |
|---|---|---|
| Resolver uma vez e conectar IP, preservando Host/SNI, também HTTPS | resolve_target→probe_many/probe_service→_connect_ip; destino numérico IPv4/IPv6 | Atendido. |
| Resolvedor alternante recusa IP não autorizado | test_alternating_dns_never_connects_to_second_answer parametrizado TCP/HTTP/HTTPS:primeira série sóIPpermitido, nova operação com resposta externa recusada antes do conector | Atendido. |
| Não resolver de novo no caminho do socket | test_numeric_socket_path_has_no_second_resolver e HTTP real com redirect externo não seguido | Atendido. |
| Riscos05-seguranca-e-pendencias atualizados | seção TOCTOU/rebinding e Limites da correção#14 | Atendido; status editorial ainda dizia para revisão. |

Pendência original identificada: **nenhuma**. TLS usa contexto/socket simulado para observar SNI e inspeção de certificado; não comprova autenticação PKI real, nem foi esse o critério da #14. O primeiro IP autorizado sem fallback e redes permitidas são decisões documentadas. Auditoria #13 e calibração não são parte desta correção.

## Escopo do cartão #14 no Trello

O cartão “Conectar sondas ao IP validado e auditar operações” reúne mais que a issue #14. A auditoria transacional PostgreSQL foi integrada no PR #36, mas âncora/rotação da #13 seguem pendentes; A1/A2 da trilha JSONL foram confirmados nesta conferência. Portanto, critérios originais de #14 atendidos **não** significam concluir todo o escopo ampliado desse cartão. Preservar essa distinção no quadro.

## Documentação histórica que exige atenção

README e guias07/08 ainda têm frases de fases anteriores: usuários/sessões em memória, persistência operacional futura, detectores ainda não conectados, painel ainda não consumidor. Essas frases não representavam o modo PostgreSQL atual; README e guias receberam atualização/pointer nesta conferência. Os specs históricos preservam o estado da etapa e não devem ser reescritos como se contivessem o CI posterior. Esta matriz é a consolidação atual e recebe links dos guias.

## Próximos passos objetivos

1. Corrigir A1/A2 em branch própria e testar concorrência/leitura atual antes de recomendar encerramento integral de #6.
2. Revisar esta conferência e registrar aceite de #7/#8/#14; não foi encontrada exigência original faltante de implementação.
3. Manter separado o backlog funcional de chaves, relatórios, runbooks, âncora e ensaios externos. Não fechar #25 nem prometer homologação por causa desta conferência.

Nenhuma issue é fechada automaticamente. Revisão técnica Codex; sem revisor humano independente atribuído.
