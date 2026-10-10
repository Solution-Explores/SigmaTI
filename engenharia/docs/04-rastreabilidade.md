# 04 · Rastreabilidade requisito → módulo → verificação

| Requisito (README) | Meta | Módulo | Verificação automática | Verificação em campo |
|---|---|---|---|---|
| RF01 Alertas em tempo real | ≤ 5 s | `probe`, `anomaly`, `slo` | `test_detecta_degrau_com_pouco_atraso`, `test_alerta_page_em_queda_total_e_silencio_apos_recuperacao` | E2 (a fazer) |
| RF02 Captura/sonda | — | `probe` | `test_probe_*` (6 testes) | — |
| RF03 Diagnóstico por IA | ≤ 15 s (RNF04) | `runbooks` (ações sugeridas) | `test_dry_run_e_padrao_e_nao_executa` | E5 (a fazer) |
| RF04 Histórico de incidentes | — | `incidents` | `test_metricas_incidentes` | — |
| RF05 Privacidade (LGPD) | nada sai sem filtro | **fora deste núcleo** (ver pendências) | — | — |
| RF06 Relatórios (MTTR) | — | `incidents`, `slo` | `test_orcamento_99_9_em_30_dias`, `test_metricas_incidentes` | relatório n8n |
| RF07 Controle de acesso/perfis | — | `approvals`, `audit_chain` | `test_papel_insuficiente`, `test_autoaprovacao_proibida`, `test_adulteracao_detectada` | — |
| RNF06 Backup/persistência | sem perda | `audit_chain` (JSONL + fsync) | `test_persistencia_continua_a_cadeia` | restauração de backup |
| RNF07 Chaves/segurança de origem | 401/403 | `probe.is_target_allowed`, `audit_chain` (HMAC) | `test_alvo_permitido`, `test_hmac_impede_recalculo_sem_chave`, `test_probe_bloqueia_alvo_externo` | — |

## Propriedades de segurança testadas

| Propriedade | Teste |
|---|---|
| Sonda não alcança redes fora da allowlist | `test_alvo_permitido`, `test_probe_bloqueia_alvo_externo` |
| Adulteração/remoção/reordenação da trilha é detectada | `test_adulteracao_detectada`, `test_remocao_e_reordenacao_detectadas` |
| Sem a chave, a cadeia não pode ser refeita | `test_hmac_impede_recalculo_sem_chave` |
| Solicitante não aprova a própria ação | `test_autoaprovacao_proibida` |
| Aprovação vencida não pode ser concedida | `test_aprovacao_vencida_nao_pode_ser_aprovada` |
| Decisão final é imutável | `test_decisao_final_e_imutavel` |
| Runbook não executa fora da allowlist | `test_allowlist` |
| Variáveis não injetam argumentos/comandos | `test_injecao_em_variavel_bloqueada` (7 casos) |
| Nenhum passo roda se algum for inválido | `test_valida_tudo_antes_de_executar` |
| Sem shell: metacaracteres são literais | `test_executor_real_sem_shell` |
