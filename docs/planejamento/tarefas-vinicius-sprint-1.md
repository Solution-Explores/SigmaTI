# Atividades do Vinícius: Sprint 1 e Sprint 2 (até 10/11/2026)

Segue as sprints e as orientações do orientador (milestones e comentários das issues). A Sprint 1 fecha a `v1.0.0` em 03/11, e 02/11 é feriado. A Sprint 2 fecha em 10/11, com o congelamento de código anunciado nesse dia. Cada um integra o próprio PR com o CI verde, como em [fluxo-de-trabalho-tcc.md](../processo/fluxo-de-trabalho-tcc.md). Vale o plano do orientador (milestones das Sprints 1, 2 e 3; o planejamento pós-demo está descontinuado desde 02/11). As atividades do Iohan estão em [tarefas-iohan-sprint-1.md](tarefas-iohan-sprint-1.md).

**Divisão de responsabilidades:** Vinícius e Iohan desenvolvem; a Joyce cuida do design e do front, **com prazo final em 17/11**. Em 03/11 os PRs #53, #54 e #55 dela foram fechados sem integrar, porque a branch `feature/front-design-system` está 46 commits atrás da `develop` e usa a pasta antiga `sigma-frontend/`: o trabalho é retomado sobre uma base nova tirada da `develop`, que o Vinícius monta. A DS-02 saiu à parte, no PR #69. Máquina física, VM e testes relacionados a elas são do Vinícius.

## Afazeres (situação em 03/11/2026, fim do dia)

Esta é a lista de trabalho. A ordem dentro de cada bloco é a sugerida. O detalhe de cada issue está nas seções das sprints, mais abaixo.

> **Atualização de 04/11 (manhã):** a ordem da semana, por dia, está em [roteiro-sprint-2-estagio.md](roteiro-sprint-2-estagio.md), só com as atividades do Vinícius. Em 04/11 o PR semanal dos diários (#75) foi integrado e o #66 fechado. O #69 e o #70 ficaram para o estágio.

### A. Depende só de você

| # | Afazer | Onde | Tamanho |
|---|---|---|---|
| A1 | ~~Decidir o `atividades-joyce.md`~~ **Feito em 03/11:** vale a reescrita de 02/11, que foi a enviada a ela (mesmo SHA-256 do arquivo entregue). Conflito do #66 resolvido | PR #66 | feito |
| A2 | **Enviar ao Iohan** a lista dele e a cobrança (o texto foi redigido em 02/11 e não consta como enviado) | fora do repo | 10 min |
| A3 | **Cobrar o orientador**, que não comenta desde 31/10: critério de recall da #5, limite de login da #46, confirmação da banca de 18/11 e licença. Avisar que #5 e #56 passam para 10/11 | #31 | 20 min |
| A4 | **Atribuir dono** à #56 e à #57, que estão sem ninguém no GitHub | GitHub | 2 min |
| A5 | **Montar a base nova do front da Joyce** a partir da `develop`, com o mock e os documentos dela em `frontend/`. Ela está parada esperando isso, e o prazo dela é 17/11 | branch nova | 2 a 3 h |
| A6 | **Triar os PRs antigos** #41, #42 e #63 (licença, que aguarda os autores) | PRs | 20 min |

### B. Trabalho técnico seu, sem depender de ninguém

| # | Afazer | Depende de | Tamanho |
|---|---|---|---|
| B1 | ✅ **Feito.** Três rodadas consecutivas de 200 alvos em máquina física, postadas na #8. Atraso máximo do calendário de 0,044 s contra a meta de 0,5 s. A caixa não foi marcada: o critério é combinado com o fechamento da #45 | — | — |
| B2 | ✅ **Feito.** 120 execuções isoladas (30 de cada um dos quatro testes) na `develop` `55a1796`, em máquina física, **zero falhas**, postadas na #45. A caixa de 30/30 **não** foi marcada, porque o mesmo critério exige o PR da sonda revisado, e nem o #47 nem o #61 têm revisão registrada | Iohan (C) | — |
| B3 | ✅ **Feito**, com desvio: medido em máquina física, não na VM, que está inacessível aqui. MTTD 0,712 s, MTTA 0,159 s, MTTR 0,191 s, burn rate 7,519 em 1 h. No PR #70 | — | — |
| B4 | ⚠️ **Mudou de natureza.** Não é trabalho de frontend: `/api/eng/incidentes/resumo` devolve `MTTD: n=0` sempre, porque nada grava o instante real da falha. Exibir MTTD exige antes decidir de onde vem esse instante. MTTA e MTTR o painel já poderia mostrar | decisão de projeto | 3 h + |
| B5 | ✅ **Feito.** `docs/tcc/balanco-dos-dados.md`, no PR #70. Oito itens medidos, cinco verificados, duas lacunas que ainda cabem, quatro para as limitações | — | — |
| B6 | **E4 da #11:** fuzzing da cadeia, N = 1000 com semente fixa e CSV. O verificador já existe; falta o laço. **Última lacuna que ainda cabe antes do congelamento** | — | 2 h |
| B7 | **#71:** decidir a resolução automática de incidente. Corrigir e remedir o E3, ou declarar no texto que o SLO só fecha intervalos por intervenção humana | decisão sua | 3 h ou 0 |

### C. Esperando o Iohan

| # | O quê | Efeito se não vier |
|---|---|---|
| C1 | **#64**, o conjunto cego da #5, com CI vermelho desde 02/11. O item 1 da lista dele. O PR #68 é uma proposta pronta, que ele pode integrar no #64 | **A #5 não fecha, e sem ela não sai a tag `v1.0.0`** |
| C2 | **#56**, o PR estrutural (CI hermético separado da deriva agendada, mais o teste com lock divergente). O escopo diminuiu: os PRs da Joyce saíram | A #56 não fecha, e a release também espera por ela |
| C3 | **Revisões independentes** da #45 e da #46. Ele é o revisor nomeado nas duas e não revisou nenhum PR | Caixa de revisão da #45 aberta; a #46 fecha sem revisão independente |
| C4 | **#57**, P0 da Sprint 2, sem dono e sem PR | Fica para a Sprint 2 |

### D. Esperando o orientador

| # | O quê | Trava |
|---|---|---|
| D1 | Critério de recall do E6 na #5: transformação (95,12% no cego) ou proteção (100%) | Fechamento da #5 |
| D2 | Limite acordado do custo de login da #46. Medido 12,9 ms; proposta de 50 ms | Última caixa da #46 |
| D3 | Confirmação da banca em 18/11 e da licença | Planejamento da Sprint 3 |
| D4 | Aval para mover #5 e #56 para 10/11 | Formalizar o atraso da Sprint 1 |

### E. Release `v1.0.0`

Só depois de **#5 e #56 integradas**. O aceite completo já passou hoje na `develop` `b657509` (`pytest` 522 passed, K10 com 20 verificações, painel com 4 testes, E2 e carga dentro da meta), mas precisa ser **repetido na `develop` final** antes da tag.

### F. Sprint 3, a partir de 11/11

Congelamento do código em 11/11, só correção de bug P0. Texto e resultados do TCC, slides, ensaio em 13 e 14/11, roteiro de demonstração, backup do ambiente e VM de contingência, e o capítulo de trabalho futuro (que agora inclui o design system descontinuado).

## O que fechou em 03/11

- **#25 fechada:** restauração em máquina física separada, com registro em `segunda-maquina.md`.
- **#13 fechada:** âncora externa, rotação com `kid` e verificação agendada, com 34 testes conferidos na `develop`.
- **#46 com 3 de 4 caixas:** contenção entre processos medida (com 8 processos em rajada, as falhas por lock caíram de 35% para 0,6%).
- **#45 com 2 de 4 caixas:** triagem registrada, timer de IA em 13 s e E2 refeito na máquina física.
- **Integrados:** #59, #60, #61, #62, #67 e #65. O #69 (hierarquia de títulos do Diagnóstico) está pronto, com CI verde, aguardando merge.
- **Fechados sem integrar:** #53, #54 e #55, porque a branch `feature/front-design-system` está 46 commits atrás da `develop` e usa a pasta antiga `sigma-frontend/`. **A frente da Joyce continua**, com prazo em 17/11, sobre uma base nova tirada da `develop` (item A5).
- **Aceite da release** executado na `develop` `b657509`.

- **E3 da #11 medido:** queda de 10 min pagina em 52,0 s, conforme a previsão analítica. **Corte de 10 s pagina indevidamente**, com o alvo no ar, porque incidentes nunca se fecham sozinhos. Abriu a **#71**.
- **#70 aberto:** MTTD, MTTA, MTTR, burn rate, o balanço dos dados do TCC e o E3, com dado bruto e dois scripts reprodutíveis.
- **Correções postadas** em #53, #54, #55 e #56, desfazendo a afirmação errada de que a frente da Joyce teria sido descontinuada.

**Risco em aberto:** a Sprint 1 terminou hoje com #5 e #56 abertas, as duas dependendo do Iohan. O orientador já previu mover para 10/11 com justificativa, e é isso que o item A3 pede.
---

## Sprint 1 (prazo 03/11)

### 1. Triagem com o orientador (1 pt)

**Situação em 02/11:** enviada em 01/11 no épico #31 (2 pontos para confirmar e 5 avisos), junto com a auditoria do épico e a triagem dos PRs (#48 fechado, #41 e #42 atualizados). Sem resposta dele. Falta pedir de forma explícita a confirmação da banca e o aval para mover a #13.

Conteúdo enviado ao orientador:

- Pedido para mover a **#13** para 10/11 (a carga da Sprint 1 passa do planejado). O milestone mantém 03/11 até ele decidir.
- Decisão sobre a **#25**: VM ou máquina física. Você pediu em 24/10 e não há registro de resposta.
- Confirmação de que a banca é em 18/11 e se há risco de antecipação, e a licença do repositório.
- Aviso de que o diagnóstico da **#56** está incompleto: o commit `8661916` (22/10) já faz a `main` checar só pelo digest, e `python scripts/validate_infrastructure.py --verify-registry` passa na `main`. Só as branches antigas, sem esse commit, estão vermelhas. Atualizar o lock não é necessário.
- Aviso de que, no fluxo atual, a revisão cruzada não é obrigatória, mas as verificações independentes que ele pediu continuam (conjunto cego escrito pelo Iohan, evidência da #25 na issue).

Depois registre a auditoria no épico #31 e triagem dos PRs #41, #42 e #48 (fechar ou atualizar).

### 2. Issue #5: regras de anonimização (4 pts, risco alto)

O orientador testou 14 casos fora do corpus e todos passaram sem bloqueio. Ele deixou quatro sugestões no último comentário da issue.

- **Corrigir as regras** em `backend/sanitizer.py` para os 14 casos: nomes após "Dr" sem ponto, após "Paciente:", "Sra." e sem cargo; login; CPF com espaços; registro de atendimento; hostname como `PACS-01` e `pacs01`; telefone, RG, data de nascimento e endereço.
- **Detector residual de nomes:** avaliar uma lista de nomes próprios brasileiros (IBGE) que **bloqueia** em vez de substituir, e medir os falsos positivos.
- **Falha injetada:** exceção ou resíduo no anonimizador resulta em nenhuma chamada externa, com registro na trilha de auditoria (fail-closed).
- **Não olhar o conjunto cego.** O Iohan escreve a regressão dos 14 casos em `backend/tests/test_sanitizer.py` e o conjunto cego. Você ajusta as regras pelos 14 casos públicos, sem ver o conjunto dele. Só depois ele mede o recall.
- **Relatório e TCC:** o Iohan escreve o relatório em `docs/historico/resultados/`. Você declara a limitação no texto e relata o recall com intervalo de confiança.
- **Pronto quando:** os 14 casos passam, a falha injetada está testada, o recall no conjunto cego é ≥ 99% (ou a limitação está declarada) e a #5 tem o comentário de evidência.

### 3. Issue #25: máquina física e testes de VM (2 pts)

> **Fechada em 03/11.** Restauração executada em máquina física separada; registro em `../specs/018-backup-restauracao/segunda-maquina.md`. Mantido abaixo como histórico.

Falta só o critério "restaurar o backup em outra máquina reproduz incidentes e auditoria íntegra". As 17 verificações em VM do mesmo host já passaram, e o smoke test está verde no CI.

1. Siga o guia [backup-restauracao.md](../operacao/backup-restauracao.md) e preencha o registro [segunda-maquina.md](../specs/018-backup-restauracao/segunda-maquina.md): data, operador, identificação fictícia das máquinas, SHA e versão do PostgreSQL.
2. Confira o manifesto autenticado com a chave transferida por canal separado, rode `restore.sh` e registre o código de saída e o resumo.
3. Verifique o inventário de tabelas e contagens, o incidente original pela API, a auditoria íntegra, a recriação do contêiner com o mesmo volume sem perda e a nova escrita sem colisão de IDs.
4. Comente na issue o resultado. Não anexe dump, trilha bruta, chaves, tokens nem configurações reais.
5. **Se a máquina não estiver disponível:** declare a limitação no TCC e mova a issue para a Sprint 2 com o aval do orientador.

### 4. Issue #13: âncora externa e rotação HMAC (5 pts, candidata a 10/11)

> **Fechada em 03/11.** PR #60 integrado, 34 testes conferidos na `develop`. Mantido abaixo como histórico.

- Âncora externa do último hash (e-mail/n8n ou push para outro servidor).
- `key id` por entrada, com rotação preservando o histórico.
- Job diário de `verificar()` com alerta.
- ADR 0002 atualizado, e testes de remoção total e de rotação.
- Se o Iohan sobrar tempo, ele pode pegar o job diário e o ADR, combinando antes.
- Se não fechar até 03/11, siga para 10/11 com o aval do orientador. A #46 depende desta issue.

### 5. Release e tag `v1.0.0` (2 pts)

A release só sai depois de #5 e #56 integradas.

```bash
git switch develop && git pull --ff-only origin develop
git switch -c release/1.0.0
python -m pytest
python scripts/validate_api_acceptance.py
python scripts/validate_panel.py
python scripts/validate_collection.py
python scripts/validate_infrastructure.py
```

Alguns scripts exigem PostgreSQL de teste em `SIGMA_TEST_DATABASE_URL`. Com o CI verde, abra o PR para a `main`, integre, crie a tag `v1.0.0` no commit entregue, leve as correções de volta à `develop` e comente na issue da versão o SHA, a data e o resultado. A #8 entra na `v1.0.0` com a limitação do E2 declarada, porque ela fecha na Sprint 2.

---

## Sprint 2 (04 a 10/11)

### 6. Issue #45: testes instáveis (4 pts, triagem até 04/11)

> **Em 03/11:** triagem registrada na issue e 2 das 4 caixas marcadas. Faltam a rodada 30/30 e a revisão independente.

Registre a triagem na issue até 04/11 com:

1. a decisão sobre o timer de IA (14 s ou 13 s), com medição;
2. a hipótese para o atraso de 0,957 s do E2 de carga (meta 0,5 s), que também segura a #8;
3. a troca do `sleep(0.25)` fixo do teste de DNS por sincronização por evento.

Depois cubra o 4º teste (`test_scheduler`, 28/30) e estabilize. Teste de tempo que falhar, repita isolado antes de concluir.

### 7. Issue #8: três rodadas de carga na VM (2 pts)

Dois critérios já estão atendidos (SSE em até 5 s em 30 quedas; reinício sem duplicar incidentes). Falta "≥ 200 alvos sem acumular atraso". O orientador pede: fechar a #45 e registrar **três rodadas de carga consecutivas** dentro da meta. Registre o resultado de cada rodada na issue e feche.

### 8. Validar o front da Joyce (2 pts)

> **Substituída em 03/11.** Os PRs #53, #54 e #55 foram fechados sem integrar, e o trabalho da Joyce é retomado sobre uma base nova tirada da `develop`. O que fica para o Vinícius é montar essa base, não validar aqueles PRs. O defeito de acessibilidade que o #53 apontava foi corrigido à parte, no PR #69. Mantido abaixo como histórico.

O que o orientador pediu sobre o front se limita ao CI verde nos PRs dela (#56). Esta validação é nossa, como responsável pelo repositório. Os PRs #52 a #55 têm só `validate-compose` vermelho (a causa é a #56); `test-config`, `test-package`, `test-postgres` e `test-recovery` passam.

**Antes de validar:** a `feature/front-design-system` está 42 commits atrás da `develop` e usa os caminhos antigos (`sigma-frontend/`, `main.py` na raiz), enquanto a `develop` tem `frontend/` e `backend/`. Qualquer integração exige atualizar a base e resolver essa diferença. Não copie arquivos de integração para contornar.

| PR | O que é | Como validar |
|---|---|---|
| #52 DS-01 | Ambientação do mock e 7 capturas (só documentação) | Rode `npm ci` e `npm run dev:mock`. Confira que os 3 perfis (`suporte.joyce`, `analista.joyce`, `gestor.joyce`) e os 5 cenários (`?cenario=vazio`, `erro`, `lento`, `falha-trilha`) batem com as 7 capturas |
| #53 DS-02 | Hierarquia de títulos do Diagnóstico (h2 para h3, h3 para h4), em `Diagnostic.jsx` e `App.css` | Veja o diff (4 linhas adicionadas, 2 removidas). Rode `npm run lint`, `npm test` e `npm run build`. Confira que nenhum texto, id ou `aria-labelledby` mudou. Rode o E2E real (`e2e/`, que sobe Python e a API) e o axe. É código que vai para o produto |
| #54 DS-03 | Proposta de marca e paleta | **Não mergear antes da decisão da equipe.** Só confira que é documentação e que nada foi aplicado ao painel |
| #55 DS-04 | 9 logotipos SVG | Depende do #54. Confira que os SVGs são válidos e sem script embutido. Se a equipe escolher outra identidade, fechar sem merge |

**Checklist C0 do backlog dela** (`design-system/tarefas-joyce.md`), para #53 e capturas: dois temas, desktop 1440 px e celular 390 px sem corte; contraste de texto ≥ 4,5:1; foco visível; teclado (Tab, Enter, link "Ir para o conteúdo"); alvos de 44×44 px; textos em português; sem mexer em `src/api.js`, `useResource.js`, `useEvents.js`, `useActionRequest.js` e `mockApi.js`.

**Resultado esperado:** um comentário em cada PR com o que foi verificado e o veredito. Recomendo integrar na `feature/front-design-system` só #52 e #53, com testes e E2E verdes, e deixar #54 e #55 para a reunião de decisão. A integração da branch na `develop` só entra antes do congelamento de 11/11 se tudo estiver verde. Caso contrário, fica para depois da banca. Nada de front novo depois de 11/11.

### 9. Issue #46: custo da auditoria (3 pts, P1)

> **Em 03/11:** PR #65 integrado e 3 das 4 caixas marcadas. Falta só o limite de login, que depende do orientador.

Leitura incremental ou cache do último `seq/hash`, preservando a recusa de gravação após adulteração. Meta de 50 ms com 100 mil registros (hoje ≈ 3 s). Depende da #13. Se não fechar até o congelamento de 11/11, registre como débito técnico no TCC.

### 10. Validação final na VM (2 pts)

Rodada final no SHA candidato, registrando MTTD e burn rate para o texto do TCC.

### 11. Painel com MTTD e burn rate (3 pts, P2)

Exibir MTTD e burn rate no painel (hoje só pela API). É o primeiro item a cortar se a carga passar de ≈ 100% no check-in de 07/11.

---

## Regras que valem para tudo

CI verde antes do merge, cada critério com teste ou comando, sem segredos, evidência comentada na issue. A issue só fecha com todos os critérios atendidos. Se não, deixe aberta e liste o que falta. Depois do congelamento de 11/11, só entra correção de bug P0.
