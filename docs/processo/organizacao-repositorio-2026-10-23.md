# Organização do repositório pelo Git Flow

Registro do diagnóstico e da limpeza das branches, em 23/10/2026. **Status: limpeza executada em 23/10/2026.** Nenhum PR foi integrado, não houve `push --force` e a `main` não foi alterada. O modelo de referência é o [Git Flow](gitflow.md).

## Objetivo e modelo

- `main`: versões aprovadas. Só recebe `release/1.0.0` e a tag `v1.0.0`, depois da demonstração de 27/10 e do aceite de 31/10 e 01/11. Não é tocada nesta organização.
- `develop`: onde o desenvolvimento acontece. Toda `feature/*` e `fix/*` parte dela e volta por PR revisado.
- `dev`: descontinuada. Foi renomeada para `develop` em 19/10; a cópia que restou no GitHub é uma linha antiga.
- Todo o resto são branches de espera (PRs abertos ou trabalho em andamento) ou resíduos de trabalhos já integrados.

## Diagnóstico de 23/10/2026

Base de comparação: `origin/develop` em `75b1874` (PRs #43 e #44 integrados) e `origin/main` em `75118ad`, 48 commits atrás da `develop` e sem commit exclusivo. Referências atualizadas com `git fetch origin --prune`.

| Grupo | Branches | Estado |
|---|---|---|
| Integradas | `codex/estado-operacional`, `codex/persistencia`, `codex/sondagem-ip-validado`, `codex/fix-k08-porta-fechada` (só local), `feature/8-coleta-sse`, `feature/15-painel-operacional`, `feature/25-backup-restauracao`, `feature/pacote`, `fix/base-issues`, `fix/coleta` | Totalmente contidas em `origin/develop`. Podáveis. |
| PRs abertos | `fix/teste-sonda-instavel` (#47), `feature/conferencia-issues-base` (#42), `feature/25-roteiro-validacao-vm` (#41) | 10 commits atrás da `develop`. #41 e #42 criam arquivos em `doc/`. |
| Em andamento | `feature/trail-fase1` | 2 commits à frente e 10 atrás. A migração `doc/`→`docs/` está no working tree, sem commit. |
| Design system | `feature/tarefas-joyce` (4 commits), `feature/design-system-joyce` (3 commits) | A primeira contém os commits da segunda e foi publicada em 23/10 (`963efd5`). |
| Redundantes | `candidato/rodada-5` (só local), `pr-44` | `candidato/rodada-5` tem árvore idêntica à da `develop`. `pr-44` é um documento de revisão de outro autor. |
| Divergente | `dev` (remota, `feef975`) | 41 commits atrás da `develop` e 1 exclusivo, de iohanjheremy: configuração do Trail e do Gemini. |

Achados da revisão (`/code-review`, nível high):

1. A migração `doc/`→`docs/` vai conflitar com #41 e #42, que ainda criam arquivos em `doc/` e editam o README.
2. `wait()` do mock do frontend ignorava um `signal` já abortado e executava o handler.
3. Dois commits existiam só neste computador (`963efd5` e `0a6ce35`). O primeiro já foi publicado.
4. `.worktrees/` não estava no `.gitignore`.
5. A configuração do Trail em `origin/dev` manda consultar `.trail/cache/`, mas ignora `/graft/`.
6. O registro da fase 1 do Trail estava desatualizado.
7. O mock aceita qualquer senha e talvez não seja removido do build de produção.
8. `candidato/rodada-5` é um merge redundante.
9. Branches integradas e obsoletas acumuladas.

## Decisões do responsável

- Apagar as branches já integradas, no GitHub e no computador.
- Guardar a `dev` na tag `archive/dev-feef975` e apagá-la.
- Atualizar #41, #42, #47 e `feature/trail-fase1` com a `develop`, sem integrar nenhum PR.
- Manter somente `feature/tarefas-joyce` no design system.
- Sem `push --force`. Nenhum commit direto em `develop` ou `main`.

## Feito antes da limpeza

- `feature/tarefas-joyce` publicada no GitHub, com push normal.
- `.worktrees/` incluído no `.gitignore`.
- Seção de atualização em [Trail, fase 1](../historico/trail-fase1.md).
- Correção do `wait()` do mock na worktree `tarefas-joyce`.

## Resultado da execução

- Correção do mock comitada e publicada em `feature/tarefas-joyce` (`afac415`).
- Migração `doc/`→`docs/` comitada em `feature/trail-fase1`, com o merge de `origin/develop`. Os três documentos que a `develop` criou em `doc/` (coleta em lotes, correção das issues base e revisão dos achados) foram movidos para `docs/historico/`.
- `origin/develop` foi mesclada em `fix/teste-sonda-instavel` (#47), `feature/conferencia-issues-base` (#42) e `feature/25-roteiro-validacao-vm` (#41), sem conflito. Os 10 testes de `test_stats_probe.py` passam no #47. Os três PRs seguem abertos e mesclável.
- `dev` arquivada na tag `archive/dev-feef975` e apagada, no GitHub e no computador.
- Branches integradas apagadas. SHAs finais, para recuperar com `git branch <nome> <sha>`:

| Branch | SHA |
|---|---|
| `codex/estado-operacional` | `86375d93a6c925f470b4ab563e377ca09356e09e` |
| `codex/persistencia` | `31471daff15db88e94f9624177e1bc441be9a632` |
| `codex/sondagem-ip-validado` | `d42edac681905096cefc6fa56a276078d0cee892` |
| `codex/fix-k08-porta-fechada` (só local) | `7975c0010dc0187d0ce158d3fdb2f6be9e47b348` |
| `feature/8-coleta-sse` | `047c43db3f4b6f2d91c4a3ffb5ebbf2b691c5b3b` |
| `feature/15-painel-operacional` | `13636785aabd15e4faf994f1307477c394254f73` |
| `feature/25-backup-restauracao` | `54646644be107724e60b11a5c6e7ca03b7cb61c4` |
| `feature/pacote` | `7f3b5d12d46d00701c34da2a1964c73075fce3e7` |
| `fix/base-issues` | `8661916b10f6147422a9a4a507e561947bc95f00` |
| `fix/coleta` | `ddd48400fffab01fc49707e303eb36419e9d6f37` |
| `candidato/rodada-5` (só local, árvore igual à da `develop`) | `0a6ce35` |
| `feature/design-system-joyce` | `22adfdf` (contida em `feature/tarefas-joyce`) |

- Os três worktrees de `.worktrees/` foram removidos. Ficam o checkout principal e `sigmati-develop`.
- `pr-44` (documento de outro autor) foi mantida.

## Procedimento seguido

Executado na ordem abaixo. Antes de cada remoção, confirme que a branch está contida na `develop`:

```bash
git fetch origin --prune
git merge-base --is-ancestor origin/<branch> origin/develop && echo ok
```

1. **Salvar o trabalho solto.** Na worktree `tarefas-joyce`, commitar a correção do mock e fazer `git push`.
2. **Commitar a migração `doc/`→`docs/`** em `feature/trail-fase1`. Incluir `docs/`, `.gitignore`, `.gitattributes` e os arquivos rastreados alterados ou removidos. Não incluir `.claude/` nem `skills-lock.json`. Em seguida `git merge origin/develop` (sem rebase), resolver conflitos e `git push`.
3. **Atualizar os PRs abertos.** Para `fix/teste-sonda-instavel`, `feature/conferencia-issues-base` e `feature/25-roteiro-validacao-vm`: `git switch <branch>`, `git merge origin/develop`, `git push`. No #47, rodar `engenharia/tests/test_stats_probe.py`. Os PRs #41 e #42 mantêm os arquivos em `doc/` até a trail-fase1 entrar na `develop`; depois, movê-los para `docs/`.
4. **Arquivar e apagar a `dev`.**

   ```bash
   git tag archive/dev-feef975 origin/dev
   git push origin archive/dev-feef975
   git push origin --delete dev
   git branch -D dev
   ```

   Antes do `-D`, confirmar que os 4 commits locais já estão na `develop` (`git branch --contains <sha>`).
5. **Podar as integradas.** Remotas: `codex/estado-operacional`, `codex/persistencia`, `codex/sondagem-ip-validado`, `feature/8-coleta-sse`, `feature/15-painel-operacional`, `feature/25-backup-restauracao`, `feature/pacote`, `fix/base-issues`, `fix/coleta`, com `git push origin --delete <branch>`. Locais: as mesmas, mais `codex/fix-k08-porta-fechada`, com `git branch -d`. `candidato/rodada-5` só sai depois de `git diff origin/develop candidato/rodada-5` vazio, com `-D`. Confirmar antes que nenhum PR aberto usa essas branches como base (hoje todos usam `develop`).
6. **Remover os worktrees** de `candidato-rodada-5`, `fix-base-issues` e `tarefas-joyce` com `git worktree remove` (a última só depois do passo 1) e apagar a pasta `.worktrees/`.
7. **Design system.** Conferir que os 3 commits de `origin/feature/design-system-joyce` são ancestrais de `feature/tarefas-joyce` e então `git push origin --delete feature/design-system-joyce`.
8. **Não mexer** em `main`, `develop`, `pr-44` (de outro autor) nem nas tags `archive/*`.

## Estado final

Branches vivas: `main`, `develop`, `feature/trail-fase1`, `feature/tarefas-joyce`, `fix/teste-sonda-instavel`, `feature/conferencia-issues-base`, `feature/25-roteiro-validacao-vm` e a `pr-44`, que fica intocada. Tag nova: `archive/dev-feef975`. Localmente, só o checkout principal e a pasta `sigmati-develop`.

## Próxima etapa: pastas e arquivos soltos (depois de 27/10)

O Git Flow não trata de pastas. O plano de reorganização está em `docs/plano-demonstracao-2026-10-27.md` (seção "Depois da demo") e no Sprint 1 de `docs/plano-sprints-pos-demo.md`. Decidido em 23/10: **nada é movido antes da demo de 27/10**; em 28/10 vêm primeiro o PR de documentação e depois o PR de estrutura do código.

Layout adotado para `docs/` (origem hoje → destino):

| Destino | Origem |
|---|---|
| `docs/planejamento/` | `plano-demonstracao-2026-10-27.md`, `plano-sprints-pos-demo.md`, `historico/plano-conclusao-2026-10-20.md` |
| `docs/processo/` | `guias/gitflow.md`, `guias/fluxo-de-trabalho-tcc.md`, `guias/organizacao-repositorio-2026-10-23.md` |
| `docs/operacao/` | `guias/instalacao.md`, `guias/backup-restauracao.md`, `guias/politica-imagens-e-portas.md`, `guias/migracao-volume-postgresql.md` |
| `docs/arquitetura/` | já está no lugar |
| `docs/tcc/` | `historico/diario-bordo/`, `historico/relatorio-orientador-2026-10-21.md`, `demo/proposta-orientador.md` |
| `docs/demo/` | `roteiro-demonstracao.md` (hoje em `docs/`); o restante já está |
| `docs/historico/` | fica, e recebe `revisao_pr_fix_base_issues.md` e `resultados/` da raiz (este como `docs/historico/resultados/`, com o padrão do script do E6 e os links das specs ajustados) |
| `docs/design/` | fica (protótipo da Joyce) |
| `docs/specs/` | `specs/` da raiz inteira (19 pastas, 52 arquivos); só documentos são afetados, nenhum código ou CI referencia `specs/` |

No PR de estrutura, o código vai para `backend/`, `sigma-frontend/` vira `frontend/` e o compose e o lock de imagens vão para `deploy/`. `scripts/` e `engenharia/` ficam onde estão; os scripts passam a incluir `backend/` no `sys.path`. A lista de caminhos que mudam está no plano de demonstração.

## Qual branch baixar em outro computador

No estágio, parta sempre da `develop`. A `main` guarda só versões entregues e não serve para desenvolver.

Primeira vez:

```bash
git clone https://github.com/Solution-Explores/SigmaTI.git
```

Computador que já tem o clone:

```bash
git fetch --prune origin
git switch develop
git pull --ff-only origin develop
```

Para continuar um trabalho em andamento:

```bash
git switch -c <branch> origin/<branch>
```

| Trabalho | Branch | PR |
|---|---|---|
| Novo trabalho | `develop`, depois `feature/nome` ou `fix/nome` | |
| Reorganização da documentação, Trail e planos da demonstração | `feature/trail-fase1` | sem PR |
| Design system e tarefas da Joyce | `feature/tarefas-joyce` | sem PR |
| Estabilizar o teste da sonda | `fix/teste-sonda-instavel` | #47 |
| Conferência das issues 6, 7, 8 e 14 | `feature/conferencia-issues-base` | #42 |
| Validação do #25 em máquina virtual | `feature/25-roteiro-validacao-vm` | #41 |
| Versão `v1.0.0` (depois da demonstração) | `release/1.0.0`, criada a partir da `develop` | |

Antes de sair de um computador, publique: `git push`. Branch que só existe localmente não aparece no outro.

## Riscos e recuperação

- Uma branch apagada continua alcançável pelo commit. Para recuperar: `git branch <nome> <sha>`. Registrar os SHAs finais ao executar o passo 5.
- O merge da `develop` nos PRs pode conflitar em `README.md` e `specs/`. Resolver preservando as duas mudanças e parar se o conteúdo for ambíguo.
- `*.md text eol=lf` no `.gitattributes` pode renormalizar finais de linha. Conferir `git diff --stat` antes de commitar.
- Aproveitar a configuração do Trail da `dev` exige antes reconciliar `.trail/cache/` com `/graft/`, por PR pequeno. O commit fica preservado na tag.

## Verificação

```bash
git fetch --prune origin
git branch -a -vv
git tag -l 'archive/*'
git worktree list
gh pr list --state open
gh api repos/Solution-Explores/SigmaTI/branches --jq '.[].name'
```

- A lista de branches remotas confere com a seção "Estado esperado ao final".
- `git rev-list --left-right --count origin/develop...<branch>` mostra `0` à esquerda para cada branch viva.
- Os PRs #41, #42 e #47 seguem abertos e sem conflito.
- Um clone limpo, em pasta temporária, mostra as mesmas branches com `git branch -r`.
