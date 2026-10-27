**Não bloqueia a demo.** Acompanhamento posterior à demonstração; não equivale a dispensar o aceite de 23/10.

## Contexto e evidências
Três testes falharam intermitentemente nas rodadas locais `rodada-2026-10-22`, `rodada-2026-10-22b` e `rodada-2026-10-22c` (Ubuntu 24.04, 4 vCPU, 4 GiB). Os artefatos não estão no repositório. Não são regressões novas demonstradas dos PRs #43/#44: provedor e sonda falharam isolados na baseline; DNS já falhou na suíte da baseline.

| Teste | Candidato isolado, rodada 2 | Baseline, rodada 3 |
|---|---:|---:|
| `tests/test_provider.py::test_real_budget_cancels_slow_provider_within_15_seconds` | 7/10 | 9/10 |
| `engenharia/tests/test_stats_probe.py::test_probe_many_perda_e_jitter` | 9/10 | 5/10 |
| `engenharia/tests/test_scheduler.py::test_dns_timeout_before_policy_does_not_create_false_incident` | 10/10 | não repetido isolado; falhou na suíte da rodada 1 |

Os arquivos `main.py`, `tests/test_provider.py`, `engenharia/tests/test_stats_probe.py` e `engenharia/sigma_eng/probe.py` são idênticos entre `8cb1e23` e `ddd4840`.

## Diagnóstico
- **Sonda: causa confirmada.** `accept()` em outra thread aceitou a mesma conexão nova 1,5 ms após `close()`, comprovado pelo cruzamento de portas. Original **26/30**; com `shutdown(socket.SHUT_RDWR)` antes do fechamento, **30/30**. Correção no branch remoto [fix/teste-sonda-instavel](https://github.com/Solution-Explores/SigmaTI/tree/fix/teste-sonda-instavel), commit `3cca38d`, ainda sem PR.
- **Provedor:** timer de 14 s atrasou até **1,263 s antes do cancelamento**. Rota/dependências ≤0,11 s, anonimização ≤1,5 ms, cancelamento/limpeza <1 ms. Debug **10/10**, instrumentado **9/10**. Zero avisos de callback lento **não prova ausência de bloqueio**. Causa específica entre selector, scheduler e hipervisor não isolada.
- **Risco RNF04:** prazo de 14 s deixa apenas 1 s até a meta de 15 s. Decidir, com justificativa e medição, se reduz o prazo interno para 13 s ou registra a margem como limite. Não aumentar a asserção para obter aprovação.
- **DNS:** falha na suíte, **10/10** isolado; causalidade ainda inconclusiva. Avaliar sincronização por evento em vez do `sleep(0.25)` fixo, sem presumir que carga é a causa.

## Próximo passo
Responsável: @Vinny1313. Revisor independente: @iohanjheremy. Triagem e decisão técnica propostas para **27/10/2026**, após a demo; a data é de triagem, não promessa de correção de todos os casos.

## Critérios de aceite
- [ ] 30/30 execuções isoladas na VM para cada teste, sem afrouxar limites.
- [ ] Provedor respeita o orçamento total de 15 s medido de ponta a ponta.
- [ ] Nenhum limite de asserção alterado sem justificativa registrada.
- [ ] PR da correção da sonda revisado; registros separam fixture, aplicação e ambiente.

Refs #4, #6, #8 e #11; não encerra nem substitui os critérios dessas issues.
