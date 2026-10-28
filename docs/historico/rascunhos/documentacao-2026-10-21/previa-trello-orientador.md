
## Relatório e mensagem ao orientador (arquivo local)

# SigmaTI — situação para o orientador · 21/10/2026

[Certo] Entregues e encerradas no GitHub: **#2** (conflitos Compose), **#3** (credenciais/portas/versões), **#4** (configuração, CORS e timeout), **#7** (persistência), **#9** (pacote), **#14** (sondagem segura) e **#15** (painel). **#6/PR #43** e **#8/PR #44**: **validados em VM; aceite final em 23/10**, após revisão independente e integração. CI verde nos SHAs atuais. **#25**: 17 verificações de restauração em VM no mesmo host; outra máquina física pendente. **#5/#13**: critérios completos de anonimização e âncora/rotação da auditoria pendentes.

| Evidência de laboratório | develop `8cb1e23` | Candidato `ddd4840` |
|---|---:|---:|
| Regressão Python | 464/467 | **489/489** |
| Carga de 200 alvos | **0/5** | **5/5** |
| Atraso máximo / erros | aquecimento reprovado | **0,093396 s / 0** |

Fontes locais: `rodada-2026-10-22`, `rodada-2026-10-22b` e `rodada-2026-10-22c`. p95 queda→SSE ≤0,410 s nas quedas sintéticas anteriores à janela de carga. Os três testes instáveis já falhavam antes dos PRs; sonda corrigida em branch separado (30/30), sem PR. O timer da IA atrasou até 1,263 s antes do cancelamento; a causa específica do agendamento permanece inconclusiva.

**Demo: sábado, 24/10, às 9h (UTC−4); SHA congelado sexta, 23/10, às 18h.** Sete passos:
1. Arquitetura: alvo → sonda → PostgreSQL → detector → SSE → painel.
2. Perfis de acesso e recusa 403, com comando de apoio.
3. Queda TCP fictícia, incidente ao vivo, reconhecimento/resolução e métricas pela API.
4. SLO, orçamento de erros e burn rate pela API.
5. Aprovação e verificação da cadeia de auditoria.
6. Anonimização de identificadores fictícios antes da IA simulada.
7. Resultados dos testes, carga e limites do laboratório.

**Limites e riscos:** IA simulada, loopback e dados fictícios; VM no mesmo host, sem homologação externa ou operação prolongada. O prazo interno da IA é 14 s para uma meta de 15 s: a margem de 1 s pode ser excedida. Anonimização válida para o corpus avaliado. Integração, ensaios, contingência e aceite de sexta ainda pendentes. Estimativas do diário: demo **≈43%**, escopo do TCC **≈65%**.

**Decisões solicitadas:** confirmar **03/11** para #5, #13, #25 e release; autorizar expansão e validações externas como trabalho futuro; definir se #25 exige outra máquina física ou aceita VM no mesmo host; escolher a licença do repositório. #41/#42, de documentação, serão revisados após a demo.

**Mensagem sugerida**
Prezado professor,
Compartilhamos o estado do SigmaTI para a demonstração de sábado, 24/10, às 9h.
O candidato passou 489/489 testes e 5/5 cargas de 200 alvos em laboratório.
Revisão, integração e aceite final estão previstos até sexta, com congelamento às 18h.
Apresentaremos o fluxo completo com dados fictícios e IA simulada, declarando os limites.
Solicitamos sua orientação sobre o prazo de 03/11, trabalho futuro, validação da restauração e licença.
O resumo acima reúne as entregas, evidências e pendências.
Atenciosamente, equipe SigmaTI.

## Trello — textos e movimentos planejados

### https://trello.com/c/RH2Ftdst — GUIA — Issues, PRs e fluxo do Kanban

Lista: Backlog → Backlog. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Referência de processo; conferir o quadro antes do congelamento. Não representa entrega de código.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Padrão do quadro
- **ISSUE #n — entrega**: o número corresponde à issue do GitHub.
- **ISSUES #n/#m — entrega**: cartão que envolve mais de uma issue.
- **ÉPICO #31 — etapa**: coordenação, CI, instalação, demonstração ou release que abrange o projeto.
- **GUIA — assunto**: orientação, sem fingir vínculo com uma issue.

**Exemplo:** antigo K07 = testes da issue #4. Não é a issue #7 de persistência. Antigo K08 = CI/instalação; não é a issue #8 de monitoramento.

## Como ler cada cartão
O topo apresenta resumo atual, links das issues e PRs com estado confirmado. Abaixo fica o histórico com a nomenclatura anterior. Cartão concluído pode entregar só parte de uma issue (ex.: #25 local entregue, outra máquina pendente). A coluna não foi alterada por esta padronização.

## Referências atuais
- [Épico #31](https://github.com/Solution-Explores/SigmaTI/issues/31).
- [Fluxo de trabalho](https://github.com/Solution-Explores/SigmaTI/blob/develop/doc/fluxo-de-trabalho-tcc.md).
- [Plano de entrega](https://github.com/Solution-Explores/SigmaTI/blob/develop/doc/plano-conclusao-2026-10-20.md).
- [PR #41 — planejamento da VM](https://github.com/Solution-Explores/SigmaTI/pull/41): aberto.
- [PR #42 — conferência de #6/#7/#8/#14](https://github.com/Solution-Explores/SigmaTI/pull/42): aberto; registra lacunas, não as corrige.

Padronização em 20/10/2026 (UTC−4). Histórico mantido; não foram alterados responsáveis, prazos, colunas ou aceites.

---
## Histórico anterior — 📌 Guia do quadro — fluxo e acordos da equipe

GIT FLOW ADOTADO — 19/10/2026
main: versões; develop: integração; feature/*: funcionalidades; fix/*: correções; release/*: preparação; hotfix/*: urgências em produção.
Branch atual: feature/pacote. PR vigente: https://github.com/Solution-Explores/SigmaTI/pull/34 (substitui #33, fechado automaticamente pela renomeação).
Commit 7f3b5d1 publica CI e documentação; integração desse commit ainda depende da revisão do PR.
Guia: https://github.com/Solution-Explores/SigmaTI/blob/feature/pacote/doc/gitflow.md
Plano: https://github.com/Solution-Explores/SigmaTI/blob/feature/pacote/doc/plano-conclusao-2026-10-20.md
Esta orientação substitui o antigo desenvolvimento direto na dev. Referências abaixo preservam o histórico.

---
FLUXO DE TRABALHO
Backlog → A fazer → Em andamento → Revisão e testes → Concluído.

Backlog: ideias, demandas futuras e itens que ainda precisam de refinamento. Este cartão é uma referência de processo.
A fazer: itens priorizados da sprint; confirmar objetivo, responsável, dependências e critérios de aceite antes de iniciar.
Em andamento: trabalho iniciado. Limite recomendado: 1 cartão por pessoa, até 3 no total.
Revisão e testes: implementação pronta, aguardando revisão e validação. Limite recomendado: 2 cartões; priorizar concluir revisões antes de puxar trabalho novo.
Concluído: critérios de aceite atendidos, revisão e testes registrados, documentação pertinente atualizada.

PADRÃO DOS CARTÕES
Título: ID — verbo + entrega.
Descrição: objetivo, responsável e prazo, dependências, critérios de conclusão e referências.
Vincular issue, PR e evidências. Não marcar como concluído apenas por ter terminado a implementação.
Quando bloqueado, registrar motivo, dependência e próximo passo na descrição; manter na etapa real.
Etiquetas por área: Infraestrutura, API, Qualidade e testes, Documentação e entrega. A ordem K01–K15 expressa a fila de prioridade da sprint; as etiquetas antigas foram preservadas para manter o histórico.

SPRINT 15–20/10/2026
Vinícius = Pessoa 1; Iohan = Pessoa 2; Joyce = Pessoa 3.
Joyce disponível apenas 08h–12h. Capacidade: 42 h; implementação: 33,6 h após reserva de 20%.
K01 e K02 liberados para iniciar. Demais dependências precisam ser confirmadas no planejamento detalhado.
Foco nas issues #2, #3 e #4. K16 e K17 são adicionais sem escopo informado; não foram criadas tarefas fictícias.
Prazos de manhã registrados às 12h; demais às 23h59.

ROTINA RECOMENDADA
Revisar diariamente bloqueios, prazos e limites de trabalho. Atualizar os cartões ao mudar de etapa. Ao encerrar a sprint, revisar pendências e replanejar com a equipe.

PENDÊNCIA DE CADASTRO
Iohan e Joyce ainda precisam estar disponíveis como membros do quadro para vinculação dos cartões. Seus nomes constam nas descrições.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base remota conferida: dev@900dcc409e72fd973be12a76330233ce163f62ed.
K01–K04: Revisão e testes, aguardando outro integrante e integração aprovada.
K08 e K14: Em andamento, com entregas parciais de CI/instruções e README.
K05–K07, K09–K13 e K15: A fazer; avanços parciais e próximos passos detalhados em cada cartão.
Issues #2, #3 e #4 continuam abertas; main/docker-compose.yml ainda contém conflitos. Nenhuma tarefa da sprint foi promovida a Concluído sem evidência de aprovação e entrega.
Os resultados de testes foram consultados nas evidências e comentários das issues; não foram reexecutados nesta conferência. Os endpoints consultados não confirmaram checks do último commit; consultar as execuções vinculadas à issue #3 antes da aprovação.
Base: [https://github.com/Solution-Explores/SigmaTI/commit/900dcc409e72fd973be12a76330233ce163f62ed](https://github.com/Solution-Explores/SigmaTI/commit/900dcc409e72fd973be12a76330233ce163f62ed "‌")
Evidências: [https://github.com/Solution-Explores/SigmaTI/tree/900dcc409e72fd973be12a76330233ce163f62ed/specs](https://github.com/Solution-Explores/SigmaTI/tree/900dcc409e72fd973be12a76330233ce163f62ed/specs "‌")
Fluxo de referência: [https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/doc/fluxo-de-trabalho-tcc.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/doc/fluxo-de-trabalho-tcc.md "‌")

### https://trello.com/c/fDovwdzt — ÉPICO #31 — Expansão: runbooks, IA e relatórios

Lista: Backlog → Backlog. Prazo nativo: 2026-11-03T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Expansão (#10, #16–#19, #21, #22, #30): trabalho futuro, sujeito ao orientador em 24/10; sem PR de implementação aberto confirmado.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 03/11/2026 às 18h — revisão de planejamento (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Planejamento de expansão. Cada issue tem seu próprio aceite; nenhuma implementação nova é declarada por este cartão.

## Issues do GitHub
- [#31 — Épico: evoluir o SIGMA para um sistema de engenharia da computação](https://github.com/Solution-Explores/SigmaTI/issues/31) — aberta.
- [#21 — Herdar do Sentinel: biblioteca de runbooks (conteúdo + execução auditada)](https://github.com/Solution-Explores/SigmaTI/issues/21) — aberta.
- [#22 — Herdar do Sentinel: reteste automático para confirmar a resolução do incidente](https://github.com/Solution-Explores/SigmaTI/issues/22) — aberta.
- [#18 — Herdar do Sentinel: triagem de incidente por IA com cadeia de provedores e fallback](https://github.com/Solution-Explores/SigmaTI/issues/18) — aberta.
- [#17 — Herdar do Sentinel: postmortem estruturado com linha do tempo e 5 porquês](https://github.com/Solution-Explores/SigmaTI/issues/17) — aberta.
- [#16 — n8n: relatório semanal automático (MTTD/MTTA/MTTR e orçamento de erros) — RF06](https://github.com/Solution-Explores/SigmaTI/issues/16) — aberta.
- [#10 — Cobrir deriva lenta: CUSUM e Page-Hinkley](https://github.com/Solution-Explores/SigmaTI/issues/10) — aberta.
- [#30 — Verificação formal da máquina de estados de aprovação e dos invariantes da cadeia](https://github.com/Solution-Explores/SigmaTI/issues/30) — aberta.
- [#19 — Herdar do Sentinel: vigilância de mudança de superfície da rede (diff de snapshots) — versão defensiva](https://github.com/Solution-Explores/SigmaTI/issues/19) — aberta.
- [#20 — Herdar do Sentinel: Production Readiness Review (PRR) para sistemas críticos do hospital](https://github.com/Solution-Explores/SigmaTI/issues/20) — aberta.
- [#24 — Herdar do Sentinel: mapa de conformidade (LGPD, ISO/IEC 27001) ligado a evidências](https://github.com/Solution-Explores/SigmaTI/issues/24) — aberta.

## PRs e referências
Sem PR exclusivo confirmado para esta etapa. Commits, CI e evidências continuam no histórico abaixo.

## Organização
- Coluna mantida: Backlog.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — Expansão — Runbooks, IA resiliente e relatórios

PLANEJADO — implementação não iniciada nesta publicação.

Fila fixa após fundação/monitoramento/painel aprovados: #21/#22 → #18/#17 → #16 → #10/#30 → #19/#20/#24. Cada bloco exige cenário completo e evidências. Suspender expansão às 10h de 20/10 se o fluxo principal estiver reprovado; congelar funcionalidades às 14h. Envio externo desabilitado na demonstração.

Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9
Disponibilidade de responsável não confirmada; não atribuir conclusão sem evidência.

### https://trello.com/c/fxR7XxOZ — ÉPICO #31 — Experimentos e validações externas

Lista: Backlog → Backlog. Prazo nativo: 2026-11-03T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Validações externas (#11, #12, #20, #24, #26–#29): trabalho futuro; dependências físicas/institucionais não atendidas. #25 tem acompanhamento separado.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 03/11/2026 às 18h — revisão de planejamento (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Consolidar dependências externas, experimentos e hardware. Não confundir validações locais com homologação externa.

## Issues do GitHub
- [#31 — Épico: evoluir o SIGMA para um sistema de engenharia da computação](https://github.com/Solution-Explores/SigmaTI/issues/31) — aberta.
- [#11 — Experimentos E2–E5: latência ponta a ponta, burn rate real, fuzzing da cadeia e RNF04](https://github.com/Solution-Explores/SigmaTI/issues/11) — aberta.
- [#12 — Coletar RTT real por 2 semanas e recalibrar os detectores (validade externa do E1)](https://github.com/Solution-Explores/SigmaTI/issues/12) — aberta.
- [#25 — Herdar do Sentinel: scripts de implantação, backup e smoke test E2E (RNF06)](https://github.com/Solution-Explores/SigmaTI/issues/25) — aberta.
- [#26 — Sonda embarcada (ESP32 / Raspberry Pi) por VLAN com envio autenticado](https://github.com/Solution-Explores/SigmaTI/issues/26) — aberta.
- [#27 — Impacto da sincronização de relógio (NTP × PTP) no MTTD medido](https://github.com/Solution-Explores/SigmaTI/issues/27) — aberta.
- [#28 — Modelo de filas do pipeline alerta → fila → IA e comparação com E2/E5](https://github.com/Solution-Explores/SigmaTI/issues/28) — aberta.
- [#29 — Telemetria SNMP/NetFlow como entrada dos detectores (além de TCP)](https://github.com/Solution-Explores/SigmaTI/issues/29) — aberta.
- [#30 — Verificação formal da máquina de estados de aprovação e dos invariantes da cadeia](https://github.com/Solution-Explores/SigmaTI/issues/30) — aberta.
- [#20 — Herdar do Sentinel: Production Readiness Review (PRR) para sistemas críticos do hospital](https://github.com/Solution-Explores/SigmaTI/issues/20) — aberta.
- [#24 — Herdar do Sentinel: mapa de conformidade (LGPD, ISO/IEC 27001) ligado a evidências](https://github.com/Solution-Explores/SigmaTI/issues/24) — aberta.

## PRs e referências
Sem PR exclusivo confirmado para esta etapa. Commits, CI e evidências continuam no histórico abaixo.

## Organização
- Coluna mantida: Backlog.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — Conclusão integral — Experimentos e dependências externas

PLANEJADO — implementação não iniciada nesta publicação.

Conferir individualmente #2–#5/#9 e K07–K15; concluir requisitos restantes de #6/#7, #8/#15–#22, #13/#14/#23/#25 e #10/#11/#28/#30. #12/#27: mínimo de 14 dias e medições entre máquinas. #26/#29: Raspberry Pi e SNMPv3 com ensaio físico. #20/#24: matriz de evidências e avaliação institucional quando disponível. #31 depende dos aceites ou redução de escopo aprovada. Recursos externos ainda não confirmados.

Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9
Disponibilidade de responsável não confirmada; não atribuir conclusão sem evidência.

### https://trello.com/c/YGVH2Pg9 — ÉPICO #31 — Plano de entrega e release

Lista: A fazer → A fazer. Prazo nativo: 2026-11-03T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Retomada já concluída. Demo em 24/10 às 9h, integração #43 em 22/10 e #44 em 23/10; aceite e congelamento em 23/10 às 18h. Demo ≈43%, escopo TCC ≈65%, estimativas do diário; release proposta para 03/11.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 03/11/2026 às 18h — proposta ao orientador (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Ponto de retomada — 20/10/2026 (Manaus)
[Certo] Preparada transferência do laboratório do estágio para a máquina de casa. O usuário informou já ter copiado a VM e os demais arquivos para o pendrive; importação e integridade no destino ainda não foram conferidas.

Código de referência: develop@8cb1e23b0e83066e52d3f81dd7ef05ce82dfc93c. Nenhum código versionado foi modificado nesta investigação.
- Restauração na VM do mesmo host: 17 verificações aprovadas. Outra máquina física permanece pendente para #25.
- Regressão: 466/467 testes Python aprovados; uma falha de carga em #8.
- API: 20 verificações; frontend: build/lint e 16 testes aprovados; teste de navegador operacional aprovado.
- E6: 59 mensagens / 53 identificadores; nenhum vazamento observado nesse corpus, sem generalizar para dados reais.
- Testes parados por solicitação do usuário; contêiner descartável removido e banco de referência preservado.

Pacote local preparado: D:\\sigma-dev\\evidencias-para-casa.zip (aproximadamente 86 KB), com relatórios de origem, sincronização GitHub/Trello e validação na VM, LEIA-ME e SHA256SUMS. Sem código, credenciais, dump ou logs brutos. O pacote foi preparado; sua cópia ao pendrive ainda não foi confirmada.

Ordem em casa: adicionar a VM existente no VirtualBox → conferir arquivos/commit e evidências → retomar somente quando solicitado → investigar/corrigir carga de 200 alvos → repetir regressão e aceite → validar restauração no outro host → revisar pendências antes de preparar release/main. Copiar/importar a VM não comprova nova restauração nem homologação hospitalar.

---
## Registro anterior (preservado; consultar atualização acima)

## Resumo atual
Plano geral. Base integrada à develop; publicação de release/main e aceites externos continuam separados.

## Issues do GitHub
- [#31 — Épico: evoluir o SIGMA para um sistema de engenharia da computação](https://github.com/Solution-Explores/SigmaTI/issues/31) — aberta.

## PRs e referências
- [PR #34 — Empacotar sigma_eng e remover imports pelo caminho engenharia (#9)](https://github.com/Solution-Explores/SigmaTI/pull/34) — integrado à develop.
- [PR #40 — feat: backup autenticado, restauração e smoke RNF06 (#25)](https://github.com/Solution-Explores/SigmaTI/pull/40) — integrado à develop.
- [PR #41 — docs: planejamento da validacao #25 em VM VirtualBox](https://github.com/Solution-Explores/SigmaTI/pull/41) — aberto; aguardando integração.
- [PR #42 — docs: conferir aceite de #6 #7 #8 #14 e registrar lacunas](https://github.com/Solution-Explores/SigmaTI/pull/42) — aberto; aguardando integração.

## Organização
- Coluna mantida: A fazer.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — Plano de entrega — 20/10 às 18h (Manaus)

PR #34 RESOLVIDO — 19/10/2026
Integrado à develop em 5d848a9e102ffa8a0810412ca772c37e3e3b1947.
PR: https://github.com/Solution-Explores/SigmaTI/pull/34
Revisão técnica: Codex, a pedido do usuário; não houve revisão independente por outro integrante.
Seis checks do PR aprovados; 77 testes locais focados aprovados; pip check aprovado.
CI do merge aprovado:
https://github.com/Solution-Explores/SigmaTI/actions/runs/39323374546
https://github.com/Solution-Explores/SigmaTI/actions/runs/39323374588
Main não alterada. Próxima frente: #6/#7; publicação de release ainda depende de aceite próprio.

---
HISTÓRICO
GIT FLOW ADOTADO — 19/10/2026
main: versões; develop: integração; feature/*: funcionalidades; fix/*: correções; release/*: preparação; hotfix/*: urgências em produção.
Branch atual: feature/pacote. PR vigente: https://github.com/Solution-Explores/SigmaTI/pull/34 (substitui #33, fechado automaticamente pela renomeação).
Commit 7f3b5d1 publica CI e documentação; integração desse commit ainda depende da revisão do PR.
Guia: https://github.com/Solution-Explores/SigmaTI/blob/feature/pacote/doc/gitflow.md
Plano: https://github.com/Solution-Explores/SigmaTI/blob/feature/pacote/doc/plano-conclusao-2026-10-20.md
Esta orientação substitui o antigo desenvolvimento direto na dev. Referências abaixo preservam o histórico.

---
Plano publicado: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Commit: 514838f — branch feat/9-pacote-sigma-eng; PR #33 https://github.com/Solution-Explores/SigmaTI/pull/33.

ESTADO VERIFICADO
PR #32 integrado à dev em 086129c; PR #33 implementado, CI anterior aprovado, aguardando revisão/integração. Esta publicação acrescenta documentação; não implementa os blocos futuros.

ORDEM
1. Revisar e integrar #9/PR #33; validar CI na dev.
2. #6/#7: PostgreSQL, Argon2id, sessões revogáveis, migrações e recuperação.
3. #14 e parte de #13: conectar ao IP validado e auditoria concorrente.
4. #8: scheduler, medições, incidentes persistidos e SSE autenticado.
5. #15: painel com dados reais e perfis.
6. Parte de #25: backup/restauração local comprovados.
7. Expansão: #21/#22 → #18/#17 → #16 → #10/#30 → #19/#20/#24.

LIMITES EM 20/10 (MANAUS)
10h: suspender expansão se fundação/monitoramento/painel falharem.
14h: congelar funcionalidades. 14–17h: testes/correções. 17–18h: roteiro, evidências e entrega.
Prazo da demonstração, não promessa de encerrar todas as issues. Trabalho incompleto fica fora da versão demonstrada.

ACEITE
Fluxo alvo → falha → incidente persistido → painel → reconhecimento/resolução; autenticação/RBAC; retomada após reinício; privacidade; backup restaurado; testes Python, PostgreSQL real, navegador, pacote, frontend e CI.

DEPENDÊNCIAS
Somente Windows/Docker local confirmado. #12 exige pelo menos 14 dias; hardware, outra máquina e validação hospitalar continuam externos. #31 só encerra conforme requisitos ou redução de escopo aprovada.
Não há nova aprovação de merge ou atribuição de disponibilidade humana neste cartão.

### https://trello.com/c/nFmreK27 — Atualizar o miro

Lista: A fazer → A fazer. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Cartão sem issue específica ou PR identificado. Confirmar necessidade de atualização do material; não há evidência para declarar a tarefa entregue. Link #31 usado somente como coordenação.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h — triagem (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)



### https://trello.com/c/zOyTl0LP — ÉPICO #31 — Consolidar aceite e preparar release

Lista: A fazer → A fazer. Prazo nativo: 2026-11-03T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Consolidação/release ainda pendente. Aceite da demo em 23/10; release v1.0.0 proposta para 03/11. Não confundir aceite da demo com publicação de release.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 03/11/2026 às 18h — proposta ao orientador (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Consolidar critérios, evidências e pendências antes de preparar a release. A conferência #42 não corrige a auditoria da #6.

## Issues do GitHub
- [#31 — Épico: evoluir o SIGMA para um sistema de engenharia da computação](https://github.com/Solution-Explores/SigmaTI/issues/31) — aberta.
- [#5 — Anonimização LGPD robusta e fail-closed (RF05)](https://github.com/Solution-Explores/SigmaTI/issues/5) — aberta.
- [#6 — Autenticação e perfis (RF07): login com JWT de sessão e RBAC](https://github.com/Solution-Explores/SigmaTI/issues/6) — aberta.
- [#7 — Persistência em PostgreSQL: alvos, medições, incidentes, aprovações e execuções de runbook](https://github.com/Solution-Explores/SigmaTI/issues/7) — aberta.
- [#8 — Sondagem contínua com scheduler e alertas em tempo real via SSE (RF01)](https://github.com/Solution-Explores/SigmaTI/issues/8) — aberta.
- [#14 — Sonda: conectar ao IP já validado (mitigar DNS rebinding / TOCTOU)](https://github.com/Solution-Explores/SigmaTI/issues/14) — aberta.
- [#25 — Herdar do Sentinel: scripts de implantação, backup e smoke test E2E (RNF06)](https://github.com/Solution-Explores/SigmaTI/issues/25) — aberta.

## PRs e referências
- [PR #42 — docs: conferir aceite de #6 #7 #8 #14 e registrar lacunas](https://github.com/Solution-Explores/SigmaTI/pull/42) — aberto; aguardando integração.

## Organização
- Coluna mantida: A fazer.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K15 — Conferir aceite, preparar entrega e atualizar status

ATUALIZAÇÃO DO PLANO — 19/10/2026
Entrega-alvo: 20/10 às 18h (Manaus). Até 17h: validação; 17–18h: roteiro, SHA, evidências e status individual das issues. Não encerrar pendências externas nem funcionalidades sem aceite.
Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9

---
HISTÓRICO PRESERVADO
INTEGRAÇÃO NA DEV — 19/10/2026

PR #32 integrado na dev em 086129c9b8dd119d72877f493e1828ef2a46c949. O usuário autorizou explicitamente 'Autorizar o merge na dev' ao ser perguntado sobre dispensar nesta entrega a revisão por outro integrante. Revisão e testes foram executados pelo Codex; não se atribui aprovação independente a outra pessoa. A exceção é específica do PR #32.

Validação na dev: árvore idêntica ao head revisado; novo aceite HTTP passou 20 verificações (timeout 14,031 s). CI API e infraestrutura aprovados no commit integrado.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381540
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381631
PR integrado: https://github.com/Solution-Explores/SigmaTI/pull/32
Registro: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/specs/011-recuperacao-sprint/integracao-dev.md

Main e encerramento final permanecem pendentes; issues #5/#6 continuam parciais. Próxima entrega implementada: issue #9, PR #33 em revisão, ainda sem integração.

HISTÓRICO ANTERIOR PRESERVADO

OBJETIVO
Conferir aceite, preparar entrega e atualizar status

RESPONSÁVEL E PRAZO
Vinícius (Pessoa 1) — 20/10/2026 / noite.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K15.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base: dev@900dcc4.
A FAZER. Issues #2, #3 e #4 permanecem abertas. Não há aprovação de outro integrante nem integração das correções à main. Preparar entrega somente após aceite completo e atualização dos registros.
Issues: [https://github.com/Solution-Explores/SigmaTI/issues](https://github.com/Solution-Explores/SigmaTI/issues "‌")
Fluxo: [https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/doc/fluxo-de-trabalho-tcc.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/doc/fluxo-de-trabalho-tcc.md "‌")
Testes citados são registros do repositório; não reexecutados nesta conferência.

### https://trello.com/c/taEBIf5c — ISSUE #6 — Autenticação, sessões e auditoria de login

Lista: Revisão e testes → Revisão e testes. Prazo nativo: 2026-10-22T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] PR #43 aberto, fix/base-issues@8662ea9, CI verde. Auditoria concorrente 7/7; regressão 476/478 (E2 depende #44; DNS temporal). Validado em VM; aceite final em 23/10. Revisão independente até 22/10 às 8h; integração prevista 22/10.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 22/10/2026 às 18h (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/6
- PR aberto: https://github.com/Solution-Explores/SigmaTI/pull/43
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Pronto para revisão — 20/10/2026 (Manaus)
[Certo] PR #43 foi disponibilizado para revisão após os checks de a97fe1b passarem no push e no PR. Correções de integridade concorrente e leitura atualizada da auditoria testadas em Windows/Linux. Sem merge automático; #6 permanece aberta até revisão e integração.
https://github.com/Solution-Explores/SigmaTI/pull/43
O desenvolvimento da coleta está isolado no PR #44, dependente deste PR. #7/#14 encerradas com aprovação explícita do usuário.

---
## Revisão — 20/10/2026 (Manaus)
[Certo] Correção da auditoria preservada no PR #43, commit a97fe1b: lock entre processos Windows/Linux, leitura atualizada e coerente da trilha, caminho padrão único e erro seguro na indisponibilidade da auditoria. Testes locais de concorrência/endpoint e smoke Linux aprovados. Todos os checks de push e PR desse commit concluíram com sucesso.
https://github.com/Solution-Explores/SigmaTI/pull/43
Sem integração à develop/main e sem encerramento da #6 nesta revisão. Desenvolvimento posterior de capacidade da #8 isolado na branch fix/coleta; os checks acima não validam essas mudanças novas.

---
## Resumo atual
JWT, PostgreSQL e RBAC entregues. Falta corrigir escrita concorrente da trilha JSONL e verificação com leitura desatualizada. PR #42 registra o diagnóstico; não implementa a correção.

## Issues do GitHub
- [#6 — Autenticação e perfis (RF07): login com JWT de sessão e RBAC](https://github.com/Solution-Explores/SigmaTI/issues/6) — aberta.

## PRs e referências
- [PR #35 — Persistir usuários e sessões revogáveis em PostgreSQL (#6/#7)](https://github.com/Solution-Explores/SigmaTI/pull/35) — integrado à develop.
- [PR #42 — docs: conferir aceite de #6 #7 #8 #14 e registrar lacunas](https://github.com/Solution-Explores/SigmaTI/pull/42) — aberto; aguardando integração.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — Issue 06 - Autenticação e perfis (RF07): login com JWT de sessão e RBAC

PENDÊNCIAS CONFIRMADAS NA AUDITORIA — CONFERÊNCIA DE 20/10/2026

JWT, Argon2id/PostgreSQL, limite de login e matrizes 401/403 implementados. Duas lacunas reproduzidas: instâncias independentes podem quebrar a cadeia JSONL; login gravou 1 entrada mas endpoint de verificação retornou 0 por snapshot antigo. Falta coordenação entre escritores/processos, leitura corrente e regressões. Implementação não foi corrigida nesta conferência. RBAC de endpoints não comprova rotação de chaves, relatórios ou autorização no n8n externo.
Issue: https://github.com/Solution-Explores/SigmaTI/issues/6#issuecomment-6293320837

PR da conferência: https://github.com/Solution-Explores/SigmaTI/pull/42
Relatório: doc/conferencia-issues-6-7-8-14.md, base develop@8cb1e23. CI integrado: 467 testes PG15 aprovados; a suíte existente não cobre os defeitos novos da auditoria. Diagnóstico sintético reproduzido, sem dados operacionais nem alteração em runtime. Issue mantida aberta; revisão técnica sem revisor humano independente atribuído.

--- Histórico anterior ---
PR #35 INTEGRADO COM AUTORIZAÇÃO — 19/10/2026
Usuário autorizou expressamente o merge nesta conversa. Integrado à develop em 27d2b552d361deceb3650ba2a47ead959b0ab6bd, com proteção do head revisado 31471da. Revisão técnica/correções pelo Codex; nenhuma revisão independente atribuída a outro integrante. Main não alterada.
CI do merge aprovado:
https://github.com/Solution-Explores/SigmaTI/actions/runs/39345514086
https://github.com/Solution-Explores/SigmaTI/actions/runs/39345514065
Usuários/sessões PostgreSQL, Argon2id, migrações e revogação/recuperação integrados. Próximo incremento #7 em codex/estado-operacional: estado operacional, retenção e recuperação. Issue #6 não encerrada automaticamente; consolidar seus critérios e registros na preparação da entrega.

---
HISTÓRICO
REVISÃO DO PR #35 CONCLUÍDA — 19/10/2026
PR: https://github.com/Solution-Explores/SigmaTI/pull/35
Head 31471daff15db88e94f9624177e1bc441be9a632. Corrigidos bloqueio do loop nas rotas de usuários, auditoria prematura de sucesso, rehash concorrente, login anterior à desativação/reativação e validação de entradas administrativas.
Local: 109 testes aprovados. CI PostgreSQL 15: 392 testes aprovados sem falhas/ignorados, 80,48 s. Aceite HTTP, E6, build/lint, navegador, pacote e infraestrutura aprovados no novo head.
CI: https://github.com/Solution-Explores/SigmaTI/actions/runs/39345018071
Infra: https://github.com/Solution-Explores/SigmaTI/actions/runs/39345018063
Relatório: https://github.com/Solution-Explores/SigmaTI/blob/31471da/specs/013-identidades-postgres/revisao.md
Implementação/revisão técnica pelo Codex; pronto para integração após aprovação, sem merge ou revisão independente atribuída. #6/#7 permanecem abertas; persistência operacional, auditoria transacional e limitação distribuída não foram entregues neste incremento. Etapa atual do cartão preservada.

---
HISTÓRICO
ATUALIZAÇÃO DO PLANO — 19/10/2026
Próxima implementação: #6/#7, Argon2id e sessões revogáveis no PostgreSQL. A autenticação atual é parcial; não encerrar #6 antes de migrações, RBAC e retomada após reinício demonstrados.
Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9

---
HISTÓRICO PRESERVADO
INTEGRAÇÃO NA DEV — 19/10/2026

PR #32 integrado na dev em 086129c9b8dd119d72877f493e1828ef2a46c949. O usuário autorizou explicitamente 'Autorizar o merge na dev' ao ser perguntado sobre dispensar nesta entrega a revisão por outro integrante. Revisão e testes foram executados pelo Codex; não se atribui aprovação independente a outra pessoa. A exceção é específica do PR #32.

Validação na dev: árvore idêntica ao head revisado; novo aceite HTTP passou 20 verificações (timeout 14,031 s). CI API e infraestrutura aprovados no commit integrado.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381540
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381631
PR integrado: https://github.com/Solution-Explores/SigmaTI/pull/32
Registro: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/specs/011-recuperacao-sprint/integracao-dev.md

Main e encerramento final permanecem pendentes; issues #5/#6 continuam parciais. Próxima entrega implementada: issue #9, PR #33 em revisão, ainda sem integração.

HISTÓRICO ANTERIOR PRESERVADO

ATUALIZAÇÃO — 19/10/2026 — ENTREGA PARCIAL PARA REVISÃO

Sessões revogadas no logout e invalidadas no reinício; usuário inativo/papel alterado perde acesso. Chave JWT obrigatória carregada após .env; sem contas padrão ou bypass; usuários por arquivo de hashes local. Login/me/logout no painel aprovado. PostgreSQL, Argon2id/bcrypt e operação com várias instâncias permanecem pendentes. Issue continua aberta.

PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Evidências: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/evidencias.md
CI da implementação: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376074

Execução e revisão técnica pelo Codex; não se declara revisão independente ou homologação hospitalar.

HISTÓRICO PRESERVADO

## Contexto

Nenhuma rota exige autenticação. O README define três perfis (Suporte N1, Analista de Redes, Gestor de TI) e uma matriz de permissões. As rotas `/api/eng/*` do núcleo de engenharia também precisam dessa proteção antes de sair do laboratório.

## Herdar do Sentinel Vigilark

Fluxo de login que devolve **JWT de sessão com expiração** (e não a chave permanente do servidor), e a cobertura de testes de sessão (`routers/auth` e `test_session_auth`).

## Proposta

- Usuários em PostgreSQL com senha em hash (Argon2id/bcrypt); papéis `suporte_n1`, `analista_redes`, `gestor_ti` (os mesmos de `approvals.py`).
- Dependência FastAPI `exige_papel("analista_redes")` aplicada à matriz do README.
- Limite de tentativas de login e registro de login/logout na `AuditChain`.

## Critérios de aceite

- 401 sem token, 403 com papel insuficiente, para cada linha da matriz
  Token expira; chave permanente nunca é devolvida
  Testes automatizados da matriz completa

**Referência:** requisito RF07; `engenharia/sigma_eng/approvals.py` (papéis)

### https://trello.com/c/WzIvGyKq — ISSUE #5 — Anonimização e bloqueio de dados sensíveis

Lista: Revisão e testes → A fazer. Prazo nativo: 2026-11-03T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] #5 aberta; etapa completa ainda pendente e sem PR aberto exclusivo. Completar critérios, casos adversariais e relatório recall/precisão; resultados do corpus sintético não valem para dados reais. Regra de revisão exige PR aberto: retorna para A fazer.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 03/11/2026 às 18h — proposta ao orientador (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/5
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Correções integradas no PR #32. Issue ainda aberta; testes sintéticos não garantem anonimização universal ou aceite institucional.

## Issues do GitHub
- [#5 — Anonimização LGPD robusta e fail-closed (RF05)](https://github.com/Solution-Explores/SigmaTI/issues/5) — aberta.

## PRs e referências
- [PR #32 — Correções de autenticação, painel e anonimização](https://github.com/Solution-Explores/SigmaTI/pull/32) — integrado à develop.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — Issue 05 - Anonimização LGPD robusta e fail-closed (RF05)

INTEGRAÇÃO NA DEV — 19/10/2026

PR #32 integrado na dev em 086129c9b8dd119d72877f493e1828ef2a46c949. O usuário autorizou explicitamente 'Autorizar o merge na dev' ao ser perguntado sobre dispensar nesta entrega a revisão por outro integrante. Revisão e testes foram executados pelo Codex; não se atribui aprovação independente a outra pessoa. A exceção é específica do PR #32.

Validação na dev: árvore idêntica ao head revisado; novo aceite HTTP passou 20 verificações (timeout 14,031 s). CI API e infraestrutura aprovados no commit integrado.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381540
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381631
PR integrado: https://github.com/Solution-Explores/SigmaTI/pull/32
Registro: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/specs/011-recuperacao-sprint/integracao-dev.md

Main e encerramento final permanecem pendentes; issues #5/#6 continuam parciais. Próxima entrega implementada: issue #9, PR #33 em revisão, ainda sem integração.

HISTÓRICO ANTERIOR PRESERVADO

ATUALIZAÇÃO — 19/10/2026 — ENTREGA PARCIAL PARA REVISÃO

E6 corrigido: 56 mensagens e 50 identificadores anotados individualmente, sem vazamentos observados neste corpus; bloqueio seguro separado da transformação. Corrigidos CPF sem rótulo, IPv6 abreviado e nomes/hostnames. Auditoria de falha não contém texto bruto. Métrica anterior podia aprovar remoção parcial. Issue permanece aberta para revisão completa; resultado não demonstra anonimização universal.

PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Evidências: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/evidencias.md
CI da implementação: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376074

Execução e revisão técnica pelo Codex; não se declara revisão independente ou homologação hospitalar.

HISTÓRICO PRESERVADO

## Contexto

`anonimizar_dados` cobre apenas IPv4 e o literal `dr.joao`. O README (RF05) promete: IPs → sub-redes, equipamentos → categorias, remoção de nomes e identificadores médicos, e **"se o filtro falhar, nada é enviado"**. Hoje, se a função levantar exceção, o fluxo não é interrompido de forma controlada.

## Proposta

- Módulo `anonimizador` com regras testáveis: IPv4/IPv6 → sub-rede (/24), MAC, hostname → categoria, e-mail, CPF/CNS, número de prontuário, nomes (lista configurável + heurística).
- **Fail-closed**: exceção ou detecção residual (reexecutar os detectores sobre a saída) ⇒ não enviar e registrar na trilha de auditoria.
- Corpus de teste sintético com casos positivos e negativos; medir **recall** de PII (meta ≥ 99% no corpus) e falsos positivos.
- Novo experimento (E6) com os números para o TCC.

## Critérios de aceite

- [ ] Testes cobrem cada tipo de identificador
- [ ] Falha injetada no anonimizador ⇒ nenhuma chamada externa
- [ ] Relatório de recall/precisão em `resultados/`

**Referência:** `engenharia/docs/05-seguranca-e-pendencias.md` (B6, B7); requisito RF05

### https://trello.com/c/9tWbeAYN — ISSUES #4/#5/#6 — Corrigir achados da API e autenticação

Lista: Revisão e testes → Revisão e testes. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] PR #32 integrado entregou parte de #4/#5/#6. #4 encerrada; #5 e #6 abertas. Correção de auditoria #43 aberta, com revisão independente pendente; não declarar o escopo conjunto concluído.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/6
- PR aberto: https://github.com/Solution-Explores/SigmaTI/pull/43
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Etapa histórica de correções do aceite, integrada no PR #32. As novas lacunas da auditoria da #6 estão descritas no PR #42 e não foram corrigidas por essa entrega anterior.

## Issues do GitHub
- [#4 — main.py: chave de API por variável de ambiente, CORS restrito, chamada assíncrona com timeout](https://github.com/Solution-Explores/SigmaTI/issues/4) — encerrada.
- [#5 — Anonimização LGPD robusta e fail-closed (RF05)](https://github.com/Solution-Explores/SigmaTI/issues/5) — aberta.
- [#6 — Autenticação e perfis (RF07): login com JWT de sessão e RBAC](https://github.com/Solution-Explores/SigmaTI/issues/6) — aberta.

## PRs e referências
- [PR #32 — Correções de autenticação, painel e anonimização](https://github.com/Solution-Explores/SigmaTI/pull/32) — integrado à develop.
- [PR #42 — docs: conferir aceite de #6 #7 #8 #14 e registrar lacunas](https://github.com/Solution-Explores/SigmaTI/pull/42) — aberto; aguardando integração.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K11 — Corrigir achados da API

INTEGRAÇÃO NA DEV — 19/10/2026

PR #32 integrado na dev em 086129c9b8dd119d72877f493e1828ef2a46c949. O usuário autorizou explicitamente 'Autorizar o merge na dev' ao ser perguntado sobre dispensar nesta entrega a revisão por outro integrante. Revisão e testes foram executados pelo Codex; não se atribui aprovação independente a outra pessoa. A exceção é específica do PR #32.

Validação na dev: árvore idêntica ao head revisado; novo aceite HTTP passou 20 verificações (timeout 14,031 s). CI API e infraestrutura aprovados no commit integrado.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381540
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381631
PR integrado: https://github.com/Solution-Explores/SigmaTI/pull/32
Registro: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/specs/011-recuperacao-sprint/integracao-dev.md

Main e encerramento final permanecem pendentes; issues #5/#6 continuam parciais. Próxima entrega implementada: issue #9, PR #33 em revisão, ainda sem integração.

HISTÓRICO ANTERIOR PRESERVADO

REVISÃO TÉCNICA ADICIONAL — 19/10/2026

PR #32 pronto para revisão da equipe. Commit 7496564c1dd78f721d5c5c5dbfa6a0951b1c0c50 publicado; checkout limpo. Corrigidos: sobrenomes preservados pela sanitização, sessões antigas após recriar conta e limites de login ignorados no .env. Aceite Docker ampliado com escuta direta do Zabbix antes/depois da recriação.

Validação: 369 testes Python sem falhas/ignorados; 20 verificações HTTP (timeout 14,032 s); 3 cenários Chromium; build/lint; E6 com 53 identificadores em 59 mensagens; 23 verificações Docker com limpeza código 0. Política: 32 verificações de credenciais, 12 cenários de infraestrutura e quatro manifests oficiais aprovados. IA simulada e dados fictícios.

CI remoto do commit: API aprovado https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752713 ; infraestrutura aprovada https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752750 .
PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Relatório: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/revisao-tecnica.md

Revisão técnica do Codex concluída. Aprovação de OUTRO integrante permanece pendente conforme o fluxo do repositório. Não houve merge dev/main, homologação hospitalar ou fechamento de issues. #5/#6 continuam parciais.

HISTÓRICO ANTERIOR PRESERVADO

ATUALIZAÇÃO — 19/10/2026 — CORREÇÃO PARA REVISÃO

CORS autenticado, login/me/logout no painel, revogação por jti, chave JWT obrigatória e arquivo de hashes. Sem contas automáticas/bypass. Aceite HTTP: 20 verificações; navegador: 3 cenários aprovados.

PR em rascunho: https://github.com/Solution-Explores/SigmaTI/pull/32
Commit: 21347528012b1291f1caaf4289f9316eff71e053
Evidências: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/evidencias.md

362 testes Python aprovados, sem ignorados. Execução e revisão técnica pelo Codex nesta conversa; não se declara revisão independente ou homologação hospitalar. CI da implementação 2134752 aprovado: API/aceite/E6/build/lint/Chromium e infraestrutura.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376074
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376159 Integração à dev/main e conclusão condicionadas à revisão/aprovação. Issues #5/#6 permanecem abertas.

HISTÓRICO PRESERVADO

ACHADOS CONFIRMADOS NO ACEITE K10 — 19/10/2026
Base testada: dev@142efd2; evidências/runner publicados em 001d304. Execução e revisão nesta conversa pelo Codex, sem revisão independente declarada.

CORREÇÕES NECESSÁRIAS

1. CORS: origem autorizada + preflight POST com content-type,authorization retorna 400. Esperado 200, mantendo restrição de origens.
2. Logout: login → status 200 → logout 200 → mesmo token retorna status 200. Esperado 401 após revogação.
3. Painel: formulário envia alerta sem JWT e não possui login; API retorna 401. Implementar fluxo de autenticação e envio de token.
4. Erros do painel: 401 é apresentado como falha de conexão com FastAPI, embora servidor esteja ativo. Distinguir autenticação, permissão e indisponibilidade.

ACEITE / REGRESSÃO
Reexecutar scripts/validate\_api\_acceptance.py, que mediu HTTP real com Uvicorn e IA simulada: 16 aprovações, duas reprovações; prazo de IA 14,016 s. Conferir também navegador até diagnóstico e preservar falha segura, logs seguros e 346 testes. Pendências anteriores da issue #6 (segredo JWT padrão, contas de demonstração, memória e carregamento do .env) seguem no registro K07/K08.

EVIDÊNCIAS
[https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/009-010-instalacao-aceite/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/009-010-instalacao-aceite/evidencias.md "‌")
[https://github.com/Solution-Explores/SigmaTI/blob/dev/resultados/aceite-k09-k10-2026-10-19.json](https://github.com/Solution-Explores/SigmaTI/blob/dev/resultados/aceite-k09-k10-2026-10-19.json "‌")

ENCAMINHAMENTO
Achados registrados; correções funcionais não executadas nesta K09/K10. Manter tarefa A fazer até iniciar a correção.

HISTÓRICO (preservado)

OBJETIVO
Corrigir achados da API

RESPONSÁVEL E PRAZO
Vinícius (Pessoa 1) — 19/10/2026.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K11.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base: dev@900dcc4.
A FAZER. Correções da autorrevisão K02 já constam nas evidências, mas não comprovam conclusão dos achados do aceite integral. Próximo passo: executar K10 e tratar os achados resultantes.
Evidência: ​[https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/specs/004-configuracao-ambiente-api/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/specs/004-configuracao-ambiente-api/evidencias.md "‌")
Testes citados são registros do repositório; não reexecutados nesta conferência.

### https://trello.com/c/v84QJxtu — ISSUES #3/#4 — Corrigir instalação e infraestrutura

Lista: Revisão e testes → Concluído. Prazo nativo: 2026-10-21T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] #3 e #4 encerradas no GitHub; correções integradas. Mover para Concluído somente quanto a esse escopo já encerrado. O aceite da demo no SHA congelado continua separado.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 21/10/2026 — situação conferida (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/3
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Correções da instalação/aceite integradas no PR #32. Evidências e achados antigos estão preservados abaixo; não representam o estado atual sem a data do registro.

## Issues do GitHub
- [#3 — Remover credenciais fixas, restringir portas e fixar versões no docker-compose](https://github.com/Solution-Explores/SigmaTI/issues/3) — encerrada.
- [#4 — main.py: chave de API por variável de ambiente, CORS restrito, chamada assíncrona com timeout](https://github.com/Solution-Explores/SigmaTI/issues/4) — encerrada.

## PRs e referências
- [PR #32 — Correções de autenticação, painel e anonimização](https://github.com/Solution-Explores/SigmaTI/pull/32) — integrado à develop.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K12 — Corrigir achados de infraestrutura e instalação

INTEGRAÇÃO NA DEV — 19/10/2026

PR #32 integrado na dev em 086129c9b8dd119d72877f493e1828ef2a46c949. O usuário autorizou explicitamente 'Autorizar o merge na dev' ao ser perguntado sobre dispensar nesta entrega a revisão por outro integrante. Revisão e testes foram executados pelo Codex; não se atribui aprovação independente a outra pessoa. A exceção é específica do PR #32.

Validação na dev: árvore idêntica ao head revisado; novo aceite HTTP passou 20 verificações (timeout 14,031 s). CI API e infraestrutura aprovados no commit integrado.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381540
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381631
PR integrado: https://github.com/Solution-Explores/SigmaTI/pull/32
Registro: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/specs/011-recuperacao-sprint/integracao-dev.md

Main e encerramento final permanecem pendentes; issues #5/#6 continuam parciais. Próxima entrega implementada: issue #9, PR #33 em revisão, ainda sem integração.

HISTÓRICO ANTERIOR PRESERVADO

REVISÃO TÉCNICA ADICIONAL — 19/10/2026

PR #32 pronto para revisão da equipe. Commit 7496564c1dd78f721d5c5c5dbfa6a0951b1c0c50 publicado; checkout limpo. Corrigidos: sobrenomes preservados pela sanitização, sessões antigas após recriar conta e limites de login ignorados no .env. Aceite Docker ampliado com escuta direta do Zabbix antes/depois da recriação.

Validação: 369 testes Python sem falhas/ignorados; 20 verificações HTTP (timeout 14,032 s); 3 cenários Chromium; build/lint; E6 com 53 identificadores em 59 mensagens; 23 verificações Docker com limpeza código 0. Política: 32 verificações de credenciais, 12 cenários de infraestrutura e quatro manifests oficiais aprovados. IA simulada e dados fictícios.

CI remoto do commit: API aprovado https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752713 ; infraestrutura aprovada https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752750 .
PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Relatório: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/revisao-tecnica.md

Revisão técnica do Codex concluída. Aprovação de OUTRO integrante permanece pendente conforme o fluxo do repositório. Não houve merge dev/main, homologação hospitalar ou fechamento de issues. #5/#6 continuam parciais.

HISTÓRICO ANTERIOR PRESERVADO

ATUALIZAÇÃO — 19/10/2026 — CORREÇÃO PARA REVISÃO

npm ci --include=optional, build e lint aprovados. Docker Engine 29.8.2 baixou os digests fixados com TLS válido; causa da falha TLS anterior não determinada. Runner de instalação passou 21 verificações, com limpeza dos recursos exclusivos.

PR em rascunho: https://github.com/Solution-Explores/SigmaTI/pull/32
Commit: 21347528012b1291f1caaf4289f9316eff71e053
Evidências: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/evidencias.md

362 testes Python aprovados, sem ignorados. Execução e revisão técnica pelo Codex nesta conversa; não se declara revisão independente ou homologação hospitalar. CI da implementação 2134752 aprovado: API/aceite/E6/build/lint/Chromium e infraestrutura.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376074
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376159 Integração à dev/main e conclusão condicionadas à revisão/aprovação. Issues #5/#6 permanecem abertas.

HISTÓRICO PRESERVADO

ACHADOS DA INSTALAÇÃO LIMPA K09 — 19/10/2026
Base independente dev@142efd2; evidências publicadas em 001d304. Execução/revisão pelo Codex nesta conversa.

BLOQUEIOS CONFIRMADOS

1. Docker Desktop/Engine 29.8.1 iniciou, mas o download das imagens fixadas falhou: failed to copy: local error: tls: bad record MAC. Duas tentativas falharam; TLS capturado na segunda. Causa não determinada. Projeto isolado sigmati-k09-20261019 não chegou a criar contêineres ou volumes.
2. npm run lint falha em sigma-frontend/src/App.jsx:38:14: err definido e não usado, regra no-unused-vars.
3. Primeiro npm ci omitiu \@rolldown/binding-win32-x64-msvc@1.2.12, já presente no lockfile. Download desse pacote para cache + npm ci --include=optional recuperou build sem alterar lockfile/versões. Investigar confiabilidade do procedimento no Windows; não concluir que o lockfile está incorreto sem evidência.

CRITÉRIOS A VALIDAR APÓS CORREÇÃO
Completar download das imagens fixadas com TLS válido, subir core e monitoring em projeto/volumes novos, conferir prontidão e autenticação PostgreSQL/n8n/Grafana/Zabbix e persistência após recriar contêineres. Preservar outros projetos e volumes. Build já passou; lint deve passar.

EVIDÊNCIAS
[https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/009-010-instalacao-aceite/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/009-010-instalacao-aceite/evidencias.md "‌")
[https://github.com/Solution-Explores/SigmaTI/blob/dev/resultados/aceite-k09-k10-2026-10-19.json](https://github.com/Solution-Explores/SigmaTI/blob/dev/resultados/aceite-k09-k10-2026-10-19.json "‌")
Python novo: pip check aprovado e 346 testes aprovados em 54,46 s. Serviços e persistência não homologados, pois não iniciaram.

ENCAMINHAMENTO
Achados registrados; correções K12 ainda não executadas. Manter A fazer até iniciar.

HISTÓRICO (preservado)

OBJETIVO
Corrigir achados de infraestrutura e instalação

RESPONSÁVEL E PRAZO
Joyce (Pessoa 3) — 19/10/2026 / manhã.
Disponibilidade: 08h–12h.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K12.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base: dev@900dcc4.
A FAZER. K03/K04 tratam credenciais, portas e imagens. Seguem pendentes avaliação/migração do volume legado e homologação da instalação/rede; validar escopo após K09. Planejar migração do Zabbix suportado como demanda separada.
Achados: [https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/specs/004-configuracao-ambiente-api/revisao-k01.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/specs/004-configuracao-ambiente-api/revisao-k01.md "‌")
Limites: [https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/specs/003-portas-e-imagens/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/specs/003-portas-e-imagens/evidencias.md "‌")
Testes citados são registros do repositório; não reexecutados nesta conferência.

### https://trello.com/c/NRkslN8y — ÉPICO #31 — Revisar PRs e validar integrações

Lista: Revisão e testes → Revisão e testes. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] PRs #43 e #44 abertos e com CI verde; revisão independente ainda não registrada no GitHub. #43 previsto 22/10, #44 23/10. #41 e #42 são documentação e ficam após a demo.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto: https://github.com/Solution-Explores/SigmaTI/pull/43
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
PRs #32 e #34–#40 integrados; o #33 foi substituído pelo #34. PRs #41 e #42 são documentação/conferência ainda abertas. Release/main é etapa própria.

## Issues do GitHub
- [#31 — Épico: evoluir o SIGMA para um sistema de engenharia da computação](https://github.com/Solution-Explores/SigmaTI/issues/31) — aberta.

## PRs e referências
- [PR #32 — Correções de autenticação, painel e anonimização](https://github.com/Solution-Explores/SigmaTI/pull/32) — integrado à develop.
- [PR #34 — Empacotar sigma_eng e remover imports pelo caminho engenharia (#9)](https://github.com/Solution-Explores/SigmaTI/pull/34) — integrado à develop.
- [PR #40 — feat: backup autenticado, restauração e smoke RNF06 (#25)](https://github.com/Solution-Explores/SigmaTI/pull/40) — integrado à develop.
- [PR #41 — docs: planejamento da validacao #25 em VM VirtualBox](https://github.com/Solution-Explores/SigmaTI/pull/41) — aberto; aguardando integração.
- [PR #42 — docs: conferir aceite de #6 #7 #8 #14 e registrar lacunas](https://github.com/Solution-Explores/SigmaTI/pull/42) — aberto; aguardando integração.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K13 — Revisar PRs, integrar e verificar checkout limpo

PR #34 RESOLVIDO — 19/10/2026
Integrado à develop em 5d848a9e102ffa8a0810412ca772c37e3e3b1947.
PR: https://github.com/Solution-Explores/SigmaTI/pull/34
Revisão técnica: Codex, a pedido do usuário; não houve revisão independente por outro integrante.
Seis checks do PR aprovados; 77 testes locais focados aprovados; pip check aprovado.
CI do merge aprovado:
https://github.com/Solution-Explores/SigmaTI/actions/runs/39323374546
https://github.com/Solution-Explores/SigmaTI/actions/runs/39323374588
Main não alterada. Próxima frente: #6/#7; publicação de release ainda depende de aceite próprio.

---
HISTÓRICO
ATUALIZAÇÃO DO PLANO — 19/10/2026
PR #32 integrado na dev (086129c). Próximo: revisar PR #33, obter aprovação e integrar; validar CI no SHA integrado. A dispensa de revisão autorizada para PR #32 não vale automaticamente para novos PRs.
Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9

---
HISTÓRICO PRESERVADO
INTEGRAÇÃO NA DEV — 19/10/2026

PR #32 integrado na dev em 086129c9b8dd119d72877f493e1828ef2a46c949. O usuário autorizou explicitamente 'Autorizar o merge na dev' ao ser perguntado sobre dispensar nesta entrega a revisão por outro integrante. Revisão e testes foram executados pelo Codex; não se atribui aprovação independente a outra pessoa. A exceção é específica do PR #32.

Validação na dev: árvore idêntica ao head revisado; novo aceite HTTP passou 20 verificações (timeout 14,031 s). CI API e infraestrutura aprovados no commit integrado.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381540
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381631
PR integrado: https://github.com/Solution-Explores/SigmaTI/pull/32
Registro: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/specs/011-recuperacao-sprint/integracao-dev.md

Main e encerramento final permanecem pendentes; issues #5/#6 continuam parciais. Próxima entrega implementada: issue #9, PR #33 em revisão, ainda sem integração.

HISTÓRICO ANTERIOR PRESERVADO

REVISÃO TÉCNICA ADICIONAL — 19/10/2026

PR #32 pronto para revisão da equipe. Commit 7496564c1dd78f721d5c5c5dbfa6a0951b1c0c50 publicado; checkout limpo. Corrigidos: sobrenomes preservados pela sanitização, sessões antigas após recriar conta e limites de login ignorados no .env. Aceite Docker ampliado com escuta direta do Zabbix antes/depois da recriação.

Validação: 369 testes Python sem falhas/ignorados; 20 verificações HTTP (timeout 14,032 s); 3 cenários Chromium; build/lint; E6 com 53 identificadores em 59 mensagens; 23 verificações Docker com limpeza código 0. Política: 32 verificações de credenciais, 12 cenários de infraestrutura e quatro manifests oficiais aprovados. IA simulada e dados fictícios.

CI remoto do commit: API aprovado https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752713 ; infraestrutura aprovada https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752750 .
PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Relatório: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/revisao-tecnica.md

Revisão técnica do Codex concluída. Aprovação de OUTRO integrante permanece pendente conforme o fluxo do repositório. Não houve merge dev/main, homologação hospitalar ou fechamento de issues. #5/#6 continuam parciais.

HISTÓRICO ANTERIOR PRESERVADO

ATUALIZAÇÃO — 19/10/2026 — ENTREGA PARCIAL PARA REVISÃO

PR #32 preparado em rascunho com base na dev. Implementação 2134752 e consolidação documental 7489bf2 publicadas; checkout local limpo. CI da implementação aprovado. Próximo passo: revisão de outro integrante e aprovação antes de integrar à dev/main. Não houve integração nem fechamento de issues.

PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Evidências: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/evidencias.md
CI da implementação: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376074

Execução e revisão técnica pelo Codex; não se declara revisão independente ou homologação hospitalar.

HISTÓRICO PRESERVADO

OBJETIVO
Revisar PRs, integrar e verificar checkout limpo

RESPONSÁVEL E PRAZO
Joyce (Pessoa 3) — 20/10/2026 / manhã.
Disponibilidade: 08h–12h.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K13.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base: dev@900dcc4.
A FAZER. Commits presentes na dev não equivalem à integração aprovada na main. Compose da main ainda contém marcadores de conflito. Falta revisão independente, validação conjunta e integração; não há evidência de checkout limpo da entrega integrada.
Fluxo: [https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/doc/fluxo-de-trabalho-tcc.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/doc/fluxo-de-trabalho-tcc.md "‌")
Main: [https://github.com/Solution-Explores/SigmaTI/blob/main/docker-compose.yml](https://github.com/Solution-Explores/SigmaTI/blob/main/docker-compose.yml "‌")
Testes citados são registros do repositório; não reexecutados nesta conferência.

### https://trello.com/c/HMFmBFhp — ÉPICO #31 — Finalizar README e roteiro da demonstração

Lista: Revisão e testes → A fazer. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Roteiro de sete passos preparado; ensaios e contingência pendentes. Não há PR aberto exclusivo de README/roteiro confirmado; mover para A fazer. PRs de documentação #41/#42 ficam após a demo.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h — roteiro; README após demo (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Documentação da demonstração é transversal. PR #41 prepara o aceite da VM; PR #42 consolida o estado das issues e lacunas confirmadas. Ambos ainda aguardam integração.

## Issues do GitHub
- [#31 — Épico: evoluir o SIGMA para um sistema de engenharia da computação](https://github.com/Solution-Explores/SigmaTI/issues/31) — aberta.

## PRs e referências
- [PR #32 — Correções de autenticação, painel e anonimização](https://github.com/Solution-Explores/SigmaTI/pull/32) — integrado à develop.
- [PR #41 — docs: planejamento da validacao #25 em VM VirtualBox](https://github.com/Solution-Explores/SigmaTI/pull/41) — aberto; aguardando integração.
- [PR #42 — docs: conferir aceite de #6 #7 #8 #14 e registrar lacunas](https://github.com/Solution-Explores/SigmaTI/pull/42) — aberto; aguardando integração.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K14 — Finalizar README e roteiro da demonstração

ATUALIZAÇÃO DO PLANO — 19/10/2026
README agora aponta para o plano publicado em 514838f. Roteiro final depende do conjunto aprovado após congelamento de funcionalidades em 20/10 às 14h (Manaus).
Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9

---
HISTÓRICO PRESERVADO
INTEGRAÇÃO NA DEV — 19/10/2026

PR #32 integrado na dev em 086129c9b8dd119d72877f493e1828ef2a46c949. O usuário autorizou explicitamente 'Autorizar o merge na dev' ao ser perguntado sobre dispensar nesta entrega a revisão por outro integrante. Revisão e testes foram executados pelo Codex; não se atribui aprovação independente a outra pessoa. A exceção é específica do PR #32.

Validação na dev: árvore idêntica ao head revisado; novo aceite HTTP passou 20 verificações (timeout 14,031 s). CI API e infraestrutura aprovados no commit integrado.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381540
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39310381631
PR integrado: https://github.com/Solution-Explores/SigmaTI/pull/32
Registro: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/specs/011-recuperacao-sprint/integracao-dev.md

Main e encerramento final permanecem pendentes; issues #5/#6 continuam parciais. Próxima entrega implementada: issue #9, PR #33 em revisão, ainda sem integração.

HISTÓRICO ANTERIOR PRESERVADO

REVISÃO TÉCNICA ADICIONAL — 19/10/2026

PR #32 pronto para revisão da equipe. Commit 7496564c1dd78f721d5c5c5dbfa6a0951b1c0c50 publicado; checkout limpo. Corrigidos: sobrenomes preservados pela sanitização, sessões antigas após recriar conta e limites de login ignorados no .env. Aceite Docker ampliado com escuta direta do Zabbix antes/depois da recriação.

Validação: 369 testes Python sem falhas/ignorados; 20 verificações HTTP (timeout 14,032 s); 3 cenários Chromium; build/lint; E6 com 53 identificadores em 59 mensagens; 23 verificações Docker com limpeza código 0. Política: 32 verificações de credenciais, 12 cenários de infraestrutura e quatro manifests oficiais aprovados. IA simulada e dados fictícios.

CI remoto do commit: API aprovado https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752713 ; infraestrutura aprovada https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752750 .
PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Relatório: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/revisao-tecnica.md

Revisão técnica do Codex concluída. Aprovação de OUTRO integrante permanece pendente conforme o fluxo do repositório. Não houve merge dev/main, homologação hospitalar ou fechamento de issues. #5/#6 continuam parciais.

HISTÓRICO ANTERIOR PRESERVADO

ATUALIZAÇÃO — 19/10/2026 — ENTREGA PARCIAL PARA REVISÃO

README, roteiro de instalação/demonstração e evidências atualizados no PR #32. Incluem criação local de hashes, cinco variáveis obrigatórias, limitações de memória, testes HTTP/navegador e instalação descartável. Falta revisão e integração aprovada.

PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Evidências: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/evidencias.md
CI da implementação: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376074

Execução e revisão técnica pelo Codex; não se declara revisão independente ou homologação hospitalar.

HISTÓRICO PRESERVADO

OBJETIVO
Finalizar README e roteiro da demonstração

RESPONSÁVEL E PRAZO
Vinícius (Pessoa 1) — 20/10/2026 / manhã.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K14.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base: dev@900dcc4.
EM ANDAMENTO — documentação parcial. README atualizado para configuração da API, credenciais, portas e imagens; roteiro de instalação ainda contém placeholders. Não foi encontrado roteiro final de demonstração que comprove esta entrega.
Documento: [https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/README.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/README.md "smartCard-inline")
Testes citados são registros do repositório; não reexecutados nesta conferência.

### https://trello.com/c/D3LstOrT — ISSUE #4 — Testar API com provedor de IA simulado

Lista: Revisão e testes → Concluído. Prazo nativo: 2026-10-21T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] #4 encerrada, entrega integrada. Mover o cartão dessa etapa para Concluído; testes instáveis têm issue própria e não substituem o aceite final de 23/10.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 21/10/2026 — situação conferida (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/4
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Etapa histórica de testes da API (antigo K07), relacionada à issue #4. Não é a issue #7 de persistência. PR #32 registra correções e aceite posteriores; a entrega inicial consta nos commits do histórico.

## Issues do GitHub
- [#4 — main.py: chave de API por variável de ambiente, CORS restrito, chamada assíncrona com timeout](https://github.com/Solution-Explores/SigmaTI/issues/4) — encerrada.

## PRs e referências
- [PR #32 — Correções de autenticação, painel e anonimização](https://github.com/Solution-Explores/SigmaTI/pull/32) — integrado à develop.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K07 — Testar API com provedor simulado

ENTREGA E REVISÃO — 19/10/2026
Escopo K07 implementado e revisado nesta conversa pelo Codex, conforme solicitação do usuário de revisar aqui sem aguardar outro integrante. Publicado na dev: implementação 6c8533e e correção de CI 7975c00.

RESULTADOS CONFERIDOS
CI Linux: 346 testes aprovados em 22,31 s, sem falhas, erros ou ignorados. Execução local: 346 aprovados; prazo real da chamada autenticada ao provedor simulado próximo de 14 s, com cancelamento e limite de 15 s comprovados.
Reaproveitada a cobertura K02/K05/K06 de falhas HTTP/transporte, JSON inválido, logs seguros, CORS, concorrência e anonimização. Adicionados sucesso e falhas após login real; token ausente, vazio, inválido e expirado nunca chamam o provedor.

CI API: [https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110405](https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110405 "‌")
CI infraestrutura: [https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110475](https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110475 "‌")
Evidências/revisão: [https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/007-008-ci-provedor-simulado/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/007-008-ci-provedor-simulado/evidencias.md "‌")
Fluxo: [https://github.com/Solution-Explores/SigmaTI/blob/dev/doc/fluxo-de-trabalho-tcc.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/doc/fluxo-de-trabalho-tcc.md "‌")

REVISÃO CONCLUÍDA / PRÓXIMAS ETAPAS
A situação Revisão e testes registra a entrega validada na dev. A revisão técnica já foi feita aqui; não há espera por outro revisor. Aceite integrado K10, achados CORS/logout/autenticação K11 e integração do conjunto na main K13 continuam separados. A issue #4 não é encerrada por esta entrega parcial.

HISTÓRICO DO CARTÃO (preservado)

OBJETIVO
Testar API com provedor simulado

RESPONSÁVEL E PRAZO
Vinícius (Pessoa 1) — 16/10/2026.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K07.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base: dev@900dcc4.
A FAZER — testes parciais já existentes na K02. Há provedor simulado para sucesso, configuração e CORS. Não há comprovação completa de timeout <= 15 s e falhas com resposta pública genérica. Completar após K05/K06.
Testes: [https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/tests/test_config.py](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/tests/test_config.py "‌")
Issue: [https://github.com/Solution-Explores/SigmaTI/issues/4](https://github.com/Solution-Explores/SigmaTI/issues/4 "‌")
Testes citados são registros do repositório; não reexecutados nesta conferência.

### https://trello.com/c/KfknLcok — ÉPICO #31 — Validar instalação limpa da demonstração

Lista: Revisão e testes → A fazer. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Ambiente local em preparação; falta ensaio técnico e aceite no SHA integrado. Sem PR aberto exclusivo dessa execução: mover para A fazer. Instalação anterior não equivale a aceite da demo atual.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/31
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Atualização — 20/10/2026 (Manaus)
[Certo] Ubuntu 24.04.4 instalado em VM VirtualBox, PostgreSQL 15 e ambiente de teste configurados. Restauração sintética passou em 17 verificações no mesmo host físico. API (20 verificações), build/lint, 16 testes frontend e cenário de navegador operacional passaram.

O aceite integrado permanece pendente: regressão Python teve 466 aprovações e uma falha de carga de 200 alvos em loopback. Não declarar instalação/homologação integral a partir desses resultados. A investigação foi interrompida a pedido do usuário, sem alteração de código versionado. Ambiente preservado para transferência e continuação em casa.

Evidências: laboratorio-vm/evidencias/ e pacote evidencias-para-casa.zip. Não foram sondados equipamentos hospitalares.

---
## Registro anterior (preservado; consultar atualização acima)

## Resumo atual
Validação transversal de instalação/configuração. Correções e reexecução do aceite estão no PR #32 integrado. Não equivale à restauração em outra máquina da #25.

## Issues do GitHub
- [#31 — Épico: evoluir o SIGMA para um sistema de engenharia da computação](https://github.com/Solution-Explores/SigmaTI/issues/31) — aberta.
- [#3 — Remover credenciais fixas, restringir portas e fixar versões no docker-compose](https://github.com/Solution-Explores/SigmaTI/issues/3) — encerrada.
- [#4 — main.py: chave de API por variável de ambiente, CORS restrito, chamada assíncrona com timeout](https://github.com/Solution-Explores/SigmaTI/issues/4) — encerrada.
- [#5 — Anonimização LGPD robusta e fail-closed (RF05)](https://github.com/Solution-Explores/SigmaTI/issues/5) — aberta.
- [#6 — Autenticação e perfis (RF07): login com JWT de sessão e RBAC](https://github.com/Solution-Explores/SigmaTI/issues/6) — aberta.

## PRs e referências
- [PR #32 — Correções de autenticação, painel e anonimização](https://github.com/Solution-Explores/SigmaTI/pull/32) — integrado à develop.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K09 — Verificar instalação limpa e configurações

REVISÃO TÉCNICA ADICIONAL — 19/10/2026

PR #32 pronto para revisão da equipe. Commit 7496564c1dd78f721d5c5c5dbfa6a0951b1c0c50 publicado; checkout limpo. Corrigidos: sobrenomes preservados pela sanitização, sessões antigas após recriar conta e limites de login ignorados no .env. Aceite Docker ampliado com escuta direta do Zabbix antes/depois da recriação.

Validação: 369 testes Python sem falhas/ignorados; 20 verificações HTTP (timeout 14,032 s); 3 cenários Chromium; build/lint; E6 com 53 identificadores em 59 mensagens; 23 verificações Docker com limpeza código 0. Política: 32 verificações de credenciais, 12 cenários de infraestrutura e quatro manifests oficiais aprovados. IA simulada e dados fictícios.

CI remoto do commit: API aprovado https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752713 ; infraestrutura aprovada https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752750 .
PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Relatório: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/revisao-tecnica.md

Revisão técnica do Codex concluída. Aprovação de OUTRO integrante permanece pendente conforme o fluxo do repositório. Não houve merge dev/main, homologação hospitalar ou fechamento de issues. #5/#6 continuam parciais.

HISTÓRICO ANTERIOR PRESERVADO

ATUALIZAÇÃO — 19/10/2026 — CORREÇÃO PARA REVISÃO

Instalação isolada concluída: 21 verificações de prontidão, autenticação e persistência após recriação. Owner nativo e login do n8n, PostgreSQL/Zabbix/Grafana verificados. Recursos descartáveis removidos; outros projetos preservados.

PR em rascunho: https://github.com/Solution-Explores/SigmaTI/pull/32
Commit: 21347528012b1291f1caaf4289f9316eff71e053
Evidências: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/evidencias.md

362 testes Python aprovados, sem ignorados. Execução e revisão técnica pelo Codex nesta conversa; não se declara revisão independente ou homologação hospitalar. CI da implementação 2134752 aprovado: API/aceite/E6/build/lint/Chromium e infraestrutura.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376074
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376159 Integração à dev/main e conclusão condicionadas à revisão/aprovação. Issues #5/#6 permanecem abertas.

HISTÓRICO PRESERVADO

EXECUÇÃO E REVISÃO — 19/10/2026 — INSTALAÇÃO BLOQUEADA
Executado e revisado pelo Codex nesta conversa. Checkout remoto independente dev@142efd2, novo ambiente virtual e credenciais fictícias geradas; cópia antiga preservada. Relatório publicado na dev@001d304.

RESULTADOS
• Python: instalação e pip check aprovados; 346 testes aprovados em 54,46 s, sem falhas/erros/ignorados.
• Frontend: primeiro npm ci omitiu pacote nativo já fixado. Cache do pacote + npm ci --include=optional completou instalação sem alterar lockfile ou versões. Build aprovado.
• Lint reprovado: sigma-frontend/src/App.jsx:38:14, err não usado. K12.
• Docker Desktop iniciado. Compose isolado e configuração aprovados; projeto sigmati-k09-20261019, portas loopback exclusivas e nenhum volume prévio.
• Inicialização bloqueada durante download: failed to copy: local error: tls: bad record MAC. Nenhum contêiner/volume do projeto foi criado.

PENDÊNCIAS K12
Investigar falha TLS e concluir download das imagens fixadas; iniciar serviços e conferir prontidão, autenticação e persistência após recriação. Não substituir digests nem desativar certificados para passar no teste. Causa original de TLS ainda não determinada.

EVIDÊNCIAS
[https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/009-010-instalacao-aceite/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/009-010-instalacao-aceite/evidencias.md "‌")
[https://github.com/Solution-Explores/SigmaTI/blob/dev/resultados/aceite-k09-k10-2026-10-19.json](https://github.com/Solution-Explores/SigmaTI/blob/dev/resultados/aceite-k09-k10-2026-10-19.json "‌")

SITUAÇÃO
Manter Em andamento; instalação não aprovada. Revisão já realizada aqui, sem espera por outro integrante. Outros projetos Docker preservados.

HISTÓRICO (preservado)

OBJETIVO
Verificar instalação limpa e configurações

RESPONSÁVEL E PRAZO
Iohan (Pessoa 2) — 17/10/2026.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K09.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base: dev@900dcc4.
A FAZER. Evidências registram apenas validação de configuração; contêineres não foram iniciados. Não há comprovação de instalação limpa, inicialização e autenticação dos serviços.
Limites: ​[https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/specs/003-portas-e-imagens/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/specs/003-portas-e-imagens/evidencias.md "‌")
Testes citados são registros do repositório; não reexecutados nesta conferência.

### https://trello.com/c/sTTArNVt — ÉPICO #31 — Manter CI e roteiro de instalação

Lista: Revisão e testes → A fazer. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] CI das bases atuais verde; instalação/aceite final da demonstração pendentes. Não há PR aberto exclusivo de uma nova mudança de CI/instalação. Mover para A fazer para executar a conferência final.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/3
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Etapa transversal de CI/instalação (antigo K08). Não é a issue #8 de monitoramento/SSE. Entrega inicial nos commits do histórico; PRs #34 e #40 acrescentam validações posteriores de pacote e recuperação.

## Issues do GitHub
- [#31 — Épico: evoluir o SIGMA para um sistema de engenharia da computação](https://github.com/Solution-Explores/SigmaTI/issues/31) — aberta.
- [#3 — Remover credenciais fixas, restringir portas e fixar versões no docker-compose](https://github.com/Solution-Explores/SigmaTI/issues/3) — encerrada.
- [#4 — main.py: chave de API por variável de ambiente, CORS restrito, chamada assíncrona com timeout](https://github.com/Solution-Explores/SigmaTI/issues/4) — encerrada.

## PRs e referências
- [PR #34 — Empacotar sigma_eng e remover imports pelo caminho engenharia (#9)](https://github.com/Solution-Explores/SigmaTI/pull/34) — integrado à develop.
- [PR #40 — feat: backup autenticado, restauração e smoke RNF06 (#25)](https://github.com/Solution-Explores/SigmaTI/pull/40) — integrado à develop.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K08 — Atualizar CI e preparar roteiro de instalação

ATUALIZAÇÃO — 19/10/2026
Implementação e revisão técnica executadas pelo Codex nesta conversa, conforme solicitação do usuário de revisar aqui sem aguardar outro integrante.

K08: coleta de API/engenharia corrigida em pytest.ini; quatro testes HTTP reativados com JWT; aspas no executável Windows corrigidas; condição de corrida Linux da porta fechada corrigida em branch separada e integrada à dev. Roteiro de instalação preparado.

EVIDÊNCIAS
346 testes locais aprovados, sem falhas/erros/ignorados; 32 checks de credenciais e 12 cenários de infraestrutura aprovados, com manifests oficiais conferidos. CI remoto do conjunto corrigido APROVADO: API/engenharia com 346 testes em 22,31 s e infraestrutura com sucesso.
API: [https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110405](https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110405 "‌")
Infraestrutura: [https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110475](https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110475 "‌")

Commits: dev@6c8533e e correção 7975c00.
Roteiro: [https://github.com/Solution-Explores/SigmaTI/blob/dev/doc/instalacao-desenvolvimento.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/doc/instalacao-desenvolvimento.md "‌")
Evidências e revisão: [https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/007-008-ci-provedor-simulado/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/007-008-ci-provedor-simulado/evidencias.md "‌")
Fluxo adotado: [https://github.com/Solution-Explores/SigmaTI/blob/dev/doc/fluxo-de-trabalho-tcc.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/doc/fluxo-de-trabalho-tcc.md "‌")

LIMITES
Instalação limpa e inicialização de serviços pertencem à K09; Docker Engine inativo nesta máquina. Aceite integrado é K10; achados de autenticação/CORS registrados para K11. Revisão técnica concluída aqui; não há espera por outro revisor. Integração do conjunto na main será conferida na K13, após aceite K10 e achados K11/K12. Não se declara revisão independente ou aceite integral das issues.

HISTÓRICO DO CARTÃO (preservado)

OBJETIVO
Atualizar CI e preparar roteiro de instalação

RESPONSÁVEL E PRAZO
Joyce (Pessoa 3) — 16/10/2026 / manhã.
Disponibilidade: 08h–12h.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K08.

CONFERÊNCIA DO REPOSITÓRIO — 15/10/2026
Base: dev@900dcc4.
EM ANDAMENTO — entrega parcial identificada. CI de infraestrutura e API cobre dev/main; validadores de credenciais, portas e imagens presentes. README contém instruções de configuração, porém instalação ainda tem placeholders e não há evidência de roteiro completo validado em instalação limpa.
CI: [https://github.com/Solution-Explores/SigmaTI/tree/900dcc409e72fd973be12a76330233ce163f62ed/.github/workflows](https://github.com/Solution-Explores/SigmaTI/tree/900dcc409e72fd973be12a76330233ce163f62ed/.github/workflows "‌")
Instalação: [https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/README.md](https://github.com/Solution-Explores/SigmaTI/blob/900dcc409e72fd973be12a76330233ce163f62ed/README.md "‌")
Testes citados são registros do repositório; não reexecutados nesta conferência.

### https://trello.com/c/z1CLDzjj — ISSUES #4/#5/#6 — Executar aceite integrado da API

Lista: Revisão e testes → A fazer. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] Aceites anteriores são históricos; executar novamente na develop integrada no SHA da demo. #5/#6 ainda abertas. Sem PR aberto exclusivo do novo aceite: mover para A fazer.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/6
- PR aberto exclusivo: nenhum confirmado; o link da issue serve para acompanhar a etapa.
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Resumo atual
Etapa de aceite HTTP/navegador com IA simulada. Correções e revalidação integradas no PR #32. Não demonstra correção das novas lacunas da #6 identificadas depois.

## Issues do GitHub
- [#4 — main.py: chave de API por variável de ambiente, CORS restrito, chamada assíncrona com timeout](https://github.com/Solution-Explores/SigmaTI/issues/4) — encerrada.
- [#5 — Anonimização LGPD robusta e fail-closed (RF05)](https://github.com/Solution-Explores/SigmaTI/issues/5) — aberta.
- [#6 — Autenticação e perfis (RF07): login com JWT de sessão e RBAC](https://github.com/Solution-Explores/SigmaTI/issues/6) — aberta.

## PRs e referências
- [PR #32 — Correções de autenticação, painel e anonimização](https://github.com/Solution-Explores/SigmaTI/pull/32) — integrado à develop.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — K10 — Executar aceite da API e registrar evidências

REVISÃO TÉCNICA ADICIONAL — 19/10/2026

PR #32 pronto para revisão da equipe. Commit 7496564c1dd78f721d5c5c5dbfa6a0951b1c0c50 publicado; checkout limpo. Corrigidos: sobrenomes preservados pela sanitização, sessões antigas após recriar conta e limites de login ignorados no .env. Aceite Docker ampliado com escuta direta do Zabbix antes/depois da recriação.

Validação: 369 testes Python sem falhas/ignorados; 20 verificações HTTP (timeout 14,032 s); 3 cenários Chromium; build/lint; E6 com 53 identificadores em 59 mensagens; 23 verificações Docker com limpeza código 0. Política: 32 verificações de credenciais, 12 cenários de infraestrutura e quatro manifests oficiais aprovados. IA simulada e dados fictícios.

CI remoto do commit: API aprovado https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752713 ; infraestrutura aprovada https://github.com/Solution-Explores/SigmaTI/actions/runs/39308752750 .
PR: https://github.com/Solution-Explores/SigmaTI/pull/32
Relatório: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/revisao-tecnica.md

Revisão técnica do Codex concluída. Aprovação de OUTRO integrante permanece pendente conforme o fluxo do repositório. Não houve merge dev/main, homologação hospitalar ou fechamento de issues. #5/#6 continuam parciais.

HISTÓRICO ANTERIOR PRESERVADO

ATUALIZAÇÃO — 19/10/2026 — CORREÇÃO PARA REVISÃO

Novo aceite HTTP real/Uvicorn com IA simulada: 20 aprovações e zero reprovações, timeout 14,031 s e cancelamento. Chromium: login → alerta → diagnóstico → logout com rejeição real do token; recarregar exige login; mensagens 401/403/rede distintas.

PR em rascunho: https://github.com/Solution-Explores/SigmaTI/pull/32
Commit: 21347528012b1291f1caaf4289f9316eff71e053
Evidências: https://github.com/Solution-Explores/SigmaTI/blob/fix/sprint-aceite-autenticacao-privacidade/specs/011-recuperacao-sprint/evidencias.md

362 testes Python aprovados, sem ignorados. Execução e revisão técnica pelo Codex nesta conversa; não se declara revisão independente ou homologação hospitalar. CI da implementação 2134752 aprovado: API/aceite/E6/build/lint/Chromium e infraestrutura.
API: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376074
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39305376159 Integração à dev/main e conclusão condicionadas à revisão/aprovação. Issues #5/#6 permanecem abertas.

HISTÓRICO PRESERVADO

EXECUÇÃO E REVISÃO — 19/10/2026 — ACEITE REPROVADO
Executado e revisado pelo Codex nesta conversa, conforme solicitação do usuário. Base independente dev@142efd2; relatório e runner publicados na dev@001d304.

HTTP REAL / UVICORN, IA SIMULADA
18 verificações: 16 aprovadas, duas reprovadas. Autenticação ativa; token obrigatório, RBAC, contrato, anonimização, falha segura e erros genéricos aprovados. Timeout medido: 14,016 s, com cancelamento e sem chamada a IA real.

REPROVAÇÕES K11

1. Preflight da origem autorizada com Authorization retorna 400 (esperado 200).
2. Logout retorna 200, mas o mesmo token continua válido (esperado 401).
3. No navegador o painel não envia JWT/não possui login: API responde 401. A interface informa falha de conexão, embora o servidor esteja ativo. Diagnóstico não alcançado.

EVIDÊNCIAS
[https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/009-010-instalacao-aceite/evidencias.md](https://github.com/Solution-Explores/SigmaTI/blob/dev/specs/009-010-instalacao-aceite/evidencias.md "‌")
[https://github.com/Solution-Explores/SigmaTI/blob/dev/resultados/aceite-k09-k10-2026-10-19.json](https://github.com/Solution-Explores/SigmaTI/blob/dev/resultados/aceite-k09-k10-2026-10-19.json "‌")
Runner: scripts/validate\_api\_acceptance.py (exit 1 quando algum critério falha).

SITUAÇÃO
Manter Em andamento. Revisão já feita aqui; repetir aceite após correções K11/K12. Não há aprovação para concluir, integrar à main ou encerrar issue. Servidores temporários encerrados após evidências.

HISTÓRICO (preservado)

OBJETIVO
Executar aceite da API e registrar evidências

RESPONSÁVEL E PRAZO
Iohan (Pessoa 2) — 18/10/2026.

DEPENDÊNCIAS
A confirmar no planejamento detalhado antes de iniciar.

CRITÉRIOS DE CONCLUSÃO
• Entrega correspondente ao objetivo implementada e revisada.
• Validação executada e evidências anexadas ou vinculadas.
• Documentação pertinente atualizada.
• Critérios específicos da issue conferidos antes do encerramento.

REFERÊNCIAS
Sprint: 15–20/10/2026. Foco nas issues #2, #3 e #4; vincular a issue e o PR correspondente quando identificados.
Ordem de prioridade: K10.

### https://trello.com/c/NbEHZVro — ISSUE #8 — Monitoramento contínuo e eventos SSE

Lista: Revisão e testes → Revisão e testes. Prazo nativo: 2026-10-23T22:00:00.000Z.

## Situação vigente — 21/10/2026 (substitui resumos antigos abaixo)
[Certo] PR #44 aberto, fix/coleta@ddd4840; inclui #43 e ainda mira fix/base-issues. CI verde. VM: baseline0/5 → candidato5/5; 489/489, p95 queda→SSE≤0,410s, atraso máximo0,093396s, erros0. Validado em VM; aceite final em 23/10. Alteração do alvo depende da integração do #43; revisão na noite de 22/10.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy); revisão pendente, não aprovada.
- Prazo: 23/10/2026 às 18h (UTC−4). Datas de proposta/triagem não são promessa de implementação.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/8
- PR aberto: https://github.com/Solution-Explores/SigmaTI/pull/44
- Evidências locais: rodada-2026-10-22, rodada-2026-10-22b e rodada-2026-10-22c; os arquivos não estão no repositório.

---
## Histórico preservado (pode conter prazos e estados superados)

## Pronto para revisão — 20/10/2026 (Manaus)
[Certo] PR #44, fix/coleta@4350632, separado e dependente do PR #43. Persistência em lotes/pipeline, eventos agrupados e contrapressão pelo calendário, sem ampliar as 32 vagas ou alterar asserções.
https://github.com/Solution-Explores/SigmaTI/pull/44
Três E2 completos aprovados: 200 alvos/2 s/32 trabalhos/6 s; zero novas perdas e erros, 599/592/590 medições na janela, mínimo 2 por alvo, atraso máximo 31,9/44,0/31,7 ms. Trinta quedas por rodada, reinício sem duplicação, replay e logout aprovados.
Regressão Windows: 487 aprovados, 0 falhas/erros, 1 ignorado específico POSIX (488 total, 211,06 s). Navegador real aprovado. Todos os cinco checks Linux do mesmo commit aprovados, incluindo PostgreSQL e recuperação.
https://github.com/Solution-Explores/SigmaTI/actions/runs/39517482380
https://github.com/Solution-Explores/SigmaTI/actions/runs/39517482458
Issue #8 permanece aberta até revisão/integração. Primeiro integrar/revisar #43 e depois retargetar #44 para develop. Nenhum merge executado. Somente loopback, dados fictícios, IA simulada; VM não usada. Não é homologação hospitalar ou teste prolongado.
Evidência local sanitizada: test-results/revisao-issues-base/entrega-final.json. Variantes reprovadas preservadas no histórico.

---
## Desenvolvimento — 20/10/2026 (Manaus)
[Certo] Branch fix/coleta, sobre a97fe1b do PR #43. Persistência em lotes limitados a 32, pipeline transacional, testes de idempotência/rollback/detectores/concorrência e contrapressão pelo calendário. Sem fila de novas sondas, sem ampliar as 32 vagas e sem alterar asserções do E2.
Primeiro E2 completo aprovado: 617 medições na janela de 6 s, sem novas perdas, erros zero, atraso máximo 0,176 s; 30 quedas, reinício sem incidente duplicado, replay e logout passaram.
Regressão completa e repetições adicionais EM EXECUÇÃO; não declarar conclusão da #8 a partir de uma aprovação. Variantes anteriores reprovadas preservadas nos relatórios locais. VM parada, somente loopback e IA simulada. Evidências: test-results/revisao-issues-base/ e doc/coleta-lotes.md.

---
## Atualização — 20/10/2026 (Manaus)
[Certo] Regressão isolada na VM: 467 testes Python, 466 aprovados e 1 reprovado, sem testes ignorados. Falha: tests/test_collection_e2.py::test_e2_thirty_failures_200_targets_restart_and_sse, em scripts/validate_collection.py:248.

No cenário original de 200 alvos lógicos TCP em loopback, intervalo de 2 s e concorrência de 32, aumentou o contador missed durante a janela de 6 s. Não houve erros ou timeouts nas métricas dessa janela. Aceite de carga permanece reprovado.

Experimentos diagnósticos sem alteração do produto: 4 trabalhadores de persistência reprovaram 3/3 rodadas; 1 trabalhador passou 1/3 e reprovou 2/3 (mais 86 e 138 ciclos descartados nas janelas reprovadas). Nenhuma configuração foi validada como correção. Houve também um stall RCU da VM durante a investigação; sua relação causal com a falha não foi comprovada.

Testes interrompidos por solicitação do usuário. Contêiner temporário removido, banco restaurado preservado, nenhum código versionado alterado. Próximo passo em casa: conferir integridade do ambiente, separar contenção de persistência e instabilidade da VM, corrigir e repetir o critério original sem reduzir a carga. Somente loopback foi sondado; não houve teste de ativos hospitalares.

Evidência selecionada: laboratorio-vm/evidencias/rodada-isolada/. Logs e diagnósticos adicionais ficam no disco da VM. Issue #8 continua pendente.

---
## Registro anterior (preservado; consultar atualização acima)

## Resumo atual
Critérios locais cobertos no PR #38: 30 quedas, reinício e 200 alvos lógicos. Painel consumidor no PR #39. Issue segue aberta para aceite; não é teste de 200 equipamentos físicos nem de longa duração.

## Issues do GitHub
- [#8 — Sondagem contínua com scheduler e alertas em tempo real via SSE (RF01)](https://github.com/Solution-Explores/SigmaTI/issues/8) — aberta.

## PRs e referências
- [PR #38 — feat(monitoramento): coleta limitada e SSE autenticado com replay (#8)](https://github.com/Solution-Explores/SigmaTI/pull/38) — integrado à develop.
- [PR #39 — feat: painel operacional conectado à API e SSE (#15)](https://github.com/Solution-Explores/SigmaTI/pull/39) — integrado à develop.
- [PR #42 — docs: conferir aceite de #6 #7 #8 #14 e registrar lacunas](https://github.com/Solution-Explores/SigmaTI/pull/42) — aberto; aguardando integração.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — Issue 08 — Executar monitoramento contínuo e SSE autenticado

CRITÉRIOS ORIGINAIS COBERTOS NO LABORATÓRIO — CONFERÊNCIA DE 20/10/2026

E2 com 30 quedas e SSE real ≤5 s; reinício mantém mesmo incidente ativo; carga de 200 alvos lógicos/2 s em janela estável de 6 s, sem fila/novas perdas/erros, atraso <0,5 s. Scheduler/jitter/contrapressão/métricas integrados. Nenhuma implementação original faltante identificada nesse escopo. Falta revisão/aceite para decidir encerramento. Não representa 200 equipamentos físicos, carga indefinida ou rede hospitalar; E2 até cliente SSE é distinto do teste de tela #15.
Issue: https://github.com/Solution-Explores/SigmaTI/issues/8#issuecomment-6293322604

PR da conferência: https://github.com/Solution-Explores/SigmaTI/pull/42
Relatório: doc/conferencia-issues-6-7-8-14.md, base develop@8cb1e23. CI integrado: 467 testes PG15 aprovados; a suíte existente não cobre os defeitos novos da auditoria. Diagnóstico sintético reproduzido, sem dados operacionais nem alteração em runtime. Issue mantida aberta; revisão técnica sem revisor humano independente atribuído.

--- Histórico anterior ---
INTEGRADO À DEVELOP — PR #38 — 20/10/2026 (UTC−4)

Integração autorizada nesta sessão após revisão técnica e CI aprovado: develop@98b129b90ab6006435a5a11bd56011d40abf2910.
https://github.com/Solution-Explores/SigmaTI/pull/38
CI após merge aprovado: https://github.com/Solution-Explores/SigmaTI/actions/runs/39420340577
Infraestrutura após merge aprovada: https://github.com/Solution-Explores/SigmaTI/actions/runs/39420340727

Continuação em #15, branch feature/15-painel-operacional: conexão do painel à API e ao SSE, com teste real até renderização. Issue #8 permanece aberta para conferência final do escopo; sem revisão humana independente atribuída. Evidências anteriores abaixo preservadas.

--- Histórico anterior ---
IMPLEMENTADO — PR #38 COM CI APROVADO / EM REVISÃO — 20/10/2026 (UTC−4)

https://github.com/Solution-Explores/SigmaTI/pull/38
Head final 047c43d. 454 testes aprovados em 144,77 s com PostgreSQL 15 real, sem falhas/ignorados. Pacote independente, API/aceite HTTP, E6, build/lint, 3 cenários Chromium e infraestrutura aprovados.
API/pacote/PG: https://github.com/Solution-Explores/SigmaTI/actions/runs/39352964495
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39352964567

Artefato postgres-test-results: 30 quedas com SSE real, mediana 197 ms, p95 291 ms, máximo 296 ms, 100% ≤5 s. 200 alvos lógicos/2 s: 602 medições na janela de 6 s, mínimo 2 por alvo, zero perdas/timeouts/erros, fila 0, pico de 7 trabalhos e atraso máximo 13 ms. Reinício manteve sessão e incidente único; replay e encerramento após logout comprovados. Revisão corrigiu HTTP 5xx/ilegível, limite durante failover e CORS de replay/controle.

Guia: engenharia/docs/09-coleta-eventos.md. Evidências: specs/016-coleta-sse/evidencias.md. Revisão técnica Codex, sem revisor independente atribuído. PR aberto, sem merge/encerramento. O ensaio mede chegada ao cliente SSE, não a tela #15, equipamentos físicos ou rede hospitalar. Próxima frente: revisar/integrar #38 e desenvolver #15; depois restauração #25.

--- Histórico anterior ---
IMPLEMENTADO — PR #38 AGUARDANDO CI/REVISÃO — 19/10/2026 (UTC−4)

https://github.com/Solution-Explores/SigmaTI/pull/38
Head af6e29b. Scheduler opt-in limitado, jitter, métricas, detector/medição/incidente transacionais, liderança PostgreSQL e SSE autenticado com replay/revalidação por evento. Sem merge/encerramento.

Local: 10 testes scheduler/stream + 25 PostgreSQL/E2 aprovados. 30 quedas: mediana 690 ms, p95 interpolado 831 ms, máximo 869 ms; 100% ≤5 s até cliente SSE real. 200 alvos lógicos/2 s, janela 6 s: 602 confirmações, zero novas perdas/erros/timeouts, atraso máximo 32 ms. Reinício, incidente único, replay e logout comprovados. CI final confere também reforço de pelo menos duas medições por alvo na janela. Não confundir com tela #15, 200 hosts físicos ou rede hospitalar.

Guia: engenharia/docs/09-coleta-eventos.md. Evidências: specs/016-coleta-sse/evidencias.md. CI completo em execução. Revisão técnica Codex, sem revisor independente atribuído. Próxima frente após revisão/integração: #15, páginas operacionais.

--- Histórico anterior ---
EM DESENVOLVIMENTO — #8 — 19/10/2026 (UTC−4)

Base develop@c288afd após integração autorizada dos PRs #36 (51c21f7) e #37 (c288afd). Branch feature/8-coleta-sse. Escopo: coleta limitada por alvo com jitter, detectores persistidos, incidente único, eventos SSE autenticados com replay e revalidação de sessão. Medir E2 em 30 repetições e carga de 200 alvos; não declarar aceite antes das evidências. Revisão técnica nesta sessão, sem revisor independente atribuído.

--- Histórico anterior ---
PLANEJADO — implementação não iniciada nesta publicação.

Depende de #6/#7 e #14. Scheduler limitado, medições persistidas, incidente sem duplicação, diagnóstico desacoplado e SSE com IDs/Last-Event-ID. Bearer em cabeçalho, sem tokens na URL; encerrar sessão expirada/revogada. Aceite: falha local gera incidente e reinício/reconexão não duplica registros; medir capacidade de 200 alvos locais.

Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9
Disponibilidade de responsável não confirmada; não atribuir conclusão sem evidência.

### https://trello.com/c/I4LgoTUv — ISSUE #25 — Backup e restauração local (etapa entregue)

Lista: Concluído → Concluído. Prazo nativo: preservado.

## Situação vigente — 21/10/2026
[Certo] Etapa local entregue; a issue #25 permanece ABERTA. Restauração em VM no mesmo host: 17 verificações. Outra máquina física não foi validada. O trabalho pendente tem cartão separado; não usar esta coluna como aceite integral de #25.

- Responsável do acompanhamento: @user_vinny / @Vinny1313.
- Revisor independente da próxima etapa: @iohanjheremy11 / @iohanjheremy.
- Prazo da pendência: 03/11/2026, proposto ao orientador; a etapa histórica permanece entregue.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/25

---
## Histórico preservado

## Atualização — 20/10/2026 (Manaus)
[Certo] Restauração executada em VM Ubuntu 24.04.4 / PostgreSQL 15, no MESMO host físico do estágio. As 17 verificações passaram: comparação das 13 tabelas por fingerprints, duas entradas da auditoria, consulta do incidente pela API, preservação após recriar contêiner e novas escritas/IDs.

Base: develop@8cb1e23b0e83066e52d3f81dd7ef05ce82dfc93c. Dados fictícios; IA simulada. VM: sigma-restore-25. O aceite em outro computador físico continua pendente: transportar a VM e ligá-la em casa não equivale, sozinho, a uma nova restauração validada. Issue #25 permanece aberta; este cartão continua concluído somente em seu escopo local.

Evidências locais: laboratorio-vm/evidencias/aceite-vm.json e RESULTADO.md; evidencias-para-casa.zip reúne relatórios selecionados. Nenhum dump, chave ou senha foi publicado no Trello.

---
## Registro anterior (preservado; consultar atualização acima)

## Resumo atual
Somente o escopo LOCAL deste cartão está entregue no PR #40. A issue #25 continua aberta pela restauração em outra máquina. PR #41 contém o planejamento da VM, ainda aberto; documento não comprova execução.

## Issues do GitHub
- [#25 — Herdar do Sentinel: scripts de implantação, backup e smoke test E2E (RNF06)](https://github.com/Solution-Explores/SigmaTI/issues/25) — aberta.

## PRs e referências
- [PR #40 — feat: backup autenticado, restauração e smoke RNF06 (#25)](https://github.com/Solution-Explores/SigmaTI/pull/40) — integrado à develop.
- [PR #41 — docs: planejamento da validacao #25 em VM VirtualBox](https://github.com/Solution-Explores/SigmaTI/pull/41) — aberto; aguardando integração.

## Organização
- Coluna mantida: Concluído.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — Issue 25 — Demonstrar backup e restauração local

CONCLUÍDO — ESCOPO LOCAL INTEGRADO / #25 AINDA ABERTA — 20/10/2026 (UTC−4)

PR #40 revisado tecnicamente e integrado à develop por autorização explícita do usuário.
https://github.com/Solution-Explores/SigmaTI/pull/40
Merge8cb1e23b0e83066e52d3f81dd7ef05ce82dfc93c; head5464664.
CI após merge:todos5checks aprovados. PostgreSQL15 com467testes; recovery8testes+23checks smoke, install.sh, backup/restore, recriação e novas escritas. API/frontend/Chromium, pacote e infraestrutura aprovados.
https://github.com/Solution-Explores/SigmaTI/actions/runs/39433266986
https://github.com/Solution-Explores/SigmaTI/actions/runs/39433267189

Cartão encerra somente demonstração de backup/restauração LOCAL. Issue #25 continua aberta, primeiro critério de outra máquina desmarcado; usuário deixou esse aceite para depois. Ativação systemd e atualização em host real não atestadas. Revisão técnica sem revisor humano independente atribuído. Guias/evidências em doc/backup-restauracao.md e specs/018-backup-restauracao/. Pasta local develop sincronizada e sem alterações.

--- Histórico anterior ---
IMPLEMENTADO — PR #40 COM CI APROVADO / EM REVISÃO — 20/10/2026 (UTC−4)

https://github.com/Solution-Explores/SigmaTI/pull/40
Head54646644be107724e60b11a5c6e7ca03b7cb61c4. Todos10checks push/PR verdes. Recovery:8testes Linux+23checks smoke com install.sh/PG15. Regressão PostgreSQL completa:467aprovados em164,60s no push, sem falhas/ignorados; job do PR também aprovado. API/frontend/diagnóstico Chromium, pacote e infraestrutura aprovados.
https://github.com/Solution-Explores/SigmaTI/actions/runs/39431722684
https://github.com/Solution-Explores/SigmaTI/actions/runs/39431723054
Artifact recovery-test-results: somente report.json.

Backup/restore PostgreSQL+JSONL com HMAC e comparação das tabelas; scripts install/update/smoke e modelo systemd. LocalPG17:13tabelas/2entradas,0,6468s em uma falha ao SSE; recriação e novas escritas/IDs sem colisão. Bundle fictício test-results/recovery-final/bundle e chave fora do bundle; não publicar.

Escopo local do cartão implementado, aguardando revisão/integração. Issue #25 permanece aberta: usuário reservou outra máquina para depois; somente critério smoke verde marcado. Ativação systemd e atualização em host real pendentes. Guia doc/backup-restauracao.md, roteiro specs/018-backup-restauracao/segunda-maquina.md. Revisão técnica, sem revisor humano independente atribuído. Sem merge nesta etapa.

--- Histórico anterior ---
IMPLEMENTADO — PR #40 EM REVISÃO / CI EM EXECUÇÃO — 20/10/2026 (UTC−4)

https://github.com/Solution-Explores/SigmaTI/pull/40
Head5464664. Backup PostgreSQL+JSONL, manifesto HMAC, comparação de todas as tabelas públicas e restauração offline em banco vazio. Scripts install/update/backup/restore/smoke e modelo systemd para API/coleta ativa. Guia doc/backup-restauracao.md.

LocalPG17:23checks aprovados,13tabelas/2entradas de auditoria; uma falha ao SSE em0,6468s. Chave errada/dump alterado/archive inválido/banco ocupado recusados; recriação com volume e novas escritas/IDs comprovadas.7testes+1ignorado Windows(permissão POSIX noCI). CI Linux executa install.sh+smoke comPG15; aguardando.

Usuário escolheu preparar pacote; segunda máquina depois. Bundle fictício local test-results/recovery-final/bundle; chave separada fora do bundle; não publicar. Evidências e roteiro externo specs/018-backup-restauracao/. Não fechar #25: primeiro critério depende de outra máquina; ativação systemd/update em host real também não executados. Sem criptografia embutida/globais/n8n/segredos. Revisão técnica, sem revisor humano independente atribuído.

--- Histórico anterior ---
PLANEJADO — implementação não iniciada nesta publicação.

Escopo parcial, depende de #6/#7. Documentar inicialização e restaurar backup em banco descartável novo; comparar registros/auditoria e registrar evidências. Restauração em outra máquina e demais critérios completos continuam pendentes; não fechar #25 só com ensaio local.

Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9
Disponibilidade de responsável não confirmada; não atribuir conclusão sem evidência.

### https://trello.com/c/cEBw3yYz — ISSUE #14 — Sondagem segura (etapa entregue)

Lista: Concluído → Concluído. Prazo nativo: preservado.

## Situação vigente — 21/10/2026
[Certo] #14 encerrada no GitHub. Este cartão concluído passa a representar somente a sondagem segura. #13 permanece ABERTA: âncora externa, rotação HMAC e verificação agendada pendentes, com cartão próprio. A conclusão de #14 não encerra #13.

- Responsável do acompanhamento: @user_vinny / @Vinny1313.
- Revisor independente da próxima etapa: @iohanjheremy11 / @iohanjheremy.
- Prazo da pendência: 03/11/2026, proposto ao orientador; a etapa histórica permanece entregue.
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/14

---
## Histórico preservado

## Aceite parcial do cartão — 20/10/2026 (Manaus)
[Certo] Usuário aprovou explicitamente #14 e a issue foi encerrada: https://github.com/Solution-Explores/SigmaTI/issues/14
Pinning TCP/HTTP/HTTPS, DNS alternante, socket numérico IPv4/IPv6 e redirect em loopback verificados. O cartão também cobre #13, que permanece pendente; manter em Revisão e testes. Não declarar âncora/rotação ou homologação hospitalar aprovadas.

---
## Resumo atual
A parte #14 (IP fixado/Host/SNI/DNS) está coberta no PR #37. Auditoria transacional PostgreSQL veio no PR #36. Âncora/rotação da #13 e lacunas JSONL da #6 continuam pendentes; o cartão tem escopo maior que apenas a #14.

## Issues do GitHub
- [#14 — Sonda: conectar ao IP já validado (mitigar DNS rebinding / TOCTOU)](https://github.com/Solution-Explores/SigmaTI/issues/14) — aberta.
- [#13 — Auditoria: ancorar o último hash fora da máquina, rotação da chave HMAC e verificação agendada](https://github.com/Solution-Explores/SigmaTI/issues/13) — aberta.

## PRs e referências
- [PR #37 — fix(sondas): conectar ao IP validado e preservar Host/SNI (#14)](https://github.com/Solution-Explores/SigmaTI/pull/37) — integrado à develop.
- [PR #36 — Persistir estado operacional e recuperar aprovações/execuções (#7)](https://github.com/Solution-Explores/SigmaTI/pull/36) — integrado à develop.
- [PR #42 — docs: conferir aceite de #6 #7 #8 #14 e registrar lacunas](https://github.com/Solution-Explores/SigmaTI/pull/42) — aberto; aguardando integração.

## Organização
- Coluna mantida: Revisão e testes.
- O número do título é o da issue do GitHub; um cartão pode representar só uma etapa dela.
- Números K01–K15 são identificadores antigos da sprint, preservados apenas como histórico.
- Padronização em 20/10/2026 (UTC−4); não muda aceite, responsáveis, prazos ou conclusão de issues.

---
## Histórico anterior — Issue 14 — Conectar sondas ao IP validado e auditar operações

ISSUE #14 COBERTA; CARTÃO TEM ESCOPO ADICIONAL — CONFERÊNCIA DE 20/10/2026

IP fixado, uma resolução por série, Host/SNI e testes DNS alternante TCP/HTTP/HTTPS integrados no PR #37. Ambos os critérios da issue #14 atendidos; nenhuma implementação original faltante identificada. Falta revisar/registrar aceite para decidir encerramento. O cartão também inclui auditoria: PostgreSQL transacional veio no PR #36, mas âncora/rotação #13 e lacunas JSONL A1/A2 da #6 permanecem. Não concluir o escopo ampliado por associação. Não foi alegada autenticação PKI real.
Issue: https://github.com/Solution-Explores/SigmaTI/issues/14#issuecomment-6293323312

PR da conferência: https://github.com/Solution-Explores/SigmaTI/pull/42
Relatório: doc/conferencia-issues-6-7-8-14.md, base develop@8cb1e23. CI integrado: 467 testes PG15 aprovados; a suíte existente não cobre os defeitos novos da auditoria. Diagnóstico sintético reproduzido, sem dados operacionais nem alteração em runtime. Issue mantida aberta; revisão técnica sem revisor humano independente atribuído.

--- Histórico anterior ---
INTEGRADO À DEVELOP — PR #37 — 19/10/2026 (UTC−4)

Integração autorizada pelo usuário nesta sessão. Merge c288afd363f772d337139551534cba76b1175a7b. Revisão técnica Codex e CI do head aprovados; sem revisão independente atribuída. CI da base combinada c288afd também aprovado: https://github.com/Solution-Explores/SigmaTI/actions/runs/39349464975 (API/pacote/PostgreSQL) e https://github.com/Solution-Explores/SigmaTI/actions/runs/39349465078 (infraestrutura).

Continuação em #8, branch feature/8-coleta-sse. Nenhuma issue encerrada automaticamente; conferir critérios completos e pendências do escopo maior do card.

--- Histórico anterior ---
IMPLEMENTADO — PR #37 COM CI APROVADO / EM REVISÃO — 19/10/2026 (UTC−4)

https://github.com/Solution-Explores/SigmaTI/pull/37
Head d42edac. Uma resolução por série; todos os IPs devem ser autorizados; conexão numérica IPv4/IPv6 sem segunda resolução; Host/SNI preservados. 37 testes locais aprovados, incluindo DNS alternante, HTTPS simulado, API e HTTP real; pip check/diff check aprovados. CI completo aprovado: 409 testes em 67,42 s com PostgreSQL 15 real, sem falhas/ignorados; pacote independente, aceite HTTP, E6, build/lint, 3 cenários Chromium e infraestrutura aprovados.
API/pacote/PG: https://github.com/Solution-Explores/SigmaTI/actions/runs/39348971206
Infraestrutura: https://github.com/Solution-Explores/SigmaTI/actions/runs/39348970917

Critérios da issue #14 implementados, sem merge/encerramento. Base independente develop@27d2b55; PR #36 permanece separado. O título deste card reúne auditoria além da issue #14: auditoria transacional operacional consta no PR #36; âncora/rotação da #13 continuam pendentes. Não considerar todo esse escopo concluído.

Evidências: specs/015-sondagem-ip-validado/evidencias.md; riscos: engenharia/docs/05-seguranca-e-pendencias.md.

--- Histórico anterior ---
PLANEJADO — implementação não iniciada nesta publicação.

Depende de #6/#7. Resolver DNS uma vez, validar IP e conectar ao endereço validado com Host/SNI preservados; teste contra DNS rebinding. Parte de #13: auditoria transacional concorrente sem texto sensível. A âncora externa permanece pendente.

Plano: https://github.com/Solution-Explores/SigmaTI/blob/feat/9-pacote-sigma-eng/doc/plano-conclusao-2026-10-20.md
Acompanhamento: https://trello.com/c/YGVH2Pg9
Disponibilidade de responsável não confirmada; não atribuir conclusão sem evidência.
### Criar: ISSUE #13 — Âncora externa, rotação HMAC e verificação agendada

Lista: A fazer. Prazo nativo: 2026-11-03T22:00:00.000Z.

## Situação vigente — 21/10/2026
[Certo] Implementação e critérios completos pendentes. Os 7/7 testes concorrentes da rodada-2026-10-22b não comprovam âncora nem rotação. Entrega proposta 03/11, a confirmar pelo orientador em 24/10. Sem PR aberto exclusivo.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy), pendente.
- Prazo: 03/11/2026 às 18h, proposto (UTC−4).
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/13
- PR aberto exclusivo: nenhum confirmado; não mover para Revisão e testes sem PR aberto.


### Criar: ISSUE #25 — Validar restauração em outra máquina física

Lista: A fazer. Prazo nativo: 2026-11-03T22:00:00.000Z.

## Situação vigente — 21/10/2026
[Certo] 17 verificações aprovadas em VM no mesmo host; outra máquina física continua pendente. As três rodadas de 21/10 preservaram o banco, sem repetir o aceite de restauração. Solicitar decisão VM versus host físico em 24/10; prazo proposto 03/11. PR #40 integrado cobriu etapa local; PR #41 aberto é documentação para revisão após a demo.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy), pendente.
- Prazo: 03/11/2026 às 18h, proposto (UTC−4).
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/25
- PR aberto exclusivo: nenhum confirmado; não mover para Revisão e testes sem PR aberto.


### Criar: Testes instáveis — não bloqueia a demo

Lista: A fazer. Prazo nativo: 2026-10-27T22:00:00.000Z.

## Situação vigente — 21/10/2026
[Certo] Não bloqueia a demo. Baseline: provedor9/10, sonda5/10; DNS já falhou na suíte. Sonda original26/30 → shutdown30/30; branch fix/teste-sonda-instavel@3cca38d, sem PR. Provedor: timer atrasa até1,263s; subcausa inconclusiva. Prazo27/10 para triagem/decisão, não correção completa. Aceite final da demo em23/10 permanece obrigatório.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy), pendente.
- Prazo: 27/10/2026 às 18h, triagem proposta (UTC−4).
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/NOVA_INSTAVEIS
- PR aberto exclusivo: nenhum confirmado; não mover para Revisão e testes sem PR aberto.


### Criar: Custo da auditoria — não bloqueia a demo

Lista: Backlog. Prazo nativo: 2026-10-27T22:00:00.000Z.

## Situação vigente — 21/10/2026
[Certo] Não bloqueia a demo. Gravação/verificação relê a trilha completa sob lock; comportamento O(n). Falta benchmark com10k/100k/1M; não afirmar gargalo já medido. Prazo27/10 para triagem/definição do benchmark, não implementação. Preservar detecção de adulteração e bloqueio de novas gravações.

- Responsável: @user_vinny (GitHub @Vinny1313).
- Revisor independente: @iohanjheremy11 (GitHub @iohanjheremy), pendente.
- Prazo: 27/10/2026 às 18h, triagem proposta (UTC−4).
- Issue: https://github.com/Solution-Explores/SigmaTI/issues/NOVA_AUDITORIA
- PR aberto exclusivo: nenhum confirmado; não mover para Revisão e testes sem PR aberto.


