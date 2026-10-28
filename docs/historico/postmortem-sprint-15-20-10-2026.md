# Postmortem sem culpa: sprint de 15 a 20/10/2026 e falha de carga da coleta

> **Rascunho de 25/10/2026.** Escrito a partir dos registros do repositório: [plano de conclusão](../planejamento/plano-conclusao-2026-10-20.md), [revisão dos achados](revisao-achados-base-2026-10-20.md), [diário de 21/10](../tcc/diario-bordo/21-10-2026.md), [plano da demonstração](../planejamento/plano-demonstracao-2026-10-27.md), [coleta em lotes](coleta-lotes.md) e as rodadas em [`validacao-vm/`](../../_pacote-local/validacao-vm/). Itens marcados **[a confirmar]** não têm fonte no repositório e precisam da memória de quem participou. Horários em UTC−4 (Manaus).

## Como ler

Este documento não procura responsáveis. Parte da premissa de que cada pessoa decidiu da melhor forma possível com o que sabia e com as ferramentas que tinha naquele momento. A pergunta é o que, no processo e no ambiente, permitiu que o problema acontecesse e demorasse a aparecer. Pessoas aparecem pelo papel (equipe, revisão, agente de testes na VM), não pelo nome.

## 1. Resumo

A sprint de 15 a 20/10 tinha entrega marcada para 20/10 às 18h. O prazo passou com as issues #6 e #8 sem aceite. O motivo mais visível foi uma falha de capacidade: no cenário E2 (200 alvos, intervalo de 2 s, 32 trabalhos), o contador `missed` subiu de 150 para 200 durante a janela de carga, numa VM com 4 vCPU e 4 GiB. A falha apareceu na validação em VM de 20/10, depois de o código já estar integrado e de uma conferência anterior ter recomendado o aceite da #8.

A correção (PR #44, coleta em lotes e espera por vagas no calendário) foi escrita depois do prazo e levou a carga de 0 de 5 para 5 de 5 na mesma VM. A integração aconteceu em 22/10 (#43 às 22h25 e #44 às 22h52). A demonstração ao orientador, marcada para 24/10, passou para 27/10 às 18h.

Quatro fatores se combinaram: escopo maior que a janela de tempo, validação de capacidade tardia e num ambiente diferente do de desenvolvimento, testes instáveis que já existiam e atrapalharam a leitura dos resultados, e uma infraestrutura de validação em VM que falhou por motivos de preparação: duas rodadas pararam antes de testar, uma teve metade do trabalho bloqueada e outra foi interrompida pela perda de acesso à VM.

## 2. Impacto

| Área | Efeito |
|---|---|
| Prazo | Entrega de 20/10 às 18h perdida. Demonstração movida de 24/10 para 27/10 às 18h |
| Escopo | Em 21/10: 7 de 30 issues encerradas (23%); #6 e #8 validadas em VM mas sem aceite; #5, #13 e #25 pendentes. Estimativas do diário: demonstração ≈43% pronta, escopo do TCC até a `v1.0.0` ≈65% |
| Qualidade | Nenhum dado perdido e nenhuma regressão em produção, porque não há produção. A falha foi achada em laboratório |
| Esforço | Quatro rodadas de VM total ou parcialmente bloqueadas ou interrompidas (rodadas 4 a 7), e uma retomada em 23/10 |
| Cronograma seguinte | #13 e #25 propostos para 10/11 em vez de 03/11. Reorganização do repositório adiada para 28/10 |

## 3. Linha do tempo

Cada entrada tem uma fonte no repositório. O que não pôde ser confirmado está marcado.

| Quando | Fato | Fonte |
|---|---|---|
| 15/10 | Início da sprint. Foco nas issues #2, #3 e #4, fila de prioridade K01 a K15, capacidade de 42 h (33,6 h de implementação, após reserva de 20%) e uma pessoa disponível só das 8h às 12h. Na conferência do quadro desse dia: K01 a K04 em revisão e testes, K08 e K14 em andamento, os demais a fazer; as três issues abertas e o `docker-compose.yml` da `main` com conflitos | [Prévia do quadro Trello](rascunhos/documentacao-2026-10-21/previa-trello-orientador.md) |
| 19/10 15:21 | PR #32 integrado, com dispensa de revisão independente autorizada especificamente para essa entrega | Plano de conclusão |
| 19/10 16:07 | Plano de conclusão publicado: sete blocos em ordem, uma fila de expansão com cinco itens e cortes de escopo às 10h e às 14h de 20/10 | Plano de conclusão |
| 19/10 20:05 a 20/10 09:46 | Integração dos PRs #35, #36, #37, #38 (coleta contínua e SSE, 20/10 08:11), #39 (painel) e #40 (backup) | `git log` |
| 20/10, antes das 14:35 (hora exata **[a confirmar]**) | Primeira rodada isolada em VM sobre `develop@8cb1e23`: 466 testes aprovados e 1 falha. O E2 reprova com `missed` de 150 para 200, erros 0, timeouts 0, atraso máximo de cerca de 97 ms. O limite de 14:35 vem da data de gravação dos relatórios no host, que é a cópia, não a execução | `validacao-vm/rodada-isolada` |
| 20/10 | Revisão técnica: a #8 deixa de ser candidata ao aceite. Experimentos sem mudar o produto: com 4 trabalhadores de persistência, 3 reprovações; com 1, 1 aprovação e 2 reprovações. Houve um stall RCU na VM. Testes parados a pedido | Revisão dos achados, [LEIA-ME](../../_pacote-local/LEIA-ME.md) |
| 20/10 18:00 | **Prazo da entrega** | Plano de conclusão |
| 20/10 19:01 | Commit `a97fe1b` (PR #43): auditoria coordenada e métricas para separar tempo de sonda e de gravação. Não corrige capacidade | `git log`, [09-coleta-eventos](../../engenharia/docs/09-coleta-eventos.md) |
| 20/10 19:49 | Commit `4350632` (PR #44): persistência em lotes e espera por vagas no calendário | `git log` |
| 21/10 00:30 a 03:30 | Retomada. Chave SSH da VM ausente do pacote, acesso recuperado pelo GRUB. O host esgotou a memória virtual (VM, Docker, navegador e um `git hash-object` lendo arquivos `.vdi`) | [Diário de 21/10](../tcc/diario-bordo/21-10-2026.md) |
| 21/10 ~02:41 | Rodada 1: `develop` 464/467 com carga **0 de 5**; merge local de `develop` + #43 + #44 com 488/488 e carga **5 de 5** | `rodada-2026-10-22` |
| 21/10 ~03:14 | Rodada 2, candidato `ddd4840`: 489/489 e carga 5 de 5. O agente de testes concluiu "não apto" por três testes instáveis; a equipe reclassificou como pré-existentes | `rodada-2026-10-22b` |
| 21/10 ~03:56 | Rodada 3: as instabilidades já existiam na `develop`. Causa da sonda confirmada (30/30 com a correção) | `rodada-2026-10-22c` |
| 22/10 | `validate-compose` vermelho no #43: a tag do PostgreSQL foi republicada no Docker Hub. O validador passou a checar só o digest (`8661916`) | Plano da demonstração |
| 22/10 21:34 a 22:05 | Rodadas 4 a 6: custo do HMAC medido, mas o ensaio do roteiro bloqueou (roteiro de Windows numa VM Linux); o commit pedido não existia na VM; `git bundle` recusou criar um bundle vazio | `rodada-2026-10-22d`, `e`, `f` |
| 22/10 22:25 e 22:52 | #43 e #44 integrados à `develop` (`75b1874`) | `git log` |
| 22/10 ~23:45 | Rodada 7: o SSH da VM deixou de responder no meio da execução. Causa não determinada | `rodada-2026-10-22g` |
| 23/10 | Rodada 7 retomada: cinco cargas de 200 alvos aprovadas; 79 de 80 execuções isoladas aprovadas; uma falha de 15,0248 s contra o limite de 15 s | `rodada-2026-10-23a` |

## 4. A falha de carga

### O que aconteceu

O cenário E2 mantém 200 alvos lógicos, intervalo de 2 s, 32 trabalhos e uma janela de observação de 6 s. A asserção exige que o contador `missed` não aumente na janela. Na `develop@8cb1e23` ele aumentou em 50 ciclos, com `errors=0`, `timeouts=0`, `queued=0`, atraso máximo de cerca de 97 ms e pico de 32 tarefas ativas. O contador `missed` mede ciclos descartados, não dados perdidos já persistidos.

### O que se sabe sobre a causa

- **Certo.** A reprovação se repetiu: 0 de 5 cargas na `develop` na rodada 1, e o E2 também reprovou no PR #43 isolado (que só trazia diagnóstico). A correção do PR #44 levou a 5 de 5 na mesma VM, nas rodadas 1 e 2, e a 5 de 5 de novo no candidato integrado em 23/10.
- **Provável.** Contenção ou capacidade insuficiente no caminho de persistência. O PR #44 passou a agrupar até 32 medições de alvos distintos numa transação e a manter o alvo à espera de uma vaga, tentando os vencimentos mais antigos primeiro. Pelo texto de [coleta-lotes.md](coleta-lotes.md), isso sugere que antes cada medição era gravada individualmente e o ciclo era descartado sem vaga livre. **[a confirmar no código de `8cb1e23`]**: esta leitura vem da documentação do PR, não de uma leitura do código antigo.
- **Não isolado.** A contribuição da virtualização (VirtualBox sobre Windows, com um stall RCU registrado) e a do código. O script da `develop` não gravava métricas antes de reprovar, então não existe medição de latência de persistência antes e depois. A taxa de aprovação melhorou, mas a causa não foi demonstrada por um experimento controlado.

### Por que demorou a aparecer

1. **O ambiente de desenvolvimento escondia o problema.** O CI anterior estava aprovado. A falha só reproduziu numa VM com 4 vCPU e 4 GiB, e essa validação aconteceu depois de o código já estar integrado na `develop`.
2. **Um critério de capacidade foi tratado como funcional.** Uma conferência anterior (PR #42) recomendou o aceite da #8 com base em testes que passavam. O critério de carga era uma propriedade do ambiente, e só podia ser verificado nele.
3. **A medição não tinha visibilidade.** Sem métricas separadas de sonda e de gravação, o primeiro diagnóstico só podia ser indireto. As métricas chegaram no PR #43, às 19h01 de 20/10, depois do prazo.
4. **Resultados de ajuste sem variação de ambiente.** Os experimentos com 4 e com 1 trabalhador deram resultados mistos (3 reprovações; 1 aprovação e 2 reprovações). Com um stall da VM no meio, não dava para concluir nada, e o registro foi honesto ao dizer isso.

## 5. A sprint não cumprida

### Fatores contribuintes

| # | Fator | Evidência |
|---|---|---|
| 1 | **Escopo maior que a janela.** A sprint nasceu com foco nas issues #2, #3 e #4 e 42 h de capacidade. O plano de 19/10 às 16h07 previa sete blocos em ordem (incluindo #6 a #9, #14, #15 e parte da #25) e uma fila de expansão com cinco itens, para pouco mais de um dia, com cortes às 10h e às 14h de 20/10. O repositório não diz se as issues #6 a #9 já faziam parte do compromisso original ou foram somadas em 19/10 **[a confirmar]** | Prévia do quadro Trello, plano de conclusão |
| 2 | **Dependência entre blocos.** O monitoramento (#8) dependia da persistência (#6 e #7). A falha de carga parou o bloco 4 e, por consequência, o painel e a recuperação | Plano de conclusão, seção 2 |
| 3 | **Revisão limitada pela disponibilidade.** Duas pessoas no código e na revisão, com a revisão independente à noite. O #43 foi integrado em 22/10 às 22h25 e o #44 às 22h52, dois dias depois do prazo original | Plano da demonstração, `git log` |
| 4 | **Testes instáveis pré-existentes.** Quatro testes (provedor de IA, sonda, DNS e o encerramento do agendador) falhavam de forma intermitente desde antes dos PRs, o que dificultou separar regressão de ruído. Em 26/10, a rodada 8 (`7851da6`) repetiu o padrão: uma falha de tempo no teste de carga E2 (0,957 s contra 0,5 s) e outra no teste do provedor de IA (15,545 s contra 15 s), sem causa isolada | Rodada 3, rodada 8, [#45](https://github.com/Solution-Explores/SigmaTI/issues/45) |
| 5 | **Preparação da validação em VM.** A rodada 4 teve o ensaio do roteiro bloqueado (roteiro só para Windows), a 5 parou porque o commit não existia na VM e a 6 parou porque a criação do bundle foi recusada. A rodada 7 foi interrompida por perda de acesso à VM | Rodadas 4 a 7 |
| 6 | **Dependência externa.** A tag do PostgreSQL republicada derrubou o `validate-compose` no CI justo antes da integração | Plano da demonstração |
| 7 | **Recursos do host.** A falta de memória virtual em 21/10 obrigou a desligar a VM | Diário de 21/10 |

### Por que o cronograma não absorveu isso

Esta seção é análise, não registro. O plano tinha cortes de escopo escritos: às 10h de 20/10, se persistência, monitoramento ou painel estivessem reprovados, a fila de expansão seria suspensa e o trabalho se concentraria neles. Isso protege o caminho crítico de distrações, mas não ajuda quando o próprio caminho crítico atrasa. Faltou um gatilho que dissesse o que sai ou muda (meta, escopo ou prazo) se um bloco crítico ainda estivesse reprovado perto das 14h.

## 6. O que funcionou

- **O critério não foi relaxado.** A asserção de `scripts/validate_collection.py:248` ficou como estava. Nenhuma carga foi reduzida para a rodada passar.
- **Linha de base antes de culpar os PRs.** A rodada 3 rodou os testes instáveis na `develop@8cb1e23` e mostrou que já falhavam, o que reclassificou o candidato de "não apto" para "apto para integração".
- **Parar na falha.** Nas rodadas 4 a 6 o agente de testes parou ao encontrar um erro de preparação, sem improvisar nem declarar resultado que não mediu.
- **Honestidade nos números.** Os relatórios separam o medido do inferido (`[Certo]`, `[Provável]`, `[Não medido]`), e os comentários das issues foram corrigidos para distinguir o medido em 22/10 do medido em 23/10.
- **Integridade das evidências.** Cada rodada traz `SHA256SUMS.txt`, e os hashes foram conferidos na cópia para o host.
- **Decisão sobre dependência externa.** O digest do PostgreSQL foi mantido e o validador passou a checar só o digest, em vez de trocar a imagem às pressas.

## 7. Ações corretivas

Todas alteram o processo, o ambiente ou a automação, não o comportamento de pessoas. Dono e prazo estão **[a atribuir]**: o repositório não tem essa informação, e cada item precisa de um dono único antes de entrar no quadro.

| # | Ação | Resolve | Prioridade sugerida | Prazo sugerido |
|---|---|---|---|---|
| A1 | **Checklist de preparação da VM antes de cada rodada**: o commit existe no repositório da VM, o bundle usa uma referência nomeada, `npm ci` e o `playwright install` foram feitos, o SSH responde, há memória livre no host e o roteiro tem versão para o sistema da VM | Fator 5, 7 | Alta | 28/10 |
| A2 | **Regra de aceite para issues de capacidade**: só se recomenda o aceite depois de reproduzir o cenário na VM de referência (4 vCPU, 4 GiB) com no mínimo 3 repetições. Registrar no [fluxo de trabalho do TCC](../processo/fluxo-de-trabalho-tcc.md) | Seção 4, item 2 | Alta | 03/11 |
| A3 | **Medir antes de ajustar**: quando um cenário de carga reprovar, gravar as métricas de sonda e de gravação (já expostas no status da coleta) antes de mudar qualquer parâmetro | Seção 4, itens 3 e 4 | Média | Já parcialmente feito no #43 |
| A4 | **Tratar os testes instáveis como bloqueio de confiança**: concluir a #45, incluindo o 4º teste (`test_scheduler`, 28/30) e a decisão sobre a margem entre o prazo interno de 14 s e a meta de 15 s | Fator 4 | Alta | 10/11 (Sprint 2) |
| A5 | **Gatilho de corte para o caminho crítico**: no próximo plano, definir antes qual bloco crítico sai (ou qual meta é reduzida) se ele não estiver aceito num horário combinado, com dono e decisão registrados | Seção 5, "Por que o cronograma não absorveu" | Média | Antes da Sprint 2 |
| A6 | **Versionar o escopo e o cronograma de cada sprint** em `docs/historico/` no início da sprint, para o próximo postmortem não depender da memória | Linha do tempo (lacuna de 15/10 a 18/10) | Média | 28/10 |
| A7 | **Avaliar um fluxo de carga fora do CI principal** (manual ou noturno) com a mesma configuração da VM, para que a regressão de capacidade apareça antes da integração. Custo e benefício a avaliar | Seção 4, item 1 | Baixa | Depois da `v1.0.0` |
| A8 | **Manter a fixação por digest** das imagens e o validador que ignora a tag mutável | Fator 6 | Concluída | `8661916` |

## 8. Perguntas em aberto

1. **[a confirmar]** O quadro registra foco nas issues #2, #3 e #4, a fila K01 a K15 e 42 h de capacidade. As issues #6 a #9, #14 e #15 faziam parte do compromisso de 20/10 desde o início, ou foram somadas no plano de 19/10? Quantos cartões K estavam concluídos em 20/10 às 18h?
2. **[a confirmar]** Os relatórios da rodada isolada foram gravados no host às 14:35 de 20/10, então a falha de carga é anterior a isso, perto do corte de congelamento das 14h. Qual foi a hora exata, e o que a equipe decidiu naquele momento (continuar a fila, parar para investigar, avisar o orientador)?
3. **[a confirmar]** Por que a demonstração mudou de 24/10 para 27/10, além da frase de reduzir risco no plano?
4. A causa técnica da falha de carga basta como está para o capítulo do TCC? Se não, vale um experimento controlado (por exemplo, o commit anterior ao PR #44 com as métricas do #43 ligadas) ou registrar a causa como "provável" e seguir?
5. Houve contribuição da virtualização? O stall RCU da VM pode ser reexaminado num host diferente, se houver outra máquina disponível para a #25.
6. O SSH da VM caiu em 22/10 às 23:45 sem causa conhecida. Há algum log do VirtualBox ou do convidado guardado?

## 9. Referências

- [Plano de conclusão, 20/10](../planejamento/plano-conclusao-2026-10-20.md)
- [Revisão dos achados das issues #6, #7, #8 e #14](revisao-achados-base-2026-10-20.md)
- [Coleta com persistência em lotes (#8)](coleta-lotes.md)
- [Diário de bordo, 21/10](../tcc/diario-bordo/21-10-2026.md)
- [Relatório ao orientador, 21/10](../tcc/relatorio-orientador-2026-10-21.md)
- [Plano da demonstração](../planejamento/plano-demonstracao-2026-10-27.md) e [plano de sprints pós-demo](../planejamento/plano-sprints-pos-demo.md)
- [Coleta contínua e SSE](../../engenharia/docs/09-coleta-eventos.md)
- Rodadas de VM: [isolada](../../_pacote-local/validacao-vm/rodada-isolada/RESULTADO.md), [1](../../_pacote-local/validacao-vm/rodada-2026-10-22/RESULTADO.md), [2](../../_pacote-local/validacao-vm/rodada-2026-10-22b/RESULTADO.md), [3](../../_pacote-local/validacao-vm/rodada-2026-10-22c/RESULTADO.md), [4](../../_pacote-local/validacao-vm/rodada-2026-10-22d/RESULTADO.md), [5](../../_pacote-local/validacao-vm/rodada-2026-10-22e/RESULTADO.md), [6](../../_pacote-local/validacao-vm/rodada-2026-10-22f/RESULTADO.md), [7](../../_pacote-local/validacao-vm/rodada-2026-10-22g/RESULTADO.md) e [7 retomada](../../_pacote-local/validacao-vm/rodada-2026-10-23a/RESULTADO.md)
- PRs [#43](https://github.com/Solution-Explores/SigmaTI/pull/43), [#44](https://github.com/Solution-Explores/SigmaTI/pull/44) e [#47](https://github.com/Solution-Explores/SigmaTI/pull/47); issues [#6](https://github.com/Solution-Explores/SigmaTI/issues/6), [#8](https://github.com/Solution-Explores/SigmaTI/issues/8), [#45](https://github.com/Solution-Explores/SigmaTI/issues/45) e [#46](https://github.com/Solution-Explores/SigmaTI/issues/46)
