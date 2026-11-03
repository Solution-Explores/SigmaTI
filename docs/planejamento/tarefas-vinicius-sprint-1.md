# Atividades do Vinícius: Sprint 1 e Sprint 2 (até 10/11/2026)

Segue as sprints e as orientações do orientador (milestones e comentários das issues). A Sprint 1 fecha a `v1.0.0` em 03/11, e 02/11 é feriado. A Sprint 2 fecha em 10/11, com o congelamento de código anunciado nesse dia. Cada um integra o próprio PR com o CI verde, como em [fluxo-de-trabalho-tcc.md](../processo/fluxo-de-trabalho-tcc.md). Vale o plano do orientador (milestones das Sprints 1, 2 e 3; o planejamento pós-demo está descontinuado desde 02/11). As atividades do Iohan estão em [tarefas-iohan-sprint-1.md](tarefas-iohan-sprint-1.md).

**Divisão de responsabilidades:** Vinícius e Iohan desenvolvem; a Joyce cuida só do front. Máquina física, VM e testes relacionados a elas são do Vinícius.

## Resumo

| Quando | Atividade | Pts | Situação em 02/11 (noite) |
|---|---|---|---|
| Sprint 1 | Triagem com o orientador | 1 | Enviada em 01/11, sem resposta |
| Sprint 1 | #5: regras de anonimização | 4 | Em andamento |
| Sprint 1 | #25: restauração em máquina física e testes de VM | 2 | Em andamento |
| Sprint 1 | #13: âncora externa e rotação HMAC (candidata a 10/11) | 5 | Pronta no PR #60, falta integrar |
| Sprint 1 | Release e tag `v1.0.0` | 2 | Falta fazer |
| Sprint 2 | #45: testes instáveis (triagem até 04/11) | 4 | Triagem e medição feitas, PR #61 sem revisão |
| Sprint 2 | #8: três rodadas de carga na VM | 2 | Medida em 01/11, falta marcar a caixa |
| Sprint 2 | Validar o front da Joyce (PRs #52 a #55) | 2 | Falta fazer |
| Sprint 2 | #46: custo da auditoria | 3 | Pronta no PR #65, falta integrar |
| Sprint 2 | Validação final na VM (MTTD e burn rate) | 2 | Falta fazer |
| Sprint 2 | Painel exibe MTTD e burn rate (P2) | 3 | Falta fazer |

## Situação em 02/11/2026 (noite)

Nenhuma issue está fechada: todo o trabalho pronto está em PR aberto, sem integração. Por isso o painel das sprints mostra 0%. "Pronta" abaixo significa código e testes feitos com CI verde, aguardando revisão e merge.

### Concluído (pronto, aguardando integração)

- **#13** (5 pts): PR #60 com âncora externa, rotação com `kid` e verificação agendada. Conferência de critérios comentada na issue. Falta revisar, integrar e fechar.
- **#46** (3 pts): PR #65, empilhado sobre o #60, com CI 5/5 verde. Login com 100 mil entradas de 4.291 ms para 13 ms (meta: 50 ms). Evidência para o TCC em `docs/tcc/evidencias/`. Falta o Iohan revisar (já marcado) e a integração depois do #60.
- **#5, parte das regras**: PR #59 com as regras para os 14 casos do orientador, CI verde.
- **#45, parte do código**: PR #61 com o timer de IA de 13 s e a espera por evento no teste de DNS, CI verde.
- **#25, preparação**: roteiro e script de ambiente (PR #62), pacote e `candidato-72948b9.bundle` gerados, ensaio completo em casa sem falhas, pendrive montado em `E:\LEVAR-PENDRIVE\`.
- **Conferência de critérios** comentada nas issues #8, #13, #25, #45 e #46, com duas caixas marcadas na #8.
- **Triagem de 01/11:** auditoria do épico #31 registrada, #48 fechado, #41 e #42 atualizados, e comentário de triagem ao orientador publicado no #31 (2 pontos para confirmar, 5 avisos, incluindo o diagnóstico da #56).
- **#8, medição:** rodada 9 na VM (candidato `da7ff94`) com três cargas de 200 alvos seguidas aprovadas, em duas passagens (p95 queda→SSE de 0,32 a 0,38 s; atraso máximo do calendário de 0,015 a 0,042 s).
- **#45, triagem e medição:** timer de IA de 14 s para 13 s com justificativa registrada, e rodada 9 com 30 execuções isoladas por teste (sonda, DNS e agendador em 30/30; provedor de IA em 13,07 a 13,11 s).
- **Comparativo** professor × plano × repositório salvo em `docs/planejamento/`.

### Em andamento

- **Triagem com o orientador:** enviada em 01/11 no épico #31. Falta a resposta dele em dois pontos: concordar em mover a #25 para a Sprint 2 (o milestone da #25 ainda mostra Sprint 1) e dizer se há regra da faculdade sobre propriedade intelectual para a licença. Ficou sem comentário dele nas #13, #25 e #56. Falta também o pedido explícito de confirmar a banca de 18/11. Os PRs #41 e #42 foram atualizados, mas seguem abertos.
- **#5:** o PR #64 do Iohan (14 casos de regressão e conjunto cego) está com CI vermelho em `test-config` e `test-postgres`, por um teste só: `test_safe_block_is_not_counted_as_transformation`. Causa: o critério de aprovação do E6 passou de recall de transformação (95,12%) para recall de proteção (100%). Já comentei o PR com as duas saídas. **Falta decidir o critério** com o Iohan e o orientador. Depois: corrigir o teste ou o critério, deixar o #64 verde, integrar #59 e #64, e registrar o recall com intervalo de confiança e a limitação na #5. Pendem 3 caixas: testes por tipo de identificador, falha injetada e relatório de recall em `resultados/`.
- **#25:** falta o critério principal, restaurar em outra máquina. Fica para **terça, 03/11, no estágio**. Se o Iohan integrar os PRs antes, regenerar o pacote no SHA oficial. Depois: preencher `segunda-maquina.md`, comentar o resultado na issue e só então marcar a caixa.
- **#45:** a triagem de 01/11 e a rodada 9 estão registradas na issue. Faltam: revisão do Iohan e integração do PR #61; marcar as caixas depois do merge; e **decidir** se o E2 é aceito com a ressalva das paradas da VM (29/30 em três passagens) ou se é refeito na máquina física. O 4º teste da lista original (`test_scheduler`, 28/30) deve corresponder à linha "Encerramento do agendador" da rodada 9, que fechou 30/30 em duas passagens. Confirmar que é o mesmo teste antes de dar por coberto.
- **#8:** as três cargas seguidas já foram medidas e aprovadas (rodada 9). Falta marcar a caixa "≥ 200 alvos", o que só vale depois da integração do #61 e do fechamento da #45, e declarar a limitação do E2 na issue.

### Falta fazer

- **Release e tag `v1.0.0`:** só depois de #5 e #56 integradas. Hoje a #5 depende dos PRs #59 e #64, e a #56 está aberta.
- **Validar o front da Joyce** (PRs #52 a #55): não iniciado. Todos abertos.
- **Validação final na VM** (MTTD e burn rate): não iniciada.
- **Painel com MTTD e burn rate** (P2): não iniciado e é o primeiro a cortar.

### Pendências de terça, 03/11

1. Restauração da #25 na máquina do estágio (pendrive pronto; a chave vai por outro canal).
2. Enviar a cobrança ao Iohan (revisões dos PRs, conjunto cego da #5) e decidir o critério de recall.
3. Cobrar a resposta do orientador à triagem de 01/11 (mover a #25, licença, banca, diagnóstico da #56).
4. Revisar e integrar o #60, o que deixa a #13 pronta para fechar.
5. Dar dono à #57 (P0, Sprint 2, sem dono, comentário nem PR).
6. Planejar o balanço de dados do TCC depois do teste de terça.

**Risco:** a Sprint 1 fecha em 03/11 com 1 dia útil. Se a #13 e a #25 escorregarem, pedir o aval do orientador para movê-las a 10/11, como já previsto abaixo. Nunca se corta a #5 nem a release.

Sprint 1: 14 pts contra ≈ 17 de capacidade, com 01/11 já em curso. Se não couber, a #13 vai para 10/11 com o aval do orientador, depois a #25. Nunca se corta a #5 nem a release.

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

Falta só o critério "restaurar o backup em outra máquina reproduz incidentes e auditoria íntegra". As 17 verificações em VM do mesmo host já passaram, e o smoke test está verde no CI.

1. Siga o guia [backup-restauracao.md](../operacao/backup-restauracao.md) e preencha o registro [segunda-maquina.md](../specs/018-backup-restauracao/segunda-maquina.md): data, operador, identificação fictícia das máquinas, SHA e versão do PostgreSQL.
2. Confira o manifesto autenticado com a chave transferida por canal separado, rode `restore.sh` e registre o código de saída e o resumo.
3. Verifique o inventário de tabelas e contagens, o incidente original pela API, a auditoria íntegra, a recriação do contêiner com o mesmo volume sem perda e a nova escrita sem colisão de IDs.
4. Comente na issue o resultado. Não anexe dump, trilha bruta, chaves, tokens nem configurações reais.
5. **Se a máquina não estiver disponível:** declare a limitação no TCC e mova a issue para a Sprint 2 com o aval do orientador.

### 4. Issue #13: âncora externa e rotação HMAC (5 pts, candidata a 10/11)

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

Registre a triagem na issue até 04/11 com:

1. a decisão sobre o timer de IA (14 s ou 13 s), com medição;
2. a hipótese para o atraso de 0,957 s do E2 de carga (meta 0,5 s), que também segura a #8;
3. a troca do `sleep(0.25)` fixo do teste de DNS por sincronização por evento.

Depois cubra o 4º teste (`test_scheduler`, 28/30) e estabilize. Teste de tempo que falhar, repita isolado antes de concluir.

### 7. Issue #8: três rodadas de carga na VM (2 pts)

Dois critérios já estão atendidos (SSE em até 5 s em 30 quedas; reinício sem duplicar incidentes). Falta "≥ 200 alvos sem acumular atraso". O orientador pede: fechar a #45 e registrar **três rodadas de carga consecutivas** dentro da meta. Registre o resultado de cada rodada na issue e feche.

### 8. Validar o front da Joyce (2 pts)

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

Leitura incremental ou cache do último `seq/hash`, preservando a recusa de gravação após adulteração. Meta de 50 ms com 100 mil registros (hoje ≈ 3 s). Depende da #13. Se não fechar até o congelamento de 11/11, registre como débito técnico no TCC.

### 10. Validação final na VM (2 pts)

Rodada final no SHA candidato, registrando MTTD e burn rate para o texto do TCC.

### 11. Painel com MTTD e burn rate (3 pts, P2)

Exibir MTTD e burn rate no painel (hoje só pela API). É o primeiro item a cortar se a carga passar de ≈ 100% no check-in de 07/11.

---

## Regras que valem para tudo

CI verde antes do merge, cada critério com teste ou comando, sem segredos, evidência comentada na issue. A issue só fecha com todos os critérios atendidos. Se não, deixe aberta e liste o que falta. Depois do congelamento de 11/11, só entra correção de bug P0.
