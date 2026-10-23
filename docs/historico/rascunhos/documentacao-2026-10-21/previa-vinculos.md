
## Trello — resolução dos vínculos antes da publicação

Novas issues confirmadas: #45 (testes instáveis) e #46 (custo da auditoria). Substituem os marcadores NOVA_INSTAVEIS/NOVA_AUDITORIA do planejamento acima. Cartões #6/#8 também recebem os dois links, marcados como não bloqueadores da demo.

### ISSUE #13 — Âncora externa, rotação HMAC e verificação agendada

## Situação vigente — 21/10/2026
[Certo] Implementação e critérios completos pendentes. Os 7/7 testes concorrentes da rodada-2026-10-22b não comprovam âncora nem rotação. Entrega proposta 03/11, a confirmar pelo orientador em 24/10. Sem PR aberto exclusivo.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy), pendente.
- Prazo: 03/11/2026 às 18h, proposto (UTC−4).
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/13
- PR aberto exclusivo: nenhum confirmado; não mover para Revisão e testes sem PR aberto.


### ISSUE #25 — Validar restauração em outra máquina física

## Situação vigente — 21/10/2026
[Certo] 17 verificações aprovadas em VM no mesmo host; outra máquina física continua pendente. As três rodadas de 21/10 preservaram o banco, sem repetir o aceite de restauração. Solicitar decisão VM versus host físico em 24/10; prazo proposto 03/11. PR #40 integrado cobriu etapa local; PR #41 aberto é documentação para revisão após a demo.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy), pendente.
- Prazo: 03/11/2026 às 18h, proposto (UTC−4).
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/25
- PR aberto exclusivo: nenhum confirmado; não mover para Revisão e testes sem PR aberto.


### ISSUE #45 — Testes instáveis (não bloqueia a demo)

## Situação vigente — 21/10/2026
[Certo] Não bloqueia a demo. Baseline: provedor9/10, sonda5/10; DNS já falhou na suíte. Sonda original26/30 → shutdown30/30; branch fix/teste-sonda-instavel@3cca38d, sem PR. Provedor: timer atrasa até1,263s; subcausa inconclusiva. Prazo27/10 para triagem/decisão, não correção completa. Aceite final da demo em23/10 permanece obrigatório.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy), pendente.
- Prazo: 27/10/2026 às 18h, triagem proposta (UTC−4).
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/45
- PR aberto exclusivo: nenhum confirmado; não mover para Revisão e testes sem PR aberto.


### ISSUE #46 — Custo da auditoria (não bloqueia a demo)

## Situação vigente — 21/10/2026
[Certo] Não bloqueia a demo. Gravação/verificação relê a trilha completa sob lock; comportamento O(n). Falta benchmark com10k/100k/1M; não afirmar gargalo já medido. Prazo27/10 para triagem/definição do benchmark, não implementação. Preservar detecção de adulteração e bloqueio de novas gravações.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy), pendente.
- Prazo: 27/10/2026 às 18h, triagem proposta (UTC−4).
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/46
- PR aberto exclusivo: nenhum confirmado; não mover para Revisão e testes sem PR aberto.


