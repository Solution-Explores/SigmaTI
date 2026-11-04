# Sprint 2 no estágio (04 a 10/11/2026)

Roteiro para trabalhar a Sprint 2 na máquina do estágio, sem depender do computador de casa. Segue o plano do orientador: Sprint 2 fecha em 10/11, o congelamento de código é em 11/11 (só correção de bug P0) e a banca é em 18/11. A lista completa continua em [tarefas-vinicius-sprint-1.md](tarefas-vinicius-sprint-1.md); aqui está só o que fazer lá, na ordem.

**Este roteiro tem só as atividades do Vinícius.** O que depende do Iohan está numa tabela à parte ("Esperando o Iohan"), para esperar a resposta dele em vez de fazer no lugar dele. Conferido em 04/11 contra as tarefas do Iohan, as issues e os cartões do Trello.

[Voltar ao índice do planejamento](README.md)

## Resumo em poucas linhas

- **Dias úteis até o congelamento:** quarta 04, quinta 05, sexta 06, segunda 09 e terça 10. Sábado e domingo ficam como folga, não como plano.
- **A Sprint 2 tem 4 issues abertas:** #8, #45, #46 e #57. Nenhuma fecha só com o seu trabalho: a #8 espera a #45, a #45 espera a revisão do Iohan, a #46 espera o orientador e a #57 é do Iohan.
- **O que é seu e cabe nesta semana:** montar a base do front da Joyce (ela está parada), o E4 da #11 (fuzzing da cadeia), a #71 (incidente que nunca se fecha sozinho), o aceite da release e a rodada final no SHA candidato. O painel com MTTD e burn rate é P2 e só entra se sobrar tempo.
- **O que é de outras pessoas:** a #57 e as revisões da #45 e da #46 (Iohan), o limite de login da #46 (orientador), o front (Joyce, prazo 17/11).
- **Máquina:** use a máquina física do estágio. A VM do VirtualBox não está acessível, então as medições seguem com o desvio já declarado nos registros anteriores (máquina física em vez de VM).

## Antes de começar (20 minutos)

Faça isto uma vez, ao chegar. Não precisa do pendrive: o repositório é público e tudo o que a Sprint 2 usa já está na `develop`, exceto o que está nos PRs #69 e #70 (veja o passo 1).

1. **Programas:** Git, Python 3.12 ou superior, Node (o CI usa a versão 24), Docker Desktop **ligado e em contêineres Linux**, e a GitHub CLI (`gh auth status` precisa mostrar a sua conta).
2. **Clonar e entrar na `develop`:**

```bash
git clone https://github.com/Solution-Explores/SigmaTI.git
cd SigmaTI
git switch develop
git pull --ff-only origin develop
```

3. **Ambiente Python** (os mesmos comandos do CI):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip install -e "./engenharia[api,dev]"
python -m pip check
```

4. **Teste de fumaça:** `python -m pytest backend/tests/test_infrastructure_policy.py -q` deve passar (31 testes). Se o Docker estiver desligado, é aqui que aparece.
5. **PostgreSQL de teste:** os testes de banco e as medições precisam de um PostgreSQL descartável em `SIGMA_TEST_DATABASE_URL`. Suba um contêiner com a imagem `postgres:15.19-alpine3.24@sha256:f7d23353e1b15400d22ebe31189f4d314b87a4c129cc400c8c2d8d4ca127bf81`, com senha gerada na hora e **sem publicar a porta em `0.0.0.0`**, e apague o contêiner e o volume no fim do dia. Nenhuma senha vai para arquivo versionado.

> A restauração da #25 já está feita. Não leve a chave de auditoria, o pacote `72948b9` nem o pendrive de restauração: nada disso é necessário agora.

## Ordem sugerida

A ordem abaixo põe primeiro o que destrava os outros. A Joyce está parada esperando a base nova, e nenhum dos itens técnicos seus bloqueia ninguém, então o front vem antes.

| Quando | Passo | O que é | Tamanho |
|---|---|---|---|
| Quarta 04 | 1 | Integrar #69 e #70 (você clica no merge) | 15 min |
| Quarta 04 | 2 | Abrir o PR semanal dos diários e fechar o #66 | 15 min |
| Quarta 04 | 3 | Base nova do front da Joyce | 2 a 3 h |
| Quinta 05 | 4 | E4 da #11: fuzzing da cadeia | 2 h |
| Sexta 06 | 5 | #71: incidente que nunca se fecha sozinho | 3 h, ou 0 se for declarado |
| Segunda 09 | 6 | Aceite da release e rodada final no SHA candidato | 1 a 2 h |
| Segunda 09 | 7 | Painel com MTTD e burn rate (P2, só se sobrar tempo) | 3 h |
| Terça 10 | 8 | Conferência final da Sprint 2 e registro das limitações | 1 a 2 h |

O que depende do Iohan e do orientador corre em paralelo e está nas tabelas "Esperando o Iohan" e "Decisões", mais abaixo. Quando a resposta chegar, o que sobra para você é pequeno.

## Passos, um por um

### Passo 1. Integrar #69 e #70

- **#69** corrige a hierarquia de títulos do Diagnóstico (CI verde, mesclável).
- **#70** traz os dois scripts de medição (`scripts/medir_e3.py` e `scripts/medir_incidentes.py`), as evidências do E3 e o balanço dos dados do TCC (CI verde, mesclável).
- **Por que primeiro:** o passo 5 reexecuta o E3 e precisa do `medir_e3.py`, que só existe no #70.
- **Como:** você faz o "Merge pull request" (merge commit, não squash). O classificador de permissões não deixa o Claude integrar PR sem revisão registrada.
- **Pronto quando:** `git pull --ff-only origin develop` traz os dois e o CI da `develop` fica verde.

### Passo 2. PR semanal dos diários

- A branch `docs/diario-03-11` tem tudo que o #66 tinha e mais (diário de 03/11 e atividades corrigidas), e o #66 está em conflito.
- **Fazer:** abrir o PR semanal a partir de `docs/diario-03-11` e fechar o #66 com um comentário que aponte para o novo.
- **Pronto quando:** um só PR de diários da semana aberto e o #66 fechado.

### Passo 3. Base nova do front da Joyce

- **Por que agora:** ela está parada, e o prazo dela é 17/11.
- **Contexto:** os PRs #53, #54 e #55 foram fechados em 03/11 porque a `feature/front-design-system` está 46 commits atrás da `develop` e usa a pasta antiga `sigma-frontend/`. O cherry-pick do `8661916` já não é necessário: ele já está na `develop`.
- **Fazer:** criar uma branch nova a partir da `develop` e levar os commits do mock (`3241071`, `afac415`) e os de documentação dela, com `-c merge.directoryRenames=true`. Reescrever à mão a seção `dev:mock` do `frontend/README.md`. O passo a passo está em [atividades-joyce.md](atividades-joyce.md), na seção "Base de trabalho".
- **Cuidados:**
  - O `design-system/exemplo` repete o `docs/design/prototipo-figcraft/`, que já está na `develop`. Decidir onde fica.
  - Corrigir os caminhos dos documentos dela (`sigma-frontend/` para `frontend/`, `../doc/…` para `docs/processo/…` e `docs/operacao/…`).
  - O guia dela manda `git switch develop` e `dev:mock`, que só existem na branch dela. Trocar a versão de Node (ele diz 22.12, o CI usa 24).
- **Pronto quando:** `npm ci`, `npm run lint`, `npm test`, `npm run build` e `npm run dev:mock` funcionam na branch nova, o PR está aberto contra a `develop` com CI verde, e a Joyce recebe o aviso para começar a trabalhar a partir dela.

### Passo 4. E4 da #11: fuzzing da cadeia de auditoria

- **O que é:** gerar cadeias de 1000 entradas, aplicar uma mutação aleatória (alterar um byte de um campo, remover uma linha ou trocar duas) e conferir que `verificar()` aponta um índice menor ou igual ao da mutação em 100% dos casos.
- **Onde:** `engenharia/experimentos/` (já existe `exp_deteccao.py` como modelo) e `engenharia/resultados/` para o CSV. O verificador é o método `verificar()` da `AuditChain`, em `engenharia/sigma_eng/audit_chain.py`.
- **Fazer:**
  1. Script com semente fixa, N = 1000 por cadeia e várias mutações por tipo.
  2. CSV com o tipo da mutação, o índice mutado e o índice que a verificação apontou.
  3. Uma linha no relatório declarando o número de casos e a taxa de detecção.
  4. Atualizar o E4 em `engenharia/docs/03-metodologia-experimental.md` (hoje "A fazer").
- **Pronto quando:** script, CSV e documento no mesmo PR, 100% de detecção com o índice correto (ou, se algum caso falhar, o caso descrito sem esconder), e comentário na #11. **Não feche a #11**: o E5 continua sem medição.
- **Tamanho:** 2 h. É a última lacuna da #11 que ainda cabe antes do congelamento.

### Passo 5. #71: incidente que nunca se fecha sozinho

- **O problema:** quando o alvo volta a responder, o incidente aberto continua aberto, porque `resolvido_em` só é escrito pelas rotas manuais. Consequência medida no E3: um corte de 10 s gera `page` aos 45 s, com o alvo no ar.
- **Decisão sua antes de começar** (as duas saídas são válidas):

| Opção | O que faz | Custo | Risco |
|---|---|---|---|
| **A. Corrigir** | Na gravação de uma medição bem-sucedida, fechar o incidente de disponibilidade aberto daquele alvo e escrever `resolvido_em`. Teste em `backend/tests/test_postgres_operational.py`. Depois reexecutar o E3 e atualizar a evidência | ≈ 3 h | Mexe no caminho de ingestão (`backend/persistence/operational.py`) perto do congelamento e da #57 |
| **B. Declarar** | Escrever no texto do TCC que o SLO é calculado sobre intervalos que só fecham por intervenção humana, e deixar a #71 como limitação | ≈ 0 h | O sistema continua com falso `page` em oscilação curta |

- **Recomendação:** A, se a sexta-feira 06 estiver livre, porque o falso `page` é um defeito real e a correção é pequena. Se a semana apertar, B, desde que fique escrito.
- **Se for A:** MTTA e MTTR já medidos mudam de significado (hoje o MTTR de 0,191 s vem de o script resolver cada incidente por chamada de API). Reexecute `python scripts/medir_e3.py --output <saida>.json --minutos-a 10 --segundos-b 10 --observacao-b 5` e `scripts/medir_incidentes.py`, e atualize `docs/tcc/evidencias/e3-burn-rate.md` e `incidentes-mttd-burn.md`.
- **Pronto quando:** na condição B do E3 (corte de 10 s) o sistema não dispara `page`, com teste e evidência no PR. Ou, na opção B, o texto da limitação commitado.

### Passo 6. Aceite da release e rodada final no SHA candidato

- **Por que:** a #5 e a #56 já estão integradas, então o que falta para a `v1.0.0` é repetir o aceite completo na `develop` atual. A #8 entra na `v1.0.0` com a limitação do E2 declarada; a #8 e a #45 são da Sprint 2 e não seguram a tag. Esta é também a "rodada final no SHA candidato" do cartão VALIDAÇÃO do Trello (prazo 10/11): registre o MTTD e o burn rate para o texto do TCC. A VM do cartão está inacessível, então a rodada é na máquina física, com o desvio declarado.
- **Fazer:** o bloco da seção 5 de [tarefas-vinicius-sprint-1.md](tarefas-vinicius-sprint-1.md) (branch `release/1.0.0`, `pytest`, `validate_api_acceptance`, `validate_panel`, `validate_collection`, `validate_infrastructure`), com o PostgreSQL de teste ligado. Abra o PR para a `main`, integre, crie a tag no commit entregue, leve as correções de volta à `develop` e comente na issue da versão o SHA, a data e o resultado.
- **Cuidados:** rode **uma** execução de cada vez (duas execuções sobrepostas já contaminaram um resultado em 03/11). A `main` já recebeu os quatro arquivos da #56 pelo #73; confira que chegam sem conflito.
- **Antes da tag:** decidir se #69 e #70 entram na release (eles são de antes do congelamento).

### Passo 7. Painel com MTTD e burn rate (P2)

- **Só se sobrar tempo.** É o primeiro item a cortar (cartão PAINEL do Trello, prazo 10/11).
- **Atenção:** não é só trabalho de frontend. `/api/eng/incidentes/resumo` devolve `MTTD: n=0` sempre, porque nada grava o instante real da falha. Hoje o painel já poderia mostrar MTTA e MTTR; o MTTD exige antes decidir de onde vem esse instante.
- **Pronto quando:** o painel mostra o que o sistema realmente mede, com teste, ou o corte fica registrado no diário e no TCC.

### Passo 8. Conferência final

- Reler as 4 issues da Sprint 2 e marcar só o que tem teste ou comando.
- Registrar no TCC as limitações que ficam: recall de transformação 95,12% no conjunto cego (n = 41), deriva lenta 16,7%, RNF04 sem evidência, tudo em loopback, e a #71 (corrigida ou declarada).
- Depois do congelamento (11/11) entra só correção de bug P0.

## Esperando o Iohan (não fazer no lugar dele)

Estas atividades são dele, pela lista [tarefas-iohan-sprint-1.md](tarefas-iohan-sprint-1.md) e pelos cartões do Trello. O que sobra para você é cobrar e, quando a resposta vier, fechar o que depende dela.

| O quê | Onde está | O que você faz quando ele entregar |
|---|---|---|
| **#57**, rotas que respondem sucesso sem efeito (opção B, resposta 501, 8 a 11 h; P0 da Sprint 2, prazo 10/11). É dele: está na lista dele e o cartão do Trello tem o nome dele. No GitHub a issue ainda não tem responsável; ele deve se atribuir | Issue #57 | Revisar o PR, conferir os testes por rota e a matriz RBAC, e integrar com o CI verde |
| **Revisão independente da #45 e da #46.** Ele é o revisor nomeado nas duas. Para a #45, é o que falta na caixa "PR da correção da sonda revisado" (#47 e #61) | Issues #45 e #46 | Marcar a caixa da #45 (a evidência de 30/30 já está postada: 120 execuções isoladas, zero falhas), fechar a #45 e depois fechar a #8 (as três rodadas de carga já estão postadas) |
| Revisões dos PRs #59 a #65, que foram integrados sem revisão registrada | PRs integrados | Nada. Só registrar no diário que a revisão veio |

- **Se o Iohan não responder até segunda 09:** registrar na #45 que a revisão independente não aconteceu e quem a substituiu, e deixar a decisão de fechar ao orientador. Não marque a caixa dele por conta própria.
- **Mensagem curta sugerida:** "Iohan, bom dia. O #64 e o #68 já estão integrados e a #5 fechou. Para a Sprint 2 preciso de duas coisas: um comentário de 'revisado' no #47 e no #61, e a #57 com você. Se for começar, ela vem depois dos PRs que já entraram na `develop`."

## Decisões que não são do Claude (a resposta destrava)

| # | Decisão | De quem | Efeito |
|---|---|---|---|
| A | Opção A ou B da #71 | Você | Passo 5 |
| B | Limite de custo de login da #46 (medido 12,9 ms; proposta de 50 ms) | Orientador | Última caixa da #46 |
| C | Critério de recall do E6 na #5 e confirmação da banca de 18/11 e da licença | Orientador | Sprint 3 |
| D | Digest novo do PostgreSQL (#74): manter o atual ou revisar | Você | Só informativo, sem pressa |

## Ao fim de cada dia

- Commitar o que ficou pronto, em PR pequeno e com CI verde. Cada um integra o próprio PR.
- Atualizar o diário de bordo do dia (um arquivo por dia, um PR por semana).
- Remover o contêiner de teste, o volume e qualquer arquivo com credencial gerada durante o dia.
- Ter em mente: a lista de afazeres em [tarefas-vinicius-sprint-1.md](tarefas-vinicius-sprint-1.md) é a fonte de verdade e deve ser atualizada quando algo fechar.
