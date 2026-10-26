# Plano até a demonstração de 27/10/2026

Elaborado em 21/10/2026 e reajustado em 22/10/2026 (UTC−4, Manaus). A demonstração
ao professor orientador deixou de ser no sábado, 24/10, às 9h. A entrega passou
para a **terça, 27/10/2026, às 18h**. Este plano substitui, até essa data,
o cronograma da sprint de 15 a 20/10, que não foi cumprido. O prazo das demais
entregas depende do orientador.

Os três dias a mais servem para reduzir risco (ensaios e revisão sem pressa).
O escopo não cresce.

Este plano funciona como a "Sprint 0" e termina na demonstração. O que vem depois
(28/10 a 17/11, com a banca em 18/11) está em
[plano-sprints-pos-demo.md](plano-sprints-pos-demo.md). Em 23/10 este plano foi
alinhado a ele: disponibilidade do Vinícius, uso do fim de semana, proposta ao
orientador e pendências herdadas.

## Situação de partida

[Certo] Atualização de 22/10 à noite (UTC−4): `develop` remoto em `75b1874ee5f83f55ab12837249a9c701fd67cef1`, após #43 (`dbc464d`, 22h25) e #44 (`75b1874`, 22h52). Os dois estão integrados; CI dos heads aprovado. Não há Approve formal no GitHub; o LGTM do Iohan no #44 é comentário.

- #6 e #8 seguem abertas; o aceite final é em 23/10 e os critérios completos continuam pendentes.
- #47 (`3cca38d`), só teste, aberto para Iohan; CI de 22/10 tinha quatro verificações aprovadas e `validate-compose` reprovado (run 39894956404), divergindo do resumo recebido. **Atualização de 23/10:** no head `0b372cb`, as cinco verificações estão aprovadas.
- PRs documentais #41/#42 e reorganização ficam depois da demo, em 28/10.
- A carga falhava na base `8cb1e23`; #44 já integrado. Resultados da VM no candidato antigo e do Windows no integrado têm origens/métodos distintos; aceite da rodada 7 ainda pendente.

## Escopo

Entra até terça:

1. [Feito em 22/10] PR #43 integrado; aceite final ainda pendente.
2. [Feito em 22/10] #44 retargetado para `develop`, CI aprovado e integrado após #43.
3. Executar o aceite mínimo na `develop` integrada.
4. Preparar o roteiro e os dados fictícios da demonstração.
5. Fazer dois ensaios e gravar uma versão de contingência.

Fica para depois da demonstração:

- PRs #41, #42 e `feature/trail-fase1`, que não alteram o que será demonstrado.
- #13: âncora externa, rotação da chave HMAC e verificação agendada.
- #5: revisão contra os critérios completos e novos casos adversariais.
- #25: restauração em outra máquina física (entra antes apenas se o aceite de sexta passar e sobrar tempo no fim de semana).
- Release `v1.0.0` na `main`.

## Equipe

| Pessoa | Disponibilidade | Papel neste plano |
|---|---|---|
| Vinícius | Segunda a sexta, manhã e tarde; sábado o dia todo; domingo só de manhã (estimativa: ~6 h focadas por dia útil, ~8 h no sábado, ~4 h no domingo) | Integração, aceite, roteiro e apresentação |
| Iohan | Dias úteis após as 22h; sábado à tarde e domingo | Revisão dos PRs e execução independente do roteiro |

Joyce continua no projeto, mas não participa deste plano.

## Regras

- Quem revisa não é quem fez. Com duas pessoas, o revisor é sempre o outro.
- O Vinícius abre os PRs até as 18h para o Iohan revisar na mesma noite.
- Nenhum merge direto em `develop` ou `main`; integração somente por PR com CI aprovado.
- Cada cartão do Trello registra responsável, revisor, prazo e link do PR.
- Uma issue só é encerrada com todos os critérios atendidos.

## Cronograma

| Dia | Vinícius | Iohan (após 22h; sábado à tarde e domingo) | Codex (VM) |
|---|---|---|---|
| Qua 21/10 | Conferir o pacote vindo do estágio (`SHA256SUMS`), subir a VM e autenticar o `gh`. Conferir o CI do #43 e esboçar o roteiro. | Revisar o PR #43. | Rodadas 1 a 3. |
| Qui 22/10 | Corrigir os achados e integrar o #43. Retargetar o #44 e rodar o CI. Preparar os dados da demonstração. | Revisar o PR #44. | Rodada 4 (custo da auditoria); rodada 5 (aceite do candidato `0a6ce35`). |
| Sex 23/10 | Integrar o #44. Executar o aceite. Ensaio 1. | Revisar a correção da sonda e conferir o roteiro. | Aceite na `develop` integrada. |
| Sáb 24/10 | Dia todo: painel manual (feito em 23/10), ajustes do ensaio 1 e atender dúvidas do Iohan. Só leitura: levantar os caminhos (imports, uvicorn, alembic, CI, scripts) que a PR de estrutura vai mover em 28/10. | À tarde: executar o roteiro sozinho, no próprio computador, a partir da `develop` integrada. | — |
| Dom 25/10 | Manhã: corrigir o que o Iohan achou e fechar o checklist de terça. Opcional: #25. | Segunda execução independente, se houver correções. Opcional: #25. | — |
| Seg 26/10 | Corrigir pendências. Ensaio 2. Gravar a contingência. Atualizar os números dos slides. **Às 18h, congelar o SHA da entrega.** | Após 22h: conferir o SHA congelado e rodar o smoke. | Após 18h: bateria completa no SHA congelado. |
| Ter 27/10 | Manhã: ensaio final e smoke no SHA congelado. Tarde: revisar proposta e slides. **16h: preparar o ambiente. 18h: demonstração.** | Apoio à noite; sem tarefa crítica. | — |

O aceite de sexta usa os testes e scripts existentes. Os scripts do painel e da coleta
exigem um PostgreSQL de teste em `SIGMA_TEST_DATABASE_URL`:

```powershell
$env:SIGMA_TEST_DATABASE_URL = '<url do PostgreSQL de teste>'
python -m pytest
python scripts/validate_api_acceptance.py
python scripts/validate_panel.py
python scripts/validate_collection.py
```

Os dados fictícios vêm de `scripts/serve_browser_acceptance.py`, que cria usuários dos
quatro perfis, alvos, SLO, 25 horas de medições, uma aprovação e um registro de auditoria.

### Caminho crítico

Se o PR #44 não estiver integrado até sexta de manhã, a entrega usa a `develop`
sem ele, com poucos alvos, e não apresenta o resultado de carga. O CI do #43 e do
#44 depende de `validate_infrastructure.py --verify-registry`; a falha de 22/10
(tag do postgres republicada no Docker Hub) foi tratada checando só o digest.
A falha conhecida com 200 alvos não deve ser exibida como resolvida.

## Roteiro da demonstração (cerca de 15 minutos)

1. **Arquitetura (1 min).** Alvo → sonda → PostgreSQL → detector → SSE → painel.
2. **Perfis de acesso (2 min).** Login como `suporte_n1`, `analista_redes` e `gestor_ti`;
   mostrar uma ação recusada com 403.
3. **Coleta ao vivo (4 min).** Derrubar o serviço TCP de teste. O incidente aparece no
   painel sem recarregar. Reconhecer, resolver e mostrar MTTD, MTTA e MTTR.
4. **SLO (2 min).** Orçamento de erros e burn rate do alvo com histórico.
5. **Governança (2 min).** Aprovação e verificação da cadeia de auditoria.
6. **IA e LGPD (2 min).** Enviar um alerta com nome e CPF fictícios e mostrar o texto
   anonimizado antes da chamada ao provedor simulado.
7. **Resultados (2 min).** Testes e ensaio de carga registrados, CI aprovado.

### Limites a declarar

- O provedor de IA é simulado.
- Os testes usam loopback e dados fictícios.
- Os números de carga do PR #44 (200 alvos, intervalo de 2 s, 32 trabalhos) foram
  medidos em laboratório e não equivalem a homologação hospitalar.
- Os resultados de anonimização valem para o corpus avaliado (E6), não para dados reais.

## Proposta ao orientador

A banca está marcada para 18/11/2026 e pode ser antecipada. Por isso a proposta
original (tudo até 03/11) foi dividida em sprints semanais, de quarta a terça.

- **Entregue:** #2, #3, #4, #7, #9, #14 e #15; #6 e #8 se o aceite de sexta passar.
- **Sprint 1, 28/10 a 03/11:** #5, aceite final de #6 e #8, reorganização do
  repositório e release `v1.0.0` (aceite em 31/10 e 01/11). Reserva para o retorno
  do orientador sobre a demonstração.
- **Sprint 2, 04/11 a 10/11:** #13 (âncora externa e rotação HMAC), #25 em outra
  máquina, #45/#47 (testes instáveis e CI) e #46 (custo da auditoria). **Mudança
  proposta:** #13 e #25 saem do prazo de 03/11 para 10/11, porque não cabem junto
  com a `v1.0.0`. Depende da concordância do orientador.
- **Sprint 3, 11/11 a 17/11:** código congelado em 11/11, texto do TCC, slides e
  ensaio. Banca em 18/11.
- **Trabalho futuro:** expansão (#10, #16–#19, #21, #22, #30, #23) e validações
  externas (#11, #12, #20, #24, #26–#29), que dependem de hospital, hardware ou
  coleta prolongada. Entram como capítulo de trabalho futuro do TCC, não como código
  antes da banca.

## Depois da demonstração: sprints

Detalhes, estimativas e riscos em [plano-sprints-pos-demo.md](plano-sprints-pos-demo.md).

| Sprint | Período | Meta |
|---|---|---|
| S1 | 28/10 a 03/11 | Fechar a `v1.0.0` (#5, #6, #8, estrutura, aceite da release) |
| S2 | 04/11 a 10/11 | Robustez e evidências (#13, #45/#47, #46, #25) |
| S3 | 11/11 a 17/11 | Congelamento, texto, slides e ensaio; banca em 18/11 |

- Capacidade do Vinícius pela disponibilidade acima: ~36 h na S1 e ~42 h por semana
  na S2 e na S3. A S1 tem só 4 dias úteis, porque 02/11 (segunda) é Finados.
- O Iohan segue com ~10 h por semana (noites, sábado à tarde, domingo).
- Nada da S1 entra antes do congelamento de 26/10; a PR de estrutura só começa em 28/10.

## Andamento

### Divisão do trabalho (definida em 21/10)

| Quem | O quê |
|---|---|
| Vinícius + Claude | Ambiente local, integração dos PRs, aceite, roteiro, slides e proposta |
| Codex | Todos os testes na VM: regressão, carga de 200 alvos (5 repetições por SHA) e o #25. Resultado em `validacao-vm/rodada-2026-10-22/RESULTADO.md`. Não faz push nem merge. |
| Iohan | Revisão #47 em 23/10 à noite; roteiro independente em 24/10 à tarde; conferir SHA e smoke em 26/10 após 22h. Revisões anteriores preservadas nos registros históricos. |

### Quarta, 21/10: feito
- O pacote do estágio foi conferido: `SHA256SUMS` sem falhas nas 16 entradas.
- `gh` autenticado. O worktree limpo da `develop@8cb1e23` está em `Desktop\sigmati-develop`, com `.venv`, `npm ci` e Chromium do Playwright.
- Acesso à VM recuperado com uma chave nova em `D:\_virtual\sigma-restore-25\segredos\`. A VM ficou desligada para liberar memória do host.
- Merge local de `develop` + #43 + #44 sem conflito, no worktree `Desktop\sigmati-integracao`. Resultado: 433 testes aprovados sem banco e 20/20 no aceite da API.
- Os PRs foram conferidos antes da revisão, e os achados foram corrigidos e enviados:
  - #43 (`8662ea9`): verificações mortas de auditoria removidas e `SanitizationError` mantido; 430 testes aprovados.
  - #44 (`696ca7b` e `ddd4840`): nota sobre o lote inteiro ser descartado, e #43 incorporado ao branch.
  - CI verde nos dois PRs.
- Roteiro de revisão publicado no #43 para o Iohan.
- Material da demo:
  - [roteiro-demonstracao.md](roteiro-demonstracao.md);
  - [demo/](demo/) com `subir_demo.py`, `demo.ps1`, a proposta ao orientador, o checklist de terça e os rascunhos de issue (custo da auditoria e testes instáveis, hoje as issues #46 e #45);
  - slides em https://claude.ai/artifact/38N6oK7SdYLf5mxAM24ZZh.
- Ajustes no roteiro:
  - o 403 e o burn rate são mostrados por `curl`;
  - o MTTD é calculado por `POST /api/eng/incidentes/metricas`;
  - a anonimização foi conferida: `[NOME_REMOVIDO] [CPF_REMOVIDO] relatou falha no [SWITCH_REDE]`.

### Quarta, 21/10: VM, rodada 1 (Codex), concluída às 02:41

Fonte: `validacao-vm/rodada-2026-10-22/RESULTADO.md`. Os 171 hashes do `SHA256SUMS.txt` conferem.

| Versão | Testes | Carga de 200 alvos |
|---|---|---|
| `develop` `8cb1e23` | 464/467 | 0 de 5 |
| #43 `a97fe1b` | 476/477; só o E2 falha, o que era esperado | — |
| #44 `4350632` | 487/488; o timeout de IA mediu 16,1 s, com limite de 15 s | 5 de 5 |
| merge `develop` + #43 + #44 | **488/488** | **5 de 5**, mais o E2 e o validador |

- No merge: p95 queda→SSE de 0,33 a 0,41 s, atraso máximo de 0,185 s, 0 erros e 0 ciclos perdidos.
- **Caminho crítico:** o #44 sai do risco técnico e a demo tende a mostrar a carga. A confirmação vem no aceite de sexta.
- A rodada 2 (`rodada-2026-10-22b`) está em andamento. Ela cobre os SHAs novos `8662ea9` e `ddd4840` e os 3 testes instáveis por tempo, com entrega até quinta às 10h.
- Os slides de resultados já mostram esses números, marcados como provisórios.

### Quarta, 21/10: VM, rodada 2 (Codex), concluída às 03:14

Fonte: `validacao-vm/rodada-2026-10-22b/RESULTADO.md`. Os 179 hashes do `SHA256SUMS.txt` conferem.

- Candidato **`ddd4840`** (develop + #43 + #44): **489/489** testes, carga **5/5** (atraso máximo de 0,093 s, 0 erros), painel aprovado.
- O Codex concluiu "não apto" por causa de 3 testes instáveis. **Reclassificação:** os PRs não alteraram esses testes nem o código testado, então as falhas já existiam antes. **O candidato está apto para integração.**
- A rodada 3 (`-22c`) está em andamento: linha de base `8cb1e23`, hipótese da sonda e diagnóstico do provedor.
- A correção do teste da sonda está pronta no branch local `fix/teste-sonda-instavel` (`3cca38d`), sem push.
- Rascunho de issue: [demo/issue-testes-instaveis.md](demo/issue-testes-instaveis.md).
- Slides atualizados: 489/489 e atraso máximo de 0,093 s.

### Quarta, 21/10: VM, rodada 3 (Codex), concluída às 03:56
- Fonte: `validacao-vm/rodada-2026-10-22c/RESULTADO.md`. Os 471 hashes conferem e a VM está desligada.
- **As instabilidades já existiam antes dos PRs:** na linha de base `8cb1e23`, o provedor passou 9/10 e a sonda 5/10.
- **Sonda:** causa confirmada. A correção com `shutdown()` passou 30/30 (branch `fix/teste-sonda-instavel`).
- **Provedor:** o timer de expiração atrasa até 1,26 s por causa do ambiente, e a margem entre o prazo de 14 s e a meta de 15 s é curta. A decisão vai para a issue, depois da demo.
- **Codex:** não há mais nada a fazer na VM antes do aceite de sexta.

### Depois da demo: organização do repositório (decidido em 21/10)

Começa na quarta, 28/10, depois da apresentação, dividido em duas PRs para a revisão continuar viável. Nada disso entra antes da entrega, para não colidir com o congelamento de segunda, 26/10: **até 27/10 nenhuma pasta ou arquivo é movido** (reconfirmado em 23/10). A ordem é a PR de documentação primeiro e a de estrutura do código depois.

**Situação em 23/10:** o `doc/`→`docs/` já está comitado e publicado em `feature/trail-fase1` (commits `988402b` e `1b7a7f1`), sem PR. As subpastas abaixo ainda não existem; hoje `docs/` tem `guias/`, `arquitetura/`, `demo/`, `design/` e `historico/`.

1. **PR de documentação e README**, de baixo risco:
   - `docs/` adota estas subpastas por assunto:

     | Subpasta | Conteúdo |
     |---|---|
     | `planejamento/` | `plano-demonstracao-2026-10-27.md`, `plano-sprints-pos-demo.md`, `plano-conclusao-2026-10-20.md` |
     | `processo/` | `gitflow.md`, `fluxo-de-trabalho-tcc.md`, `organizacao-repositorio-2026-10-23.md` |
     | `operacao/` | `instalacao.md`, `backup-restauracao.md`, `politica-imagens-e-portas.md`, `migracao-volume-postgresql.md` |
     | `arquitetura/` | `stack-de-tecnologia.md`, `estudo-de-caso.md` |
     | `tcc/` | `diario-bordo/`, `relatorio-orientador-2026-10-21.md`, `proposta-orientador.md` |
     | `demo/` | `roteiro-demonstracao.md`, `checklist-terca.md`, `demo.ps1`, `subir_demo.py`, rascunhos das issues |
     | `specs/` | a pasta `specs/` da raiz inteira (19 pastas, 52 arquivos), movida como está |

     `design/` (protótipo da Joyce) e `historico/` (registros datados) continuam como pastas próprias. O plano de sprints vai para `planejamento/`, junto do plano da demonstração.
   - **`specs/` → `docs/specs/`** (decidido em 23/10, seguindo o plano de 21/10). Só documentos são afetados: nenhum código, script ou CI referencia `specs/`. Em contrapartida, os 22 links relativos `../../` que saem das specs (16 arquivos; para `README.md`, `engenharia/`, `resultados/` etc.) ganham um nível, e os 10 links `../` entre specs continuam válidos. Fora de `specs/`, 13 arquivos citam o caminho: `README.md`, `DESIGN.md`, `PRODUCT.md`, `docs/README.md`, `docs/design/README.md`, `docs/design/prototipo-figcraft/MASTER.md`, `docs/guias/instalacao.md`, `docs/guias/politica-imagens-e-portas.md`, `docs/guias/organizacao-repositorio-2026-10-23.md`, `docs/historico/plano-conclusao-2026-10-20.md`, os dois planos e `engenharia/docs/05-seguranca-e-pendencias.md`.
   - **Arquivos soltos da raiz:** `revisao_pr_fix_base_issues.md` vai para `docs/historico/` e `resultados/` (3 evidências) para `docs/historico/resultados/`. Correções que precisam entrar no mesmo PR:
     - `scripts/executar_experimento_e6.py:101`: o padrão de saída passa a `docs/historico/resultados/experimento-e6-anonimizacao.md` (o CI já usa `--output test-results/e6.md`);
     - links `../../resultados/...` em `specs/009-010-instalacao-aceite/evidencias.md` e `specs/011-recuperacao-sprint/evidencias.md` passam a `../../historico/resultados/...`;
     - citações textuais de `resultados/experimento-e6-anonimizacao.md` nas specs `005-anonimizador-fail-closed/` (`spec.md`, `plan.md`, `tasks.md`, `evidencias.md`, `registro-issue.md`);
     - **não** mexer em `engenharia/sigma_eng/api.py`, `engenharia/README.md` e `engenharia/docs/*`: ali `resultados/` é o diretório de saída da auditoria em tempo de execução (`resultados/audit.jsonl`), outro assunto.
   - Os links quebram ao mover subpastas: atualizar `README.md`, `docs/README.md`, as specs, `scripts/install.sh` e as mensagens dos scripts, conferindo com `git grep -n "docs/"` e `git grep -n "specs/"` antes do merge.
   - README enxuto e apresentável:
     - selos de CI, Python, Node e PostgreSQL;
     - descrição curta e um print do painel, capturado no ensaio de sexta;
     - diagrama de fluxo em Mermaid (alvo → sonda → PostgreSQL → detector → SSE → painel);
     - funcionalidades, início rápido, resultados (488/488 e carga 5/5), limites e equipe.
   - As instruções longas de instalação saem do README e vão para `docs/operacao/`.
2. **PR de estrutura do código**, de risco maior:
   - `backend/` recebe `main.py`, `auth.py`, `config.py`, `sanitizer.py`, `api_errors.py`, `routers/`, `persistence/`, `migrations/` e `tests/`;
   - `sigma-frontend/` vira `frontend/`;
   - `deploy/` recebe o compose e o lock de imagens.
   - Só `git mv` e ajuste de caminhos: imports, uvicorn, alembic, CI e scripts. Nenhuma mudança de lógica.
   - Caminhos que mudam (levantamento de 23/10): `pytest.ini` (`testpaths`, `pythonpath`), `alembic.ini` (`script_location`), `.github/workflows/api-config.yml` (requirements, `sigma-frontend`, `scripts/`), `scripts/validate_panel.py` e `scripts/validate_infrastructure.py` (`sigma-frontend`, `docker-images.lock.json`), os `scripts/*.py` que importam `persistence`, os testes em `tests/` (imports de `main`, `routers` e `persistence`), `.gitignore`, o nome em `package.json` e o `docker-compose.yml`.
   - **Complemento do levantamento (23/10, só leitura, `git grep` no `75b1874`):** faltavam na lista acima `deploy/sigma-coleta.service` (`WorkingDirectory=/opt/sigma` e `uvicorn main:app`; passa a apontar para `backend`), `scripts/validate_compose_credentials.py`, `scripts/validate_installation.py` e `tests/test_infrastructure_policy.py` (citam `docker-compose.yml` e `docker-images.lock.json`), e `migrations/env.py` (importa `persistence`; anda junto com `backend/migrations/`). **`scripts/install.sh` também muda:** roda `pip install -r requirements.txt` (linha 10) e `python -m alembic upgrade head` (linha 12) a partir da raiz. `migrations/` vai para `backend/`, e o plano ainda não diz onde ficam `requirements.txt` e `alembic.ini`; a PR de estrutura precisa decidir isso e ajustar o script, e `scripts/validate_installation.py` deve cobrir a instalação limpa depois da mudança. Os outros scripts de shell (`update.sh`, `backup.sh`, `restore.sh`, `smoke.sh`) não citam `main:app`, `sigma-frontend` nem o lock de imagens, nem `requirements.txt` ou `alembic`. Também citam os caminhos antigos só em texto: `README.md`, `DESIGN.md`, `PRODUCT.md`, `engenharia/README.md` e `engenharia/docs/02-guia-de-implementacao.md`.
   - **`scripts/` fica na raiz** (decidido em 23/10): todos usam `ROOT = Path(__file__).resolve().parents[1]` como raiz do repositório para achar o compose, o lock de imagens e o frontend; dentro de `backend/` essa raiz mudaria. Em vez disso, os scripts que importam módulos do backend (`create_demo_users`, `executar_experimento_e6`, `manage_identity`, `retain_measurements`, `serve_browser_acceptance`, `validate_api_acceptance`, `validate_collection`, `validate_recovery`) passam a inserir `ROOT / "backend"` no `sys.path`; `recovery.py` e `validate_postgres.py` entram na conferência por usarem esses caminhos de forma indireta. `engenharia/` (pacote `sigma_eng`) continua onde está.
   - Depois disso: CI verde, regressão do Codex na VM e revisão do Iohan.
   - Integrar até sexta, 30/10, para não apertar a release de 03/11.
3. **Página do repositório no GitHub** (fora de PR, com confirmação): descrição "About" e tópicos, por exemplo `monitoramento`, `lgpd`, `fastapi`, `react`, `postgresql`, `sse`, `slo`, `rbac` e `tcc`.

### Quinta, 22/10: ajuste de data, CI do #43 e rodada 4 do Codex

- **Data nova:** entrega na terça, 27/10, às 18h. SHA congelado na segunda, 26/10, às 18h. Reorganização do repositório adiada para depois da entrega.
- **CI do #43 vermelho em `validate-compose`:** a tag `postgres:15.19-alpine3.24` foi republicada no Docker Hub. Digest atual `sha256:a8e0425…`; o lock fixa `sha256:f7d2335…`, que continua disponível no registry. O código não mudou. Decisão: manter o digest antigo. O commit `8661916` faz o validador checar só o digest (as tags são mutáveis). Enviado ao `fix/base-issues`; `validate-compose` voltou a passar. `test-config` e `test-postgres` estavam em andamento ao registrar.
- **Suíte sem banco no `fix/base-issues`:** 433 aprovados e 48 pulados. Cuidado de ambiente: o venv de `sigmati-develop` importa o `sigma_eng` do `develop`; ao testar um branch de PR, defina `PYTHONPATH` para o `engenharia\` do branch.
- **Quarto teste instável:** em uma segunda execução da suíte sem banco, `engenharia/tests/test_scheduler.py::test_shutdown_finishes_started_write_before_releasing_leadership` falhou (1 falha, 432 aprovados, 48 pulados), e a primeira execução tinha passado 433. Isolado, 30 execuções em cada lado: `develop` `8cb1e23` **28/30** e `fix/base-issues` `8661916` **29/30**. Já existia antes do #43 e não é regressão. A issue #45 cobre três testes (provedor, sonda e DNS); este quarto precisa entrar nela.
- **Iohan** empurrou `1db24a2` (UTF-8 inválido na auditoria e sanitização fora do event loop) e `3d32e79` (doc de code-review) no #43. Ainda não há Approve nem Request changes no GitHub.
- **Codex, rodada 4** (`validacao-vm/rodada-2026-10-22d`, candidato `ddd4840`):
  - Custo da verificação HMAC, gravação: 37,8 ms com 1 mil registros, 355,9 ms com 10 mil e 3.001,5 ms com 100 mil. Login total com 100 mil: 5.715,9 ms. O custo é linear e o limite de 50 ms da issue #46 não é atendido pelo desenho atual.
  - Ensaio do roteiro: bloqueado. O roteiro exige Windows e PowerShell, e a VM é Linux. Os dois itens ⚠ continuam sem confirmação.
- **Codex, rodada 5** (`rodada-2026-10-22e`): em andamento, no candidato local `0a6ce35` (develop + #43 com `8661916` + #44). Escopo: aceite completo, carga de 200 alvos × 5 e 10 execuções isoladas de cada teste instável.
- As issues rascunhadas já existem: #45 (testes instáveis) e #46 (custo da auditoria). A evidência da rodada 4 ainda precisa ser anexada à #46.

### Quinta, 22/10: noite

[Certo] Registro consolidado; os relatos anteriores de PR aberto, CI em andamento e rodada 5 em execução ficam superados por esta seção. Horários UTC−4.

- **Integração:** #43 em `dbc464d3712615c3a7cae7bada810b7b668db1ac`, 22h25; depois #44 em `75b1874ee5f83f55ab12837249a9c701fd67cef1`, 22h52. #44 tem base `develop`; CI dos heads dos dois aprovado. LGTM do Iohan no #44 às 21h53 é comentário, não review formal. Revisão adicional do Vinícius informada no pedido; não houve Approve formal.
- **Windows do Vinícius, PostgreSQL descartável, `75b1874`:** aceite HTTP todos PASS (`test-results/k10-acceptance.json` do worktree `sigmati-develop`); painel automatizado 4/4 (`panel-browser.xml`). Pytest 491 aprovados/1 pulado informado no pedido; log bruto não localizado, **não medido nesta conferência**.
- **Carga Windows:** 200 alvos lógicos/2 s, um serviço TCP loopback; 30 quedas, mediana 0,710 s, p95 0,806 s, máximo 0,819 s, 100% ≤5 s. Erros 0; `missed_capacity` 0, `missed_overlap` 187, timeouts 60, acumulados antes/depois e sem aumento na janela. Reinício preserva incidente único/sessão. Fonte: `sigmati-develop/test-results/collection-e2.json`. SSE mede chegada ao cliente; não 30 renderizações. Não comparar com VM `ddd4840` (p95 ≤0,410 s e atraso máximo 0,093396 s): hardware, SO e método distintos.
- **Ensaio 1 Windows pela API:** 403/200 por perfil; incidente em 0,7 s, MTTD 0,45 s, MTTA/MTTR 29 s; burn rate `at_risk`, 12 min, `page`; solicitante recebe 409 e revisor aprova, auditoria íntegra. Anonimização e formato `{ "incidentes": [...] }` confirmados, helpers corrigidos em `demo.ps1`. Fonte: Achados do Ensaio 1 no roteiro e relato do Vinícius; não houve nova medição aqui. Painel manual permanece pendente.
- **Cuidados:** subir o serviço antes de resolver o incidente; aprovação expira em 15 min (subir dados no máximo 10 min antes da etapa 5 ou criar pedido novo na hora); acentos no PowerShell 5.1 são problema de exibição.
- **VM:** rodada 4 mediu HMAC (~3 s para 100 mil registros; limite proposto de 50 ms não atendido). Rodadas 5 e 6 bloqueadas **antes de testar**: objeto `0a6ce35` ausente na VM e bundle vazio recusado, respectivamente. Candidato antigo superado; resultados dessas rodadas: não medidos.
- **Rodada 7:** pedida em `validacao-vm/rodada-2026-10-22g/PEDIDO-CODEX.md`, candidato `75b1874`, até 23/10 às 10h; sem RESULTADO disponível na conferência. Bundle SHA-256 `0e1129ccb8d12a10893d10360665dcdf9c5a6f69ea8164889863695fcafa87ea`.
- **#47:** aberto, só teste da sonda, 26/30 → 30/30 na VM rodada 3; revisão do Iohan pendente. CI atual **4 aprovados + validate-compose reprovado**, run [39894956404](https://github.com/Solution-Explores/SigmaTI/actions/runs/39894956404); não publicar 5/5 atual.
- **#45/#46:** comentários de 22/10 existem. A #45 registra o quarto teste 28/30 (`8cb1e23`) e 29/30 (`8661916`), sem causa isolada; #46 registra HMAC da rodada 4. A triagem “27/10 após demo às 18h” conflita com a nova apresentação; Trello propõe 28/10, sem alterar critérios GitHub.
- **Agenda:** 23/10 aceite VM/painel manual/#47; 24/10 à tarde roteiro do Iohan; 25/10 correções e segunda execução se necessária, #25 opcional; 26/10 ensaio 2, gravação, slides, freeze às 18h e bateria completa do Codex depois, smoke do Iohan após 22h; 27/10 manhã ensaio/smoke, 16h preparar e desligar `sigma-restore-25`, 18h demo; 28/10 organização. Joyce/DS mantêm datas e gates, sem ampliar escopo até terça.

### Sexta, 23/10: rodada 7 retomada e painel manual

Horários UTC−4. Feito por Claude, com autorização do Vinícius para usar a VM e o Docker.

- **Rodada 7 retomada na VM** (`validacao-vm/rodada-2026-10-23a/`, resultado em `RESULTADO.md`, 213 hashes em `SHA256SUMS.txt`). A rodada `22g` tinha parado em 22/10 às 23:45 e a VM estava desligada. Foram aproveitados os resultados já medidos nela (pytest 491 aprovados e 1 falha de ambiente, API 20/20, painel 4/4, infraestrutura PASS) e rodado o que faltava no mesmo candidato `75b1874`:
  - e2e do painel pelo pytest, depois do `npm ci`: aprovado, o que explica a única falha do pytest completo (a suíte completa não foi repetida; **não se declara 492/492**);
  - cinco cargas de 200 alvos: p95 queda→SSE de 0,395 a 0,496 s, máximo de 0,545 s, atraso máximo do calendário de 0,056 a 0,283 s, 0 erros, 0 timeouts, `missed_capacity` 0;
  - 80 execuções isoladas: 79 aprovadas. A falha foi `test_real_budget_cancels_slow_provider_within_15_seconds` no worktree B, com 15,0248 s contra o limite de 15 s. Entra na #45 (margem do timer de 14 s).
- **#47:** o head agora é `0b372cb` e as cinco verificações estão aprovadas, `validate-compose` incluído. Isso substitui o "4 aprovados + 1 reprovado" de 22/10. Falta a revisão do Iohan (sem Approve nem Request changes).
- **#6 e #8** seguem abertas; o aceite é registrado, mas as issues só fecham com todos os critérios.
- **Painel manual** (navegador embutido, `develop@75b1874`, banco `sigma-db` do Docker Desktop): etapas 2 a 6 passaram, com os achados em [roteiro-demonstracao.md](roteiro-demonstracao.md). Principais: incidente em 0,7 s sem recarregar, MTTA 17,07 s e MTTR 27,68 s no painel, MTTD 0,67 s pela API, auditoria íntegra e anonimização na tela. Dois cuidados novos: subir o serviço de novo abre um incidente extra de latência, e recarregar a página encerra a sessão.
- A VM `sigma-restore-25` foi desligada depois da rodada. O Docker Desktop ficou ligado; a demo foi encerrada e o schema do ensaio foi removido (0 schemas `sigma_panel_*` restantes).

### Segunda, 26/10: #47 integrado e aceite local no novo SHA

Horários UTC−4. Feito por Claude, com autorização do Vinícius para integrar o #47.

- **Integração:** #47 entrou na `develop` por merge commit, `7851da64348dc1437e1258282034b5dca61007fb`, depois do parecer favorável do Iohan (comentário, sem Approve formal). O CI desse SHA terminou com sucesso nos dois fluxos (`CI Infrastructure Validation` e `API and engineering regression`).
- **Windows do Vinícius, PostgreSQL do Docker Desktop, `7851da6`** (worktree `sigmati-develop`):
  - pytest completo: **491 aprovados e 1 pulado** em 411,98 s;
  - aceite HTTP (`validate_api_acceptance.py`): todos PASS. A primeira execução falhou só porque sobrou `k10-acceptance.users.json` de 22/10 (o script abre o arquivo com `x`); os resíduos foram movidos para `test-results/antigos-22-10/` e a repetição passou;
  - painel (`validate_panel.py`): 4 de 4 aprovados;
  - coleta (`validate_collection.py`): 30 quedas, mediana 0,734 s, p95 0,854 s, máximo 1,065 s, 100 % em até 5 s; 200 alvos lógicos, intervalo de 2 s, 0 erros, `missed_capacity` 0, `missed_overlap` 199 e 63 timeouts (acumulados, como em 22/10); reinício preserva incidente único e sessão. Escopo: loopback, um serviço TCP, sem painel nem rede hospitalar.
  - Não comparar com a VM: hardware, SO e método diferentes.
- **VM:** bundle `validacao-vm/rodada-2026-10-26a/candidato-7851da6.bundle` (SHA-256 `21541500f5e64257c7d9ff6022cf762d7ee161665073a21ca0edda01ded9f602`) e `PEDIDO-CODEX.md` prontos para a rodada 8, a entregar ao Codex depois do congelamento das 18h. Não medido: o resultado dessa rodada.
- **SHA congelado:** `7851da64348dc1437e1258282034b5dca61007fb`, por decisão do Vinícius em 26/10, de manhã (o plano previa 18h). Registrado em [demo/checklist-terca.md](demo/checklist-terca.md). A bateria completa do Codex (rodada 8) fica para depois das 18h; o Iohan confere o SHA e roda o smoke depois das 22h.
- **Ensaio 2** (26/10, 9h14–9h20, navegador embutido, `7851da6`): etapas 2 a 6 passaram sem ajuste no texto; MTTD 0,26 s, MTTA 15,06 s, MTTR 29,03 s; auditoria íntegra (13 registros); anonimização na tela. O incidente extra de latência depois do retorno do serviço apareceu de novo (segunda vez). Detalhes em [roteiro-demonstracao.md](roteiro-demonstracao.md), "Achados do Ensaio 2". Ficou sem conferir a janela anônima de um navegador real (o ensaio usou abas do embutido, uma sessão por aba).
- **Gravação de contingência:** feita em 26/10 com o Playwright do frontend, no `7851da6` (`validacao-vm/contingencia/contingencia-7851da6.webm`, 1 min 58 s, fora do repositório). O script é `docs/demo/gravar_contingencia.mjs`. É um vídeo condensado, com legendas, e não um ensaio falado de 15 minutos. Duas tentativas anteriores foram descartadas: uma por erro do script e outra porque os dados tinham resíduo da primeira.
- **Slides:** o slide "Resultados" e a capa (data 27/10) foram atualizados com os números do `7851da6` (Windows) e a ressalva de que os da VM são do `75b1874`; link em https://claude.ai/artifact/38N6oK7SdYLf5mxAM24ZZh.
- **Ferramenta:** ponte MCP para o Codex em `~/.claude/mcp-servers/codex-bridge/` (fora do repositório); só leitura por padrão.

### Pendente
- [x] Ensaio de API Windows de 22/10 confirmou os itens ⚠; painel manual feito em 23/10 (ver "Sexta, 23/10").
- [x] CI do #43 aprovado e integração feita; Approve formal não ocorreu e não é declarado.
- [x] Base #44 mudada para `develop`, CI aprovado e integração em 22/10 após #43.
- [x] PR #47 aberto e evidência da rodada 4 publicada na #46.
- [x] 23/10: rodada 7 retomada na VM e concluída (ver "Sexta, 23/10"); critérios #6/#8 seguem abertos.
- [x] 23/10: painel manual feito; CI do #47 voltou a passar (`0b372cb`).
- [x] 25/10, 18h21 (commit `e82d13b` no branch `pr-47`) e 22h41 (comentário no PR): revisão do #47 pelo Iohan, parecer favorável (LGTM) como comentário; não há Approve formal no GitHub. O arquivo `revisao_pr_47_teste_sonda_instavel.md` está só no branch `pr-47` e entra na PR de documentação de 28/10. Obs.: o commit não é da revisão do #43/#44 (essas foram em 21 e 22/10).
- [x] 26/10: #47 integrado na `develop` (merge `7851da64348dc1437e1258282034b5dca61007fb`), com a autorização do Vinícius. Candidato ao congelamento das 18h.
- [ ] 24/10 e 25/10: o relatório da execução independente do roteiro pelo Iohan não está no repositório nem nas issues. Cobrar com ele.
- [x] 23/10: resultado da rodada 7 retomada anexado à [#45](https://github.com/Solution-Explores/SigmaTI/issues/45#issuecomment-6377082969), à [#6](https://github.com/Solution-Explores/SigmaTI/issues/6#issuecomment-6377083347) e à [#8](https://github.com/Solution-Explores/SigmaTI/issues/8#issuecomment-6377083680). Os comentários de #6 e #8 foram corrigidos para separar o que foi medido em 22/10 do que foi medido em 23/10.
- [ ] 24/10 à tarde: roteiro independente do Iohan; 25/10 correções, segunda execução se necessária, #25 opcional.
- [x] 26/10: ensaio 2, gravação de contingência e slides (ver "Segunda, 26/10"); SHA congelado em `7851da6`.
- [ ] 26/10, depois das 18h: bateria completa do Codex na VM (`validacao-vm/rodada-2026-10-26a/PEDIDO-CODEX.md`) e atualização dos slides com o resultado, se divergir.
- [ ] 26/10, depois das 22h: o Iohan confere o SHA `7851da6` e roda o smoke.
- [ ] 27/10: ensaio/smoke de manhã; desligar VM e preparar ambiente às 16h; demo às 18h.
- [ ] Trello/GitHub: publicação e conferência da atualização em `validacao-vm/rodada-2026-10-22h/RESULTADO.md`.

Herdado para as sprints (ver [plano-sprints-pos-demo.md](plano-sprints-pos-demo.md)):

- [ ] 27/10 à noite ou 28/10: registrar o retorno do orientador e converter em issues da S1.
- [ ] 28/10: abrir a PR de documentação (`doc/` → `docs/`) e a PR de estrutura; integrar a estrutura até 30/10.
- [ ] S2: #45 passa a cobrir também o 4º teste instável (`test_scheduler`, 28/30 na `develop`) e a margem do timer de IA (14 s contra 15 s).
- [x] S2: o `validate-compose` do #47 passou em 23/10 (head `0b372cb`, cinco verificações aprovadas); o #47 só conta como concluído depois da revisão do Iohan e da integração.
- [ ] S2 (stretch): painel exibir MTTD e burn rate, hoje só pela API.
- [ ] Confirmar com o orientador: #13 e #25 em 10/11, data da banca e licença do repositório.

## Referências

- [Plano de sprints pós-demo](plano-sprints-pos-demo.md)
- [Plano de conclusão de 20/10](historico/plano-conclusao-2026-10-20.md)
- [Git Flow do SigmaTI](guias/gitflow.md)
- [Fluxo de trabalho do TCC](guias/fluxo-de-trabalho-tcc.md)
- [Quadro SigmaTI](https://trello.com/b/vswV1j1T/sigmati)
