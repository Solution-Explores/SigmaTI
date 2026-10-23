# Plano de sprints pós-demo (28/10 a 17/11/2026)

## Contexto
A demo ao orientador acontece **terça 27/10 às 18h** (SHA congela segunda 26/10 às 18h). Não existe sprint formal de duração fixa: a sprint de 15 a 20/10 não foi cumprida e depois o trabalho seguiu por cronograma diário. A **banca está marcada para 18/11/2026, e pode ser antecipada**. Restam três semanas úteis após a demo, e o backlog é maior que isso. O plano abaixo usa sprints de 1 semana, trata 11/11 como congelamento de código (margem para a banca antecipada) e separa o que entra do que vira "trabalho futuro" no TCC.

Fontes: `docs/plano-demonstracao-2026-10-27.md`, `docs/historico/rascunhos/documentacao-2026-10-21/levantamento-github.md`, `specs/018-backup-restauracao/segunda-maquina.md`, `validacao-vm/rodada-2026-10-22h/RESULTADO.md`.

## Premissas (confirmar)
- Equipe: Vinícius (integração, aceite), Iohan (revisor, disponível após 22h, sábado à tarde e domingo), Joyce (design, fora deste escopo). Codex roda testes na VM.
- Disponibilidade do Vinícius: segunda a sexta de manhã e à tarde, sábado o dia todo, domingo só de manhã. Estimativa: ~6 h focadas por dia útil, ~8 h no sábado, ~4 h no domingo. Iohan: ~10 h/sem (noites, sábado à tarde, domingo).
- Sprints rodam de quarta a terça. 02/11 (segunda) é Finados, então a S1 tem 4 dias úteis.
- Capacidade: **1 pt ≈ 2 h**. S1 ≈ 46 h → 23 pts brutos, **~17 planejados**. S2 e S3 ≈ 52 h → 26 pts brutos, **~19 planejados** (≈75%, com margem para interrupções e revisão noturna).
- Estimativas são do planejamento (o repositório não tem pontos); ajustar se necessário.
- Escopo escolhido: v1.0.0 + débitos técnicos (#45, #46, #47). Expansão (#10, #16–#19, #21, #22, #30, #23) **não entra** antes da banca; vira capítulo de trabalho futuro. Itens externos e design Joyce ficam fora.

---

## Sprint 1 — 28/10 a 03/11 · "Fechar a v1.0.0"
**Meta:** `v1.0.0` publicada na `main` com #5, #6 e #8 aceitas e repositório reorganizado.

| Prio | Item | Est. | Dono | Dependências |
|------|------|------|------|--------------|
| P0 | PR de estrutura (`backend/`, `frontend/`, `deploy/`), integrar até 30/10 | 3 | Vinícius | Revisão do Iohan |
| P0 | #6 e #8: aceite final | 2 | Vinícius | #43/#44 já na `develop` |
| P0 | #5: anonimização contra critérios completos + casos adversariais | 3 | Iohan/Vinícius | Corpus E6 |
| P0 | Aceite da release `v1.0.0` (31/10 e 01/11) e tag na `main` | 2 | Vinícius | Estrutura integrada |
| P0 | Reserva para o retorno do orientador sobre a demo (triar em 28/10) | 2 | Vinícius | Retorno da demo |
| P1 | PR de documentação/README (subpastas de `docs/`, arquivos soltos) + descrição e tópicos do repositório | 2 | Vinícius | `feature/trail-fase1` (`docs/` já comitado, sem PR) |
| P1 | #25: restauração em outra máquina física | 2 | Iohan | Acesso à segunda máquina |
| P2 | #13: âncora externa da auditoria + rotação HMAC | 5 | Vinícius | Decisão do orientador |

**Carga:** P0 = 12 pts; com P1 = 16 pts (~94% dos ~17 planejados); com #13 = 21 pts (~124%). P1 e P2 são o que se corta.
**Alerta:** a proposta ao orientador prometia #13, #5, #25 e `v1.0.0` até 03/11. Mesmo com a disponibilidade maior, #13 não cabe sem estourar. Recomendo negociar #13 e #25 para 10/11 (Sprint 2). Só puxar #13 para a S1 se P0 e P1 fecharem até 01/11.

**Ordem da reorganização:** nenhuma pasta ou arquivo é movido antes de 27/10. Em 28/10 abre-se primeiro o PR de documentação (baixo risco) e depois o de estrutura do código. O layout está em `docs/plano-demonstracao-2026-10-27.md`, seção "Depois da demo".

**Datas:** 28/10 início + reorg · 30/10 estrutura integrada · 31/10–01/11 aceite · 01/11 mid-check · 02/11 Finados (feriado) · 03/11 fim/demo interna · 03/11 retro.

**Riscos**
| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Revisão só à noite/fim de semana (Iohan) | PR de estrutura trava 30/10 | Abrir PR em 28/10; revisão em lotes |
| Mover pastas quebra CI/compose | `validate-compose` reprovado (já ocorreu no #47) | Rodar CI no PR antes do aceite; manter rollback |
| Máquina física indisponível (#25) | Item não fecha | Registrar como limitação no TCC |
| Links quebrados ao mover subpastas de `docs/` e `resultados/` | Referências mortas em `README.md`, `specs/*` e scripts | `git grep` dos caminhos antigos, `scripts/validate_*` e CI antes do merge |
| `feature/trail-fase1` ficar sem PR | `docs/` só existe nessa branch | Abrir o PR de documentação em 28/10, primeiro item do dia |

---

## Sprint 2 — 04/11 a 10/11 · "Robustez e evidências"
**Meta:** auditoria verificável fora do host, testes estáveis e resultados prontos para o texto do TCC.

| Prio | Item | Est. | Dono | Dependências |
|------|------|------|------|--------------|
| P0 | #13: âncora externa, rotação HMAC, verificação agendada (se não coube na S1) | 5 | Vinícius | — |
| P0 | #45 + #47: testes instáveis (IA, sonda, DNS, scheduler; inclui o 4º teste, `test_scheduler`, 28/30) e CI do compose; decidir a margem do timer de IA (14 s contra 15 s) | 4 | Iohan | PR #47 |
| P0 | #25: segunda máquina física (se não coube na S1) | 2 | Iohan | Máquina |
| P1 | Rodada final de validação na VM + registro de MTTD/burn rate no texto | 2 | Vinícius | #45 |
| P1 | #46: custo da verificação HMAC (hoje ~3 s com 100 mil registros, meta 50 ms) | 3 | Vinícius | #13 |
| P2 | Painel exibir MTTD e burn rate (hoje só pela API) | 3 | Vinícius | — |

**Carga:** P0 = 9 pts (+2 se #25 escorregar da S1); com P1 = 14 pts (~74% dos ~19 planejados); com P2 = 17 pts (~89%).
**Datas:** 04/11 início · 07/11 mid-check · 10/11 fim · **10/11 anunciar congelamento de código**.

---

## Sprint 3 — 11/11 a 17/11 · "Congelamento e banca"
**Meta:** projeto estável, texto e apresentação prontos para a banca de 18/11.

| Prio | Item | Est. | Dono |
|------|------|------|------|
| P0 | Congelar código em 11/11; só correções de bug P0 | — | Todos |
| P0 | Texto/resultados do TCC e slides da banca | 4 | Vinícius |
| P0 | Ensaio de banca (13–14/11) e ajustes | 2 | Vinícius, Iohan |
| P0 | Roteiro de demo reaproveitado de `docs/roteiro-demonstracao.md`; backup do ambiente + VM de contingência | 2 | Iohan |
| P1 | Seção "Trabalho futuro": #10, #16–#19, #21, #22, #30, #23 e itens externos, com justificativa | 2 | Vinícius |
| P2 | #46 (se ainda aberta) como débito documentado | — | — |

**Carga:** P0 = 8 pts, com P1 = 10 pts (~53% dos ~19 planejados). A folga é deliberada: banca antecipada e imprevistos. **Datas:** 11/11 freeze · 14/11 ensaio · 17/11 checklist final · **18/11 banca**.
**Se a banca for antecipada:** a S3 comprime; a S2 vira a última sprint de código e o freeze passa para o dia anterior à nova data.

---

## Depois da banca (backlog, sem datas)
- Expansão: #10, #16–#19, #21, #22, #30, #23.
- Externos (dependem de hospital/hardware/coleta longa): #11, #12, #20, #24, #26–#29; épico #31.
- Design Joyce (DS-01 a DS-42), camada visual nova depois da `v1.0.0`.

## Definition of Done (todas as sprints)
- [ ] PR revisado (revisão cruzada) e integrado na `develop`
- [ ] CI verde (incluindo `validate-compose`)
- [ ] Testes passando; sem novos testes instáveis
- [ ] Documentação/spec atualizada
- [ ] Issue só fecha com todos os critérios atendidos; sinal do orientador quando aplicável

## Pontos em aberto para confirmar com o orientador
1. Renegociar #13/#25 de 03/11 para 10/11.
2. Confirmar 18/11 e se há risco de antecipação.
3. Licença do repositório.

## Verificação
- Cada sprint termina com: lista de issues fechadas, CI verde na `develop`, rodada de aceite registrada em `validacao-vm/`, atualização do quadro Trello.
- Mid-sprint check-in: comparar carga real contra o planejado; cortar P2/P1 se passar de ~100%.
