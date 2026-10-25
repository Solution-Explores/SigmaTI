# Revisão do PR #47 — Estabilização do teste de sonda de estatísticas (`test_stats_probe.py`)

**Veredito: Aprovação (Approve).** A alteração é estritamente cirúrgica, focada exclusivamente no arquivo de teste (`engenharia/tests/test_stats_probe.py`), não afrouxa nenhuma asserção e resolve a condição de corrida em sockets de servidor no encerramento de threads no Linux sem causar regressões no Windows. O PR está apto para merge imediato na branch `develop`.

---

## 1. Verificação Local e Execução de Testes

- **Ambiente de Teste:** Windows 11, Python 3.14.6, repositório em worktree dedicada (`SigmaTI-review`, branch `pr-47`, HEAD `0b372cb`).
- **Suíte Focada de Sonda (`engenharia/tests/test_stats_probe.py`):**
  - **10/10 testes aprovados** em todas as execuções.
  - **Validação de Estabilidade (5 rodadas consecutivas):** 100% de aprovação (50/50 execuções individuais, tempos médios de ~2,8s por suíte, 0 flakiness detectado no Windows).
- **Regressão Geral Não-PostgreSQL (`pytest -m "not postgres"`):**
  - **437 aprovados, 55 ignorados (contêiner PG/integração) em 89,23 s** — zero falhas e zero erros.
- **Validação de Branch e Merge:**
  - O commit `0b372cb` já integrou o topo de `origin/develop` (`75b1874`).
  - `git diff develop...pr-47` confirma alteração restrita a um único arquivo (`engenharia/tests/test_stats_probe.py`, +14 / -4 linhas).

---

## 2. Análise Técnica e Checklist da Correção

### A. Diagnóstico da Causa Raiz e Comportamento Multiplataforma
1. **Comportamento no Linux:** No Linux, chamar apenas `srv.close()` em um socket de escuta não interrompe de imediato uma chamada bloqueante `accept()` em execução em outra thread de teste. Sem o `srv.shutdown(socket.SHUT_RDWR)`, conexões subsequentes ainda podiam ser aceitas mesmo após a instrução de fechamento, provocando falha intermitente em `test_probe_many_perda_e_jitter` (que media perdas parciais como 66,67% em vez de 100%).
2. **Compatibilidade com Windows:** No Windows (Winsock), chamar `shutdown()` em um socket que está apenas em estado de escuta (`listen`) e não conectado a um par remoto levanta `OSError` (`WSAENOTCONN` / código 10057). O bloco `try: srv.shutdown(...) except OSError: pass` neutraliza essa exceção de forma transparente, permitindo que o `srv.close()` subsequente execute sem erro.
3. **Encapsulamento Uniforme:** A função auxiliar `_fechar(srv)` foi aplicada consistentemente nos 4 pontos de finalização de servidor de teste: `test_probe_tcp_up`, `test_probe_http_500_degradado`, `test_probe_http_200_com_csp_up` e `test_probe_many_perda_e_jitter`.

### B. Integridade das Asserções
- **Nenhuma asserção foi afrouxada:** Todas as verificações de perda, integridade, latência e status HTTP foram rigorosamente mantidas. Especificamente, o teste crítico `assert morto.loss_pct == 100 and morto.latency == {"n": 0}` continua exigindo 100% de perda após o desligamento da porta.

### C. Avaliação das Evidências Empíricas
- **Eficácia comprovada:** A validação empírica da correção decorre dos resultados controlados na VM Linux (rodada 3 / `validacao-vm/rodada-2026-10-22c`, na base `8cb1e23`), onde a taxa de aprovação saltou de 5/10 (sem a correção) para 30/30 (com a correção).
- **Rodada 7:** Na rodada 7 de 23/10, o teste passou 10/10 em ambos os cenários (comportamento típico de condições de corrida probabilísticas dependentes de escalonamento de threads/CPU), o que reforça que a prova de eficácia se apoia na rodada 3.

### D. Delimitação de Escopo
- O PR #47 cumpre estritamente o princípio de responsabilidade única: foca somente na estabilização do `test_stats_probe.py`. Os demais testes instáveis identificados (provedor de IA, resolução de DNS e `scheduler`) permanecem sob acompanhamento na Issue #45.

---

## 3. Texto Sugerido para Parecer no Pull Request (GitHub)

```markdown
### Parecer de Revisão: Aprovado (LGTM) 🚀

Revisão técnica e conferência local concluídas com êxito na branch `pr-47` (head `0b372cb`).

- **Escopo Cirúrgico:** Diff restrito unicamente ao arquivo de teste `engenharia/tests/test_stats_probe.py` (+14 / -4 linhas).
- **Correção da Condição de Corrida:** A inclusão de `_fechar(srv)` invocando `shutdown(SHUT_RDWR)` antes do `close()` soluciona a não-interrupção do `accept()` bloqueado no Linux. O tratamento de `OSError` garante total compatibilidade multiplataforma com o subsistema Winsock no Windows.
- **Rigor Mantido:** Nenhuma asserção foi alterada ou afrouxada; o teste continua exigindo 100% de perda pós-encerramento.
- **Testes Locais (Windows 11 / Python 3.14.6):**
  - `engenharia/tests/test_stats_probe.py`: 5 execuções consecutivas com 10/10 aprovações (100% de estabilidade).
  - Regressão geral (`pytest -m "not postgres"`): 437 testes aprovados e 55 ignorados (zero falhas e zero erros).
- **Integração:** Head já se encontra sincronizado com a `develop` (`75b1874`), sem qualquer conflito.

Pronto para merge em `develop`.
```
