# Pauta de 28/10/2026: pós-congelamento

Rascunho de 27/10, à noite, para a conversa de quarta. Não substitui o [plano de sprints](plano-sprints-pos-demo.md) nem a seção "Depois da demo: organização do repositório" do [plano da demonstração](plano-demonstracao-2026-10-27.md). O que está em "Decisões" é recomendação, a confirmar.

## Ponto de partida (conferido em 27/10, só leitura)

- `develop` é igual a `origin/develop` e está em `7851da6`, o SHA congelado. Ela ainda usa `doc/`; não tem `docs/`. Não há tag do SHA da demonstração (as tags existentes são `archive/*`).
- `feature/trail-fase1` está 19 commits à frente e 3 atrás da `develop` (os do #47: `3cca38d`, `0b372cb`, `7851da6`). A simulação de merge com a `develop` não dá conflito.
- `feature/documentacao-demo` (Iohan, base `75b1874`) não serve para merge: 336 de 390 arquivos já são idênticos aos nossos, cinco documentos da demo estão em versão anterior e 48 arquivos são cache de `.trail/`. O que valia, o relatório do ensaio de 25/10, já está em [historico/ensaio-independente-2026-10-25.md](../historico/ensaio-independente-2026-10-25.md).
- `pr-47` tem a revisão do #47 do Iohan (`revisao_pr_47_teste_sonda_instavel.md`) e o mesmo relatório.

## Decisões

1. **Regra da `develop` depois da demonstração.** Hoje o congelamento significa "nenhum commit novo até a demo". Proposta: terminada a demo, vale a Definition of Done do [plano de sprints](plano-sprints-pos-demo.md) (PR com revisão cruzada, CI verde incluindo `validate-compose`, sem teste instável novo, doc atualizada) e o congelamento de código volta em 11/11. Antes de liberar, marcar o `7851da6` com uma tag (por exemplo `demo-2026-10-27`), para o estado demonstrado continuar reproduzível. A tag só deve ser criada e enviada com a sua confirmação.
2. **Ordem das PRs.** Primeiro documentação, depois estrutura, como já decidido. Antes de abrir a de documentação, trazer a `develop` para dentro da `feature/trail-fase1` (limpo, pela simulação). A PR leva `doc/` → `docs/`, o relatório do Iohan, o `demo.ps1` corrigido e o `docs/demo/` que faltava na `develop` (tropeço 1 do relatório). `visao-do-produto.md` e o postmortem da sprint estão marcados como rascunho: decidir se entram assim.
3. **Destino das branches.**
   - `feature/documentacao-demo`: não mergear; apagar no GitHub só depois de o Iohan confirmar que não há nada dele fora do relatório.
   - Revisão do #47 (`pr-47`): antes de incorporar, alinhar duas divergências. O texto diz que o teste passou de 5/10 para 30/30, e o guia e o plano falam em 26/30 para 30/30 (rodada 3). O texto também declara "Approve", e no GitHub há só o comentário com o parecer favorável.
   - `.trail/cache`: decidir se se versiona ou se vai para o `.gitignore`.
4. **Retorno do orientador.** Triar em 28/10 (reserva P0 de 2 pontos na S1) e converter em issues. Falta o registro do retorno, que não está no repositório.
5. **Prazos com o orientador.** Renegociar #13 e #25 de 03/11 para 10/11, confirmar 18/11 e o risco de antecipação da banca, e a licença do repositório.
6. **#45.** Passa a cobrir o quarto teste instável (`test_scheduler`), o atraso do teste de carga E2 na rodada 8 (0,957 s contra 0,5 s) e a margem do timer de IA (14 s contra 15 s).

## Pendências de 27/10 sem registro

- Como foi a demonstração das 18h e o que o orientador respondeu.
- Os itens de terça do [checklist](../demo/checklist-terca.md) continuam em branco.
- Smoke do Iohan no `7851da6`: sem registro.
- Trello: a escrita ainda espera chave e token válidos (ver "Pendente" no plano).
