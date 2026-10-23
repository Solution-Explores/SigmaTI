# Rascunho de issue: testes instáveis por tempo (abrir depois da rodada 3 da VM)

**Título:** Testes instáveis: timeout do provedor de IA, sonda após fechamento e timeout de DNS

## Contexto
Nas rodadas de VM de 21/10 (`validacao-vm/rodada-2026-10-22` e `-22b`; Ubuntu 24.04, 4 vCPU, 4 GiB), três testes falharam de forma intermitente. Os PRs #43 e #44 não alteraram esses testes nem o código que eles testam: `git diff 8cb1e23..ddd4840` está vazio em `main.py`, `tests/test_provider.py`, `engenharia/tests/test_stats_probe.py` e `engenharia/sigma_eng/probe.py`.

| Teste | Isolado (rodada 2) | Observação |
|---|---|---|
| `tests/test_provider.py::test_real_budget_cancels_slow_provider_within_15_seconds` | 7/10 | Timeout configurado de 14 s; medições de 15,2 a 16,3 s. O log interno de `consultar_ia` registrou 16.023 ms. |
| `engenharia/tests/test_stats_probe.py::test_probe_many_perda_e_jitter` | 9/10 | Perda de 66,67% em vez de 100% |
| `engenharia/tests/test_scheduler.py::test_dns_timeout_before_policy_does_not_create_false_incident` | 10/10 | Falha só na suíte completa, com a VM ocupada |

## Causas (rodada 3, `validacao-vm/rodada-2026-10-22c`, 471 hashes conferidos)
A instabilidade **já existia antes dos PRs**. Na linha de base `8cb1e23`, o provedor passou 9/10 e a sonda 5/10. Os quatro arquivos envolvidos são idênticos, byte a byte, entre `8cb1e23` e `ddd4840`.

- **Sonda: causa confirmada.** O `accept()` bloqueado em outra thread aceitou uma conexão nova da sonda 1,5 ms depois do `close()`. As portas foram cruzadas, cliente 43416 = `peer_port`. Resultados:
  - sem correção: 26/30;
  - com `shutdown(SHUT_RDWR)` antes do `close()`: **30/30**.

  A correção está no branch `fix/teste-sonda-instavel` (`3cca38d`, já no GitHub).
- **Provedor: o tempo extra está no atraso do timer de expiração.** O timer chegou a atrasar até 1,26 s depois do prazo de 14 s.
  - Nada além disso pesou: rota e dependências levaram ≤ 0,11 s, a anonimização ≤ 1,5 ms, e a limpeza do httpx2 e o `__aexit__` menos de 1 ms.
  - Não houve aviso de callback lento no asyncio, então nenhuma função Python bloqueou o event loop. O atraso vem do agendamento do ambiente (selector, scheduler do Linux ou hipervisor), sem causa mais específica isolada.
  - **Risco de produto:** com prazo de 14 s e meta de 15 s, sobra só 1 s de margem para atrasos do ambiente. Opções a decidir: reduzir `IA_TIMEOUT_SECONDS` para 13 s, ou manter e registrar a margem como limite.
- **DNS:** sensível ao tempo sob carga, e só falha na suíte completa. Avaliar uma espera por evento em vez do `sleep(0.25)` fixo.

## Critérios de aceite
- 30 de 30 execuções isoladas na VM para cada teste, sem afrouxar limites.
- Provedor: a chamada respeita o orçamento total de 15 s, medido de ponta a ponta na VM.
- Nenhum limite de asserção afrouxado sem justificativa registrada.
