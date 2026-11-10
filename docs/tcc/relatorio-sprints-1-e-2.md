# Relatório das Sprints 1 e 2 do SIGMA

**Período:** 28/10/2026 a 10/11/2026 · **Elaborado em:** 10/11/2026 · **Fontes:** diários de bordo (`docs/tcc/diario-bordo/`), issues, PRs e comentários do GitHub (`Solution-Explores/SigmaTI`), evidências em `docs/tcc/evidencias/`.

Regra deste relatório: só afirma como feito o que está integrado na `develop` ou na `main`, ou o que está registrado como medição com dado bruto. O que não foi verificado vem dito como tal.

---

## 1. Resumo

| | Sprint 1 (28/10 a 03/11) | Sprint 2 (04/11 a 10/11) |
|---|---|---|
| Meta do plano | Fechar a `v1.0.0` | Robustez e evidências |
| Issues do marco | 4 de 4 fechadas (#5, #13, #25, #56) | **2 de 4 fechadas** (#45, #57); #8 e #46 abertas |
| Entrega principal | `v1.0.0` na `main` (tag em `0379374`), aceite completo | Rotas sem efeito falso, testes estáveis, custo da auditoria, experimentos E3 e E4 |
| Pendência herdada | Orientador não consultado sobre desvios | Testes finais da #8 e do E3 não executados; limite de login da #46 sem definição |

**Conclusão curta.** A Sprint 1 cumpriu a meta, com ressalvas declaradas. A Sprint 2 **encerra pelo prazo (10/11), e não por ter cumprido todas as metas**: metade das issues do marco fechou, e o restante entra como **débito técnico na Sprint 3**, a tratar com o orientador no sábado, 14/11. A seção 6 traz a avaliação.

**Plano do orientador (31/10):** Sprint 1 até 03/11, Sprint 2 até 10/11 (#8, #45, #46, #57), Sprint 3 até 17/11; congelamento de código em 11/11; banca entre 01 e 10/12 (edital); 18/11 é o início da preparação da apresentação.

---

## 2. Equipe e contribuições

Os números vêm do GitHub (PRs integrados, issues e comentários). **Não existe diário de bordo do Iohan nem da Joyce no repositório**: só o modelo `docs/tcc/diario-bordo/joyce/_modelo.md`. O que está abaixo é o que o GitHub mostra, e não relato pessoal deles.

### Vinícius ([@Vinny1313](https://github.com/Vinny1313)): integração, aceite e documentação
- 29 dos 34 PRs integrados entre 26/10 e 09/11 são dele (Joyce 3, Iohan 2): reorganização do repositório (#49 a #51), regras da anonimização (#59), âncora externa, rotação de chave e verificação agendada da auditoria (#60), custo da auditoria (#65), estabilização dos testes (#61), CI de infraestrutura (#72, #73), E4 (#78), correção do fechamento de incidentes (#79), release `v1.0.0` (#82), ajustes da #57 (#90) e os diários.
- Diários de bordo: 21/10 a 09/11 neste repositório (outubro reconstruído no PR #93).
- Conduziu o aceite completo da `v1.0.0` e a restauração em máquina física (#25), com o Claude Code.

### Iohan ([@iohanjheremy](https://github.com/iohanjheremy)): revisor e testes de segurança
- **#64** (04/11): regressão dos 14 casos da conferência, conjunto cego do E6 e regras de anonimização.
- **#89** (08 a 09/11): fixa o resultado esperado dos 14 casos, prova o bloqueio ponta a ponta e acrescenta o teto de 20% de bloqueio.
- **#57**: a branch `fix/57-rotas-sem-efeito` (07/11, 23:09 em Manaus), que eliminou as respostas de sucesso sem efeito.
- Pareceres de "Aprovado" nos PRs #59, #60, #61, #62 e #65 e confirmação da revisão independente nas issues #45 e #46 (07 a 08/11).
- **Limite:** os pareceres são **comentários**, e não "Approve" formal do GitHub. Os PRs #64, #68, #78 e #79 foram integrados sem comentário dele.

### Joyce ([@JoyceYasminSilva5](https://github.com/JoyceYasminSilva5)): design system e front
- Integrados: **#52** (DS-01, ambientação do mock e capturas), **#85** (DS-03/DS-04, identidade v4 e logotipos SVG) e **#88** (ajustes da revisão do #85).
- Em rascunho, ainda sem revisão final: **#86** (tipografia, DS-05), **#87** (tokens de cor, DS-06), **#95** (escalas de espaço e texto, DS-07) e **#96** (paleta v4 e contraste, DS-08).
- Frente com prazo em 17/11, como no plano do orientador. As revisões desses PRs estão em andamento em outra sessão do projeto, e este relatório não as antecipa.

---

## 3. Sprint 1 (28/10 a 03/11): "Fechar a v1.0.0"

| Issue | Resultado | Evidência | Ressalva |
|---|---|---|---|
| **#5** Anonimização LGPD fail-closed | Fechada. Recall de proteção **100%**; falsos positivos 1 de 20 (**5,00%**, no limite do critério) | #59, #64, #68, #89; `engenharia/resultados/` | **Recall de transformação 95,12%** no conjunto cego (n = 41): o critério original **não foi atendido**. Foi mantido e declarado, e não reescrito |
| **#13** Auditoria: âncora externa, rotação HMAC, verificação agendada | Fechada (#60) | testes de `test_audit_anchor`, `test_audit_job` | Webhook real do n8n e cofre da chave (#23) **não testados**: só requisição simulada |
| **#25** Backup e restauração (RNF06) | Fechada. Restauração em **máquina física separada**, em 03/11, sem segredo em arquivo versionado | `docs/specs/018-backup-restauracao/segunda-maquina.md` | O plano original era uma VM (#41, guia hoje como histórico); a mudança para máquina física foi decidida em 01/11 |
| **#56** CI de infraestrutura | Fechada. O Docker Hub republicou a tag do PostgreSQL; passou a valer o digest fixado, com PR sem rede e conferência agendada (#72, #73) | `docker-images.lock.json` | **Critério da #56 reduzido**; o orientador ainda não foi informado |

**A `v1.0.0`.** Tag em `0379374` (árvore `d40994f` = aceite em `15568d3`); `main` e `develop` unidas (#81) com árvore `ce03793`. O aceite completo foi executado numa só rodada isolada: duas execuções anteriores foram descartadas (defeito do meu script e sobreposição de processos).

**Outras entregas da Sprint 1:** reorganização do repositório em `backend/`, `frontend/`, `deploy/` e `docs/` (#49 a #51); estabilização de testes (#47, #61); roteiro e diários.

**O que deu errado na Sprint 1 (do diário):**
- O #68 adiantou uma tarefa do Iohan (o #64 era dele), por não ter lido a lista dele antes.
- A VM de teste parava de 15 s a 9 min sem causa identificada, e o E2 nunca fechou 30 de 30 numa única passagem contínua (todas as falhas coincidiram com paradas da VM). A medição final foi feita em máquina física.
- Duas falhas minhas corrigidas na hora: a senha do usuário da VM apareceu na saída de um comando de teste (senha trocada), e escrevi num comentário público que a frente de design system da Joyce estava "descontinuada", o que estava errado (corrigido em seguida).
- O orientador não respondeu à triagem de 01/11.

---

## 4. Sprint 2 (04/11 a 10/11): "Robustez e evidências"

| Issue | Situação em 10/11 | Evidência | O que falta |
|---|---|---|---|
| **#57** Rotas respondem sucesso sem efeito | **Fechada** (#90, 09/11) | `TestRotasSemEfeitoFalso`; rotas planejadas respondem `501` | nada |
| **#45** Testes instáveis (IA, sonda, DNS) | **Fechada** (08/11) | **120 execuções isoladas, zero falhas**, SHA `55a1796` | Orientador não foi consultado: o critério de 30/30 foi aceito em **máquina física** no lugar da VM |
| **#8** Sondagem contínua e SSE (RF01) | **Aberta** | Três rodadas de 200 alvos em 03/11: p95 queda→SSE de 0,781 a 0,835 s, **100% dentro de 5 s**, atraso máximo do calendário **0,044 s** (meta 0,5 s) | Essas rodadas são do SHA `9918a17`, **antes do #79**, que mexeu no caminho de ingestão. Repetir pós-#79 era a tarefa de 09/11 e **não foi executada** |
| **#46** Custo da auditoria | **Aberta**, 3 de 4 critérios atendidos | Login com 100 mil entradas: **4.291 ms → 12,9 ms**; gravação em rajada 125,8 ms; contenção com 8 processos: **35% de falhas → 0,6%** | **Limite de login não definido** (proposta: 50 ms para login, 150 a 200 ms para gravação em rajada). Depende do orientador |

**Experimentos e medições feitos na Sprint 2**
- **E3 (burn rate)** passou nas duas condições depois do #79: queda de 10 min chega a `page` em **52,0 s**; corte de 10 s **não pagina** (antes pagava aos 45 s, defeito do ciclo de vida do incidente, corrigido na #71). Duas execuções por condição, em loopback. Evidência: `docs/tcc/evidencias/e3-pos-71.md`.
- **E4 (fuzzing da cadeia de auditoria)**, N = 1000, semente 20261104: **100% de detecção** em troca de byte, linha apagada e linhas trocadas; **0% no corte do fim da trilha** (limite de qualquer cadeia lida só de si mesma; é o que a âncora cobre).
- **MTTD, MTTA, MTTR e burn rate** medidos (PR #70) e **balanço dos dados do TCC** com os números desfavoráveis dentro (PR #80).
- **#71** (incidente de disponibilidade que nunca fechava sozinho) corrigida no #79.

**Opção D da #46 (ponto de verificação assinado), em andamento.** Para a "partida fria" da trilha (a primeira gravação de um processo novo verifica a trilha inteira, cerca de 1 s com 100 mil entradas), o PR #94 acrescenta um arquivo `<trilha>.checkpoint` assinado por HMAC. O CI está verde (539 testes passaram, 13 deles novos; a `develop` tem 526). **Não foi medido o ganho, o ADR 0002 não foi atualizado e falta a revisão independente do Iohan.** Mexe no núcleo de integridade; **não integrar antes da revisão**.

**Documentos e decisões da Sprint 2:** banca entre 01 e 10/12 (edital); regra de pastas dos experimentos (#11: manter e documentar); PRs antigos #41 (integrado como histórico) e #42 (fechado); #74 (digest do PostgreSQL mantido, só a base Alpine mudou; sem varredura de CVE); painel P2 decidido como versão parcial (MTTA e MTTR), **não implementado**.

---

## 5. Pontos de atenção honestos

**Não executado ou não verificado**
- **Rodadas de carga da #8 e E3 da `v1.0.0` no estágio** (planejadas para 09/11): **não realizadas**, por relato do Vinícius em 10/11. A evidência do E3 na versão entregue não existe.
- **Painel P2 em versão parcial** e **opção D**: não concluídos.
- **Testes locais:** a máquina de casa estava sem Python e sem virtualização para o Docker. Parte do trabalho da Sprint 2 foi validada só pelo CI.
- **Achados A1 e A2** do relatório antigo do #42 (cadeia inválida com duas instâncias; `verificar` retornando 0): **não reconferidos**.
- **Varredura de CVE** nas imagens: não feita.

**Medições com limite declarado:** tudo em loopback e numa máquina; 2 execuções por condição no E3 (não 30); passo de amostragem de 2 s na condição A do E3; trilhas sintéticas nos benchmarks da auditoria; o SLO de 99,9% em 30 dias é o padrão do módulo, e não um objetivo acordado com o hospital.

**Desvios que o orientador ainda não conhece**
1. Critério da #56 reduzido.
2. #45 fechada com máquina física no lugar da VM, sem consulta.
3. Recall de transformação de 95,12% na #5.
4. Dia e horário da banca (edital: 01 a 10/12) e licença (#63, rascunho que aguarda os autores).
5. Limite de login da #46.

---

## 6. Avaliação: a Sprint 2 pode ser dada por encerrada?

**Sim, pelo prazo; não, pelas metas.** O marco venceu em 10/11, e o plano do orientador já previa o destino do que não fechasse: em 31/10 ele comentou na #46 que, se não fechasse até o congelamento de 11/11, ela deveria ser registrada como **débito técnico no TCC (Sprint 3)**. A #8 não tem essa regra escrita, mas a situação é parecida: o que falta é uma prova, e não uma funcionalidade.

| Critério | Situação | Leitura |
|---|---|---|
| Issues do marco concluídas | 2 de 4 (50%) | Parcial |
| O que está aberto é desenvolvimento ou prova? | Prova (#8) e decisão (#46) | Nenhuma funcionalidade nova pendente |
| Há regressão ou defeito aberto na `develop`? | Não conhecido; CI da `develop` verde (526 testes) | Estável |
| Há evidência antes do #79 que ainda vale? | Sim, 3 rodadas da #8; mas o #79 mexeu no caminho quente | Prova insuficiente até repetir |

**Como dizer isso sem exagero:** "Sprint 2 encerrada em 10/11 com duas das quatro issues concluídas (#45, #57). A #8 e a #46 passam para a Sprint 3 como débito técnico: a #8 exige repetir as rodadas de carga depois do #79, e a #46 exige o limite de login acordado com o orientador." **Não dizer** "Sprint 2 cumprida" nem "#8 concluída".

**Débito técnico para a Sprint 3**
1. #8: três rodadas de carga pós-#79 (SHA e máquina anotados) e fechamento da issue.
2. #46: definir o limite de login; decidir sobre a opção D (PR #94: medir, atualizar o ADR 0002, revisão do Iohan). Se o congelamento de 11/11 valer, a D só entra com a exceção do orientador ou depois da banca.
3. E3 na `v1.0.0`: evidência ausente.
4. Painel P2 parcial (MTTA e MTTR); o MTTD segue sem fonte do instante real da falha.
5. Capítulo 7 do TCC (hipóteses confirmadas e refutadas, trabalhos futuros) e a lista de limitações da seção 5.
6. Varredura de CVE e atualização do digest do PostgreSQL (#74), depois da banca.
7. "Approve" formal do Iohan nos PRs que revisou.

**Para a conversa de sábado (14/11)**
- Confirmar o encerramento da Sprint 2 com 2 de 4 e o destino da #8 e da #46.
- Definir o limite de login (#46).
- Aprovar os desvios da seção 5 (critério da #56, máquina física na #45, recall de 95,12% na #5).
- Confirmar se o congelamento de 11/11 se mantém, dada a banca entre 01 e 10/12.
- Confirmar dia e horário da banca e a licença (#63).

---

## 7. Fontes

Diários de bordo: [04/10](diario-bordo/04-10-2026.md) e [21/10](diario-bordo/21-10-2026.md) (e os de outubro do PR #93), [01/11](diario-bordo/01-11-2026.md), [02/11](diario-bordo/02-11-2026.md), [03/11](diario-bordo/03-11-2026.md), [04/11](diario-bordo/04-11-2026.md), [05/11](diario-bordo/05-11-2026.md), [06/11](diario-bordo/06-11-2026.md), [07/11](diario-bordo/07-11-2026.md), [08/11](diario-bordo/08-11-2026.md), [09/11](diario-bordo/09-11-2026.md).
Evidências: `docs/tcc/evidencias/` (E3, auditoria #46), `engenharia/resultados/` (E4, E6), `docs/tcc/balanco-dos-dados.md`, `docs/tcc/limitacoes.md`.
Plano: `docs/planejamento/plano-pos-demo-issues-abertas.md` e `docs/planejamento/roteiro-sprint-2-estagio.md`.
