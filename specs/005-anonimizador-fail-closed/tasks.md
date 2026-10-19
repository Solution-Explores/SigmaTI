> Atualização 19/10/2026: entrega parcial em correção/revisão. As afirmações de conclusão abaixo são históricas e não equivalem ao aceite integral. Consulte [a revisão da sprint](../011-recuperacao-sprint/evidencias.md).

---
description: "Lista de tarefas da Issue #5 - Módulo Anonimizador com Fail-Closed e Experimento E6"
---

# Tasks: Anonimização LGPD Robusta e Fail-Closed (RF05) #5

**Input**: [spec.md](spec.md) e [plan.md](plan.md) em `specs/005-anonimizador-fail-closed/`  
**Prerequisites**: K05 (cliente HTTP assíncrono e timeouts) e K06 (erros públicos padronizados)  
**Organization**: As tarefas são agrupadas por fases e histórias de usuário.

---

## Phase 1: Setup e Estrutura Básica

- [x] T001 Criar diretórios `resultados/` e `tests/data/` no repositório.
- [x] T002 Definir as estruturas de dados e contratos de resultado de sanitização (`ResultadoSanitizacao`, `SanitizationError`, `SanitizationResidualError`) em `sanitizer.py`.
- [x] T003 Configurar categorias de mapeamento de equipamentos hospitalares em `sanitizer.py`.

---

## Phase 2: Foundational (Módulo de Sanitização e Regras Base)

- [x] T004 Implementar regras de generalização de rede: IPv4 para sub-rede `/24` e IPv6 para prefixo `/64` utilizando `ipaddress` em `sanitizer.py`.
- [x] T005 [P] Implementar mascaramento de endereços MAC (`00:1B:44:11:3A:B7`, variantes hifenizadas e pontuadas) em `sanitizer.py`.
- [x] T006 [P] Implementar mapeamento categórico de hostnames/equipamentos (switches, roteadores, tomógrafos, servidores) em `sanitizer.py`.
- [x] T007 [P] Implementar sanitização de PII médica e civil: CPFs, cartões CNS, números de prontuário e e-mails em `sanitizer.py`.
- [x] T008 Implementar sanitização de nomes próprios com base em lista configurada e heurísticas contextuais clínicas em `sanitizer.py`.

---

## Phase 3: User Story 1 — Sanitização Abrangente de Dados (Priority: P1) 🎯 MVP

- [x] T009 [P] [US1] Criar testes unitários para cada tipo de identificador de rede (IPv4, IPv6, MAC) em `tests/test_sanitizer.py`.
- [x] T010 [P] [US1] Criar testes unitários para dados pessoais e hospitalares (CPF, CNS, prontuário, e-mail, nomes) em `tests/test_sanitizer.py`.
- [x] T011 [P] [US1] Criar teste para validar a não existência de tabela reversível de/para em memória (RF05) em `tests/test_sanitizer.py`.
- [x] T012 [US1] Integrar o pipeline de transformações em função unificada `sanitizar_texto(texto: str) -> ResultadoSanitizacao` em `sanitizer.py`.
- [x] T013 [US1] Garantir sanitização tanto no campo `alerta.descricao_erro` quanto em `alerta.equipamento` na montagem do prompt em `main.py`.

---

## Phase 4: User Story 2 — Falha Segura (*Fail-Closed*) e Auditoria (Priority: P1)

- [x] T014 [P] [US2] Criar teste unitário para detecção residual em `tests/test_fail_closed.py`.
- [x] T015 [P] [US2] Criar teste de integração injetando exceção no anonimizador e verificando que `consultar_ia` não é chamado (`tests/test_fail_closed.py`).
- [x] T016 [P] [US2] Criar teste de integração verificando registro estruturado seguro de auditoria sem vazamento do payload original (`AUDIT_PRIVACY`).
- [x] T017 [US2] Implementar etapa de verificação residual (*two-pass detection*) em `sanitizer.py`.
- [x] T018 [US2] Integrar o mecanismo fail-closed no endpoint `POST /api/alertas` em `main.py`, abortando o envio externo na presença de resíduos ou exceção.
- [x] T019 [US2] Conectar o evento de falha à trilha de auditoria e ao logging seguro padronizado.

---

## Phase 5: User Story 3 — Validação Empírica e Experimento E6 para o TCC (Priority: P2)

- [x] T020 [P] [US3] Construir corpus sintético com 50 casos rotulados (25 positivos com diversas classes de PII e 25 negativos com logs técnicos) em `tests/data/corpus_sintetico_pii.json`.
- [x] T021 [US3] Desenvolver script de medição e benchmarking `scripts/executar_experimento_e6.py`.
- [x] T022 [US3] Executar o script, apurar métricas (Recall de PII: **100.00%**, Falsos Positivos: **0.00%**) e gerar o relatório em `resultados/experimento-e6-anonimizacao.md`.

---

## Phase 6: Revisão, CI e Evidências

- [x] T023 Executar suite completa do `pytest` garantindo compatibilidade com os testes de regressão (127 testes passando).
- [x] T024 Atualizar a tabela de bloqueadores em `engenharia/docs/05-seguranca-e-pendencias.md` (mitigando B6 e B7).
- [x] T025 Gerar arquivo de evidências da execução dos testes e do Experimento E6 em `specs/005-anonimizador-fail-closed/evidencias.md`.
- [x] T026 Gerar `registro-issue.md` consolidando a entrega para a Issue #5.
