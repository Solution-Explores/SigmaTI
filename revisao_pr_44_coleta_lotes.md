# Revisão do PR #44 — Persistir coleta em lotes e aguardar vagas no calendário (#8)

**Veredito: Aprovação (Approve).** A solução técnica é exemplar, robusta e aderente a todos os requisitos de integridade ACID, contenção controlada e métricas da Issue #8. O PR pode ser integrado assim que o PR #43 (`fix/base-issues`) for mergeado na branch base.

---

## 1. Verificação Local e Execução de Testes

- **Ambiente:** Windows 11, Python 3.14.6, repositório em worktree dedicada (`SigmaTI-review`).
- **Suíte Focada do Scheduler (`engenharia/tests/test_scheduler.py`):**
  - **16 aprovados em 5,32 s** (100% de sucesso).
  - Cobre: espera transitória de capacidade no calendário sem descarte, commit atômico de lotes, drenagem completa no `stop()`, propagação de falhas em lote para todos os waiters, saturação de scheduler sem backlog/sobreposição e distinção de perdas (`missed_capacity`, `missed_clock`, `missed_overlap`).
- **Regressão Geral Não-PostgreSQL (`pytest -m "not postgres"`):**
  - **434 aprovados, 55 ignorados (específicos de contêiner PG/integração) em 85,73 s** — zero falhas e zero erros.
- **Validação de Merge e Compatibilidade:**
  - `git merge-tree` entre o HEAD de `pr-44` (`ddd4840`) e o HEAD atual de `fix/base-issues` (`3d32e79`) executou com **zero conflitos**, garantindo integração transparente quando o PR #43 for concluído.

---

## 2. Análise Técnica e Checklist dos Requisitos

### A. Algoritmo do Scheduler e Contrapressão (#8)
1. **Eliminação do descarte prematuro:** Anteriormente, se as 32 vagas estivessem ocupadas no instante exato do tick, o alvo perdia o ciclo inteiro de 2 s. Agora, o scheduler registra o alvo em `_capacity_deferred`, incrementa `capacity_deferrals` e mantém a oportunidade pontual no calendário (`_due`).
2. **Prevenção de efeito manada (thundering herd):** Não há criação de tarefas, threads ou filas adicionais na memória. O scheduler despacha assim que uma vaga é liberada.
3. **Descarte estrito de períodos vencidos:** Se o atraso acumular a ponto de ultrapassar um intervalo completo (`(now - due) // interval >= 1`), os ciclos perdidos são descartados (evitando rajadas compensatórias) e categorizados precisamente em `missed_capacity`.
4. **Métricas segregadas:** `missed_clock`, `missed_overlap`, `missed_capacity` e `capacity_deferrals` permitem diagnosticar com exatidão a causa raiz de qualquer perda de ciclo.

### B. Persistência em Lotes (`PostgresOperationalStore.record_measurements`)
1. **Ordenação de Locks Anti-Deadlock:** `SELECT id FROM alvos WHERE id = ANY(...) ORDER BY id FOR UPDATE` garante lock determinístico ordenado lexicograficamente por ID, prevenindo deadlocks circulares entre lotes ou workers concorrentes.
2. **Snapshots Isolados sob READ COMMITTED:** A execução em pipeline desacopla o lock dos alvos da leitura de detectores, garantindo que o snapshot de estado reflita o último commit pós-aquisição de lock.
3. **Cálculo de Anomalias Fiel:** Processamento do EWMA/MAD preserva paridade binária e comportamental com a ingestão individual (`test_batch_and_individual_detector_state_match`).
4. **Atomicidade e Rollback Integral:** Medições, agregações (`minute`/`hour`), snapshots de detectores, incidentes deduplicados e eventos operacionais são comitados em uma única transação atômica. Se qualquer validação, chave ou inserção falhar, o lote inteiro sofre rollback.
5. **Idempotência e Replay Seguro:** Se algum identificador de medição já constar no banco, a execução cai no caminho unitário `record_measurement(..., _session=session)` dentro da mesma transação, comparando integridade de payload e prevenindo contagens duplicadas.
6. **Serialização Estrita de Eventos:** O advisory lock global `pg_advisory_xact_lock(7417001)` garante ordenação estrita dos eventos operacionais até o commit, com `session.flush()` prévio para reduzir a janela crítica do lock.

### C. Drenagem e Ciclo de Vida
1. **Drenagem Limpa no Shutdown:** O método `Scheduler.stop()` aguarda tanto os futures em `_writes` quanto a corrotina `_batch_task`, garantindo que medições já coletadas sejam efetivamente persistidas no banco antes de liberar a liderança do nó.
2. **Fallback Transparente:** Mantida total compatibilidade retroativa para repositórios que implementam apenas `record_measurement`.

---

## 3. Observações e Recomendações (Não Bloqueantes)

- **A. Alvo inexistente descarta lote inteiro:**
  Conforme adequadamente registrado em `doc/coleta-lotes.md`, se um alvo for removido do banco durante a coleta, a ausência de lock correspondente lança `KeyError` e aborta o lote inteiro. Como o sistema atual adota desativação lógica (`PATCH /ativo=false`) e não implementa deleção física de alvos, a modelagem atual é segura. Caso hard delete venha a ser suportado no futuro, valerá isolar a linha faltante.
- **B. Instalação de desenvolvimento local:**
  Para desenvolvedores testando localmente na branch de review, lembrar de rodar `pip install -e engenharia` no venv para que as novas métricas de dataclass sejam refletidas de imediato.

---

## 4. Texto Sugerido para Parecer no Pull Request (GitHub)

```markdown
### Parecer de Revisão: Aprovado (LGTM) 🚀

Revisão técnica e validação local concluídas com sucesso.

- **Scheduler e Calendário (#8):** A retenção da oportunidade de coleta via `_capacity_deferred` resolve o descarte indevido por indisponibilidade momentânea de worker sem expandir concorrência além de 32 e sem enfileirar sondas na memória. A distinção entre `missed_clock`, `missed_overlap` e `missed_capacity` traz excelente observabilidade.
- **Pipeline e Transacionalidade:** Locks ordenados por ID (`ORDER BY id FOR UPDATE`) eliminam risco de deadlock entre lotes. O pipeline do Psycopg otimiza roundtrips, e o rollback conjunto de amostras, detectores, agregados e incidentes assegura integridade ACID completa.
- **Idempotência e Eventos:** Fallback atômico para verificação de replay e advisory lock `7417001` preservam consistência e ordem contígua da trilha operacional.
- **Testes Locais:** 16/16 testes de scheduler aprovados (5,32 s); 434 testes não-Postgres aprovados (zero falhas/erros); merge limpo sem conflitos contra o topo de `fix/base-issues`.

Pronto para integração assim que o PR #43 for concluído e incorporado.
```
