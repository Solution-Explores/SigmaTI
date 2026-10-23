# Git Flow

Modelo de branches do SigmaTI, adotado em 19/10/2026. A `main` é a branch padrão. A antiga `dev` virou `develop`, com os commits preservados.

| Branch | Origem | Destino por PR | Uso |
|---|---|---|---|
| `main` | | | Versões aprovadas, marcadas com tags `vX.Y.Z`. |
| `develop` | `main` | `release/*` | Integração do desenvolvimento. |
| `feature/nome` | `develop` | `develop` | Uma funcionalidade ou issue. |
| `fix/nome` | `develop` | `develop` | Correção durante o desenvolvimento. |
| `release/X.Y.Z` | `develop` | `main`, depois `develop` | Congelamento, correções e aceite de uma versão. |
| `hotfix/nome` | `main` | `main`, depois `develop` | Correção urgente da versão entregue. |

Use nomes curtos, em minúsculas e separados por hífen, como `feature/persistencia` e `fix/login`. Cite o número da issue no PR e nos commits.

## Desenvolver

```bash
git switch develop
git pull --ff-only origin develop
git switch -c feature/nome
# implementar, testar e registrar evidências
git push -u origin feature/nome
```

Abra o PR para `develop`. Exija revisão e CI aprovado antes de integrar. Não desenvolva direto nas branches permanentes.

## Release e hotfix

**Release.** Quando houver uma versão concreta, crie `release/X.Y.Z` a partir da `develop` aprovada. Congele funcionalidades e registre o aceite. Depois da revisão, integre à `main`, crie a tag `vX.Y.Z` no commit entregue e leve as correções de volta à `develop` por PR.

**Hotfix.** Para urgências, crie `hotfix/nome` a partir da `main`. Depois de revisar e testar, integre à `main`, publique uma versão de correção e leve a alteração à `develop`. Se houver uma release em preparação, leve também a ela. Nenhuma correção pode ficar só na produção.

As branches `release/*` e `hotfix/*` são temporárias e só existem enquanto há trabalho para elas. Adotar o fluxo não publica versão nem aprova merge. As proteções de branch precisam ser conferidas nas configurações do GitHub, porque esta documentação não as impõe.

## Nomes antigos

| Antes | Agora |
|---|---|
| `dev` | `develop` |
| `feat/9-pacote-sigma-eng` | `feature/pacote` |
| `feat/engenharia-vigilark` | `feature/engenharia` |
| `fix/sprint-aceite-autenticacao-privacidade` | `fix/aceite` |
| `fix/revisao-k01-volumes-instalacao` | `fix/docker` |

As branches antigas já integradas foram renomeadas para manter a referência histórica. Nenhum commit foi apagado. O PR #33 foi fechado pela renomeação da origem, e o [PR #34](https://github.com/Solution-Explores/SigmaTI/pull/34) (`feature/pacote` para `develop`) o continua.

Em outros clones, guarde as mudanças locais e atualize os nomes:

```bash
git branch -m dev develop
git fetch --prune origin
git branch --set-upstream-to=origin/develop develop
```

Para a sua branch de trabalho, repita os passos com os nomes da tabela. Relatórios antigos continuam usando o nome da época.
