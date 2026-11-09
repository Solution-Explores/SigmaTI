# Planejamento pós-demo das issues abertas (28/10 a 18/11/2026)

## Contexto

A demo ao orientador foi em 27/10 (SHA `7851da6`, tag `demo-2026-10-27`). A banca será entre **01 e 10/12/2026** (edital; a Coordenação publica o dia e o horário). Em **18/11** começa a preparação da apresentação. Em 31/10 o orientador entregou a auditoria das issues de estabilização (`main@87e6a19`) e definiu três sprints, com milestones e prazos no GitHub. **Este plano segue essa divisão.** O [plano de sprints pós-demo](plano-sprints-pos-demo.md) é anterior à demo e fica como histórico.

Situação em 01/11: 26 issues abertas. A #6 foi fechada na auditoria (31/10). Entraram duas issues novas, #56 e #57.

**Premissas:**
- Equipe: Vinícius e Iohan, que trabalham de forma independente, cada um com apoio de agente de IA (Iohan: noites e fim de semana, ~10 h/sem). Joyce (design) fica fora.
- Fluxo: [fluxo de trabalho independente](../processo/fluxo-de-trabalho-tcc.md). Não há revisão obrigatória nem atribuição prévia: quem está livre pega a próxima issue na ordem do plano. A coluna "Quem pega" é só sugestão.
- Prazos: ficam nos **milestones do GitHub** (Sprint 1 em 03/11, Sprint 2 em 10/11, Sprint 3 em 17/11). Atrasou, aparece lá.
- 1 pt ≈ 2 h. Capacidade planejada: ≈ 17 pts na Sprint 1 (feriado em 02/11), 19 pts na Sprint 2 e 19 pts na Sprint 3. As estimativas são do planejamento, não do repositório.
- Definition of Done: CI verde (incluindo `validate-compose`), cada critério de aceite com teste ou comando, sem segredos, evidência registrada na issue e documentação atualizada. O autor integra o próprio PR. **Teste de segurança ou privacidade não pode ser escrito só por quem implementou a regra** (lição da #5).
- Pendente do orientador: o plano antigo recomendava mover #13 e #25 para 10/11. Os milestones mantêm 03/11 até ele decidir.

## Visão geral

| Sprint | Período | Papel | Meta | Issues |
|---|---|---|---|---|
| 1 | 28/10 a 03/11 | Começo | Fechar a `v1.0.0` | #56 (bloqueador), #5 (risco alto), #25, #13 |
| 2 | 04 a 10/11 | Meio | Robustez e evidências | #8, #45, #46, #57 |
| 3 | 11 a 17/11 | Fim | Congelamento, texto e ensaio; 18/11 inicia a preparação da apresentação | texto do TCC, slides, ensaio |
| 4 | depois da banca | Pós-fim | Expansão e pesquisa (backlog sem data) | #10 a #12, #16 a #24, #26 a #31 |

## Sprint 1: Fechar a v1.0.0 (28/10 a 03/11) · meta ≈ 17 pts

**Saída:** `v1.0.0` na `main` com #5, #25 e #56 fechadas, #13 fechada ou com o aval do orientador para ir a 10/11, e a #8 com a limitação do E2 declarada. Feriado em 02/11.

**Ordem de ataque:** #56 primeiro, porque destrava o merge de todos os PRs; depois #5 (risco alto); #25 e #13 em paralelo conforme a disponibilidade; release por último.

| Prio | Issue | Tarefa | Quem pega | Pts |
|---|---|---|---|---|
| P0 | #56 CI de infraestrutura vermelho | O diagnóstico da issue está incompleto: o commit `8661916` (22/10) já faz a `main` checar o manifest só pelo digest, e `validate_infrastructure.py --verify-registry` passa na `main`. As branches vermelhas (`feature/ds-*`, `feature/front-design-system`) não têm esse commit. Comentar a causa correta na issue (a proposta atual dela, de atualizar o lock, não é necessária). As branches vermelhas são dos PRs #52 a #55, da Joyce: avisar nos PRs para atualizar com a `main`, ou atualizar com a permissão dela, e reexecutar o CI. Só depois decidir se o digest do postgres deve ser atualizado, com revisão do changelog. Estrutural: separar a checagem hermética (compose × lock) da deriva agendada e informativa | Iohan | 1 |
| P0 | #5 Anonimização LGPD (RF05), risco alto | Seguir as sugestões do orientador na issue. Os 14 casos adversariais da auditoria vazam (nomes sem ponto após "Dr", após "Paciente:" ou sem cargo, login, CPF com espaços, registro de atendimento, hostname como `PACS-01`, telefone, RG, data de nascimento, endereço). **Vinícius:** corrigir as regras, incluindo os tipos novos; avaliar uma lista de nomes próprios do IBGE como detector residual que bloqueia, medindo falsos positivos; falha injetada sem chamada externa. **Iohan:** incluir os 14 casos como regressão em `tests/test_sanitizer.py` sem relaxar asserções (1); criar o **conjunto cego** sem ver as regras, cobrindo também os tipos novos, e relatar recall e precisão só nele, com intervalo de confiança (meta ≥ 99%) (3). Relatório em `docs/historico/resultados/`, com a limitação declarada | Vinícius (4) e Iohan (4) | 8 |
| P0 | Release | Aceite completo na `develop` (pytest, `validate_api_acceptance`, `validate_panel`, `validate_collection`) e tag `v1.0.0` na `main` | Vinícius | 2 |
| P1 | #25 Implantação e backup (RNF06) | Restauração em segunda máquina física (único critério aberto; as 17 verificações em VM já passaram). A decisão VM ou máquina física, pedida ao orientador em 24/10, ainda não tem registro | Vinícius | 2 |
| P1 | #13 Auditoria: âncora e rotação HMAC | Âncora externa do último hash, `key id` por entrada com rotação preservando o histórico, job diário de `verificar()`, ADR 0002. Se não fechar até 03/11, segue para a Sprint 2 com o aval do orientador | Vinícius | 5 |
| P0 | Triagem | Registrar a auditoria na #31, triar os PRs #41, #42 e #48 e confirmar com o orientador: dia e horário da banca (edital: 01 a 10/12), #13 e #25 em 03/11 ou 10/11, licença do repositório | Vinícius | 1 |

**Carga:** P0 = 12 pts (#56 1, #5 8, release 2, triagem 1); com #25 = 14; com #13 = 19 (≈ 112% dos ~17). Como já estamos em 01/11, o saldo real é menor que o da semana inteira. **Corte, nesta ordem:** #13 vai para a Sprint 2 (com aval), depois #25. Nunca se corta #56, #5 nem a release.

**Divisão por pessoa (Sprint 1):**

| Pessoa | Atividades | Pts | Ordem |
|---|---|---|---|
| Vinícius | #5 regras, tipos novos, detector de nomes e falha injetada (4) · #25 restauração em máquina física/VM e testes relacionados (2) · #13 âncora e rotação HMAC (5) · release e tag `v1.0.0` (2) · triagem com o orientador (1) | 14 | #5 regras, #25, #13, triagem, release por último |
| Iohan | #5 regressão dos 14 casos (1) e conjunto cego com relatório de recall (3) · #56 CI de infraestrutura (1) | 5 | conjunto cego primeiro (não depende de ninguém), regressão, #56 |

- **Divisão da #5:** quem escreve as regras (Vinícius) não escreve os casos de avaliação (Iohan), como pede o orientador. Iohan não vê as regras antes de fechar o conjunto cego, e Vinícius não ajusta as regras olhando o conjunto cego.
- **Máquina física, VM e testes relacionados** ficam com o Vinícius, que é quem tem o ambiente. Isso inclui a #25, a rodada de carga da #8 e a validação final.
- **Carga:** a soma da Sprint 1 passa do planejado (19 contra ~17). Vinícius concentra 14 pts. Pedir ao orientador que a #13 vá para 10/11 resolve; sem isso, a #13 é o item cortado.
- A #56 não bloqueia PRs novos: a `develop` já contém o commit `8661916`. Ela só limpa as branches antigas e corrige o registro da causa.
- A release só sai depois de #5 e #56 integradas.
- **Verificação independente:** os pontos que o orientador pediu continuam valendo (conjunto cego escrito por outra pessoa, evidência da #25 comentada na issue, testes de cada critério). O resto segue o [fluxo](../processo/fluxo-de-trabalho-tcc.md): cada um integra o próprio PR com o CI verde.

**Riscos:** CI instável sem revisão humana de apoio (tratar a #45 cedo); #5 mexe em área sensível, então só fecha com o conjunto cego e o caso negativo; máquina física indisponível para #25 (registrar como limitação no TCC).

## Sprint 2: Robustez e evidências (04 a 10/11) · meta ≈ 19 pts, previsto 12 a 15

**Saída:** testes sem instabilidade conhecida, rotas sem "sucesso falso", auditoria verificável fora do host e resultados prontos para o texto. **10/11: anunciar o congelamento de código.**

| Prio | Issue | Tarefa | Quem pega | Pts |
|---|---|---|---|---|
| P0 | #45 Testes instáveis | **Registrar a triagem até 04/11** com: decisão do timer de IA (14 s ou 13 s, com medição), hipótese para o atraso de 0,957 s do E2 de carga e troca do `sleep(0.25)` do teste de DNS por sincronização por evento. Depois cobrir o 4º teste (`test_scheduler`) e estabilizar. Atribuída ao Vinícius no GitHub | Vinícius | 4 |
| P0 | #8 Scheduler + SSE (RF01) | Prazo vencido (era 23/10). Dois critérios já atendidos (SSE ≤ 5 s em 30 quedas; reinício sem duplicar). Para fechar: fechar a #45 e registrar **três rodadas de carga consecutivas** (≥ 200 alvos) dentro da meta de 0,5 s, na VM | Vinícius | 2 |
| P0 | #57 Rotas com sucesso sem efeito | Rotas não implementadas respondem `501`: `POST /api/chaves/rotacao`; `POST /api/alertas` registra o incidente de fato (armazenamento da #7) ou muda o texto para "Diagnóstico gerado"; `/api/n8n/acesso` lê `SIGMA_N8N_URL`; listas fixas vazias de `/api/alertas`, `/api/pacotes` e `/api/relatorios` deixam de parecer "sem dados". Um teste por rota garante que nenhuma responde 2xx sem efeito; a matriz RBAC de `test_session_auth.py` continua verde; o painel não mostra 501 como sucesso. Rotação real fica na #23 e relatórios na #16 | Iohan | 3 |
| P1 | #46 Custo da auditoria | Triagem estava marcada para 27/10 sem registro. Leitura incremental ou cache do último `seq/hash`, preservando a recusa de gravação após adulteração; meta de 50 ms com 100 mil registros (hoje ~3 s). Se não couber, documentar como débito | Vinícius | 3 |
| P1 | Validação | Rodada final na VM (Codex) no SHA candidato; registrar MTTD e burn rate no texto | Vinícius | 2 |
| P0 | #13 e #25 | Só se escorregaram da Sprint 1 | Quem estiver livre | (5 + 2) |
| P2 | Painel | Exibir MTTD e burn rate (hoje só pela API) | Vinícius | 3 |

**Carga:** P0 = 9 pts (+7 se #13 e #25 escorregarem); com P1 = 14; com P2 = 17 (≈ 89% dos 19). Vinícius concentra #45, #8, #46 e a validação na VM (11 pts); Iohan fica com a #57 e pode assumir parte do painel. **Corte:** se passar de ~100% no check-in de 07/11, sai o P2 e depois a #46.

## Sprint 3: Congelamento e banca (11 a 17/11) · meta ≈ 10 de 19 pts (folga deliberada)

**Saída:** projeto estável, texto e apresentação prontos. Marcos: 11/11 congelamento · 13 e 14/11 ensaio · 17/11 checklist final (fim do milestone) · **18/11 início da preparação da apresentação** (banca entre 01 e 10/12).

| Prio | Tarefa | Quem pega | Pts |
|---|---|---|---|
| P0 | Congelar o código em 11/11; só correção de bug P0 | Todos | 0 |
| P0 | Texto e resultados do TCC; slides da banca | Vinícius | 4 |
| P0 | Ensaio de banca (13 e 14/11) e ajustes | Vinícius, Iohan | 2 |
| P0 | Roteiro de demo (`docs/demo/roteiro-demonstracao.md`) | Iohan | 1 |
| P0 | Backup do ambiente e VM de contingência | Vinícius | 1 |
| P1 | Capítulo "Trabalho futuro" com as issues da Sprint 4 e a justificativa de cada uma | Vinícius | 2 |

**Janela da banca (edital):** 01 a 10/12. O congelamento de 11/11 se mantém.

## Sprint 4: Depois da banca (backlog, sem data)

| Grupo | Issues |
|---|---|
| Expansão de engenharia | #10 (CUSUM e Page-Hinkley), #16 (relatório semanal n8n, RF06), #17 (postmortem), #18 (triagem por IA com fallback), #19 (diff de superfície), #21 (runbooks), #22 (reteste automático), #23 (cofre de chaves, RNF07), #30 (verificação formal) |
| Dependem de hospital, hardware ou coleta longa | #11 (E2 a E5), #12 (RTT real por 2 semanas), #20 (PRR), #24 (LGPD e ISO 27001), #26 (sonda embarcada), #27 (NTP × PTP), #28 (modelo de filas), #29 (SNMP e NetFlow) |
| Épico | #31 (guarda-chuva dos itens acima) |

Ordem sugerida: #23 e #16 (fecham RNF07 e RF06), depois #10, #21, #22, #18 e #17. Os itens de pesquisa dependem de acesso externo.

## Cobertura das 26 issues abertas

- Sprint 1: #5, #13, #25, #56.
- Sprint 2: #8, #45, #46, #57.
- Sprint 4: #10, #11, #12, #16 a #24, #26 a #31.
- Fechada na auditoria: #6.
- Conferência: #5 (casos adversariais rodados em 01/11), #56 (script rodado na `main` em 01/11) e #57 (rotas lidas no código) foram verificadas neste plano. Os demais achados da auditoria, incluindo a contagem de 492 testes no CI, foram aceitos como informados.

## Referências

- Auditoria das issues de estabilização, do orientador (31/10/2026).
- [Plano de sprints pós-demo (anterior)](plano-sprints-pos-demo.md)
- [Plano até a demonstração de 27/10/2026](plano-demonstracao-2026-10-27.md)
- [Pauta de 28/10/2026](pauta-pos-congelamento-2026-10-28.md)
