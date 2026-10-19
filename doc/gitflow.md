# Git Flow do SigmaTI

Adotado em 19/10/2026. `main` permanece como branch padrão. A antiga `dev`
passou a se chamar `develop`; os commits foram preservados.

| Branch | Origem | Destino por PR | Uso |
|---|---|---|---|
| `main` | — | — | Versões aprovadas, identificadas por tags `vX.Y.Z`. |
| `develop` | `main` | `release/*` | Integração do desenvolvimento. |
| `feature/nome` | `develop` | `develop` | Uma funcionalidade ou issue. |
| `fix/nome` | `develop` | `develop` | Correções durante o desenvolvimento. |
| `release/X.Y.Z` | `develop` | `main` e depois `develop` | Congelamento, correções e aceite de uma versão. |
| `hotfix/nome` | `main` | `main` e depois `develop` | Correção urgente da versão entregue. |

Use nomes curtos, minúsculos e separados por hífen, como `feature/persistencia`
e `fix/login`. Relacione o número da issue no PR e nos commits. `fix/*` é a
convenção adicional para correções que não são urgências da versão entregue.

## Desenvolvimento

```powershell
git switch develop
git pull --ff-only origin develop
git switch -c feature/nome
# implementar, testar e registrar evidências
git push -u origin feature/nome
```

Abra PR para `develop`. Exija revisão e CI aprovado antes da integração.
Não faça desenvolvimento diretamente nas branches permanentes. A aprovação
excepcional do PR #32 continua limitada àquela entrega.

## Release e hotfix

Crie `release/X.Y.Z` a partir da `develop` aprovada quando houver uma versão
concreta para preparar. Congele funcionalidades e registre o aceite. Depois
da revisão, integre à `main`, crie a tag `vX.Y.Z` no commit entregue e integre
as correções da release de volta à `develop` por PR.

Para urgências, crie `hotfix/nome` a partir da `main`. Depois de revisar e testar,
integre à `main`, publique uma nova versão de correção e leve a alteração à
`develop`; se existir uma release em preparação, leve a correção também a ela.
Não deixe correções exclusivas da produção fora da linha de desenvolvimento.

Branches `release/*` e `hotfix/*` são temporárias: serão criadas quando houver
trabalho correspondente. A adoção do fluxo não publica uma versão nem aprova merges.
Proteções obrigatórias no servidor devem ser conferidas nas configurações do
GitHub; esta documentação e a configuração local não as impõem.

## Migração dos nomes

| Nome anterior | Nome atual |
|---|---|
| `dev` | `develop` |
| `feat/9-pacote-sigma-eng` | `feature/pacote` |
| `feat/engenharia-vigilark` | `feature/engenharia` |
| `fix/sprint-aceite-autenticacao-privacidade` | `fix/aceite` |
| `fix/revisao-k01-volumes-instalacao` | `fix/docker` |

As branches antigas já integradas foram renomeadas para preservar a referência
histórica; não representam trabalho novo. Não foram apagados commits.
O PR #33 foi fechado automaticamente pela renomeação da origem. Sua continuação
é o [PR #34](https://github.com/Solution-Explores/SigmaTI/pull/34), de
`feature/pacote` para `develop`, preservando os commits anteriores.

Em outros clones, preserve mudanças locais e atualize os nomes existentes:

```powershell
git branch -m dev develop
git fetch --prune origin
git branch --set-upstream-to=origin/develop develop
```

Para a branch de trabalho, use os mesmos passos substituindo os nomes conforme
a tabela. Referências históricas em relatórios continuam descrevendo o nome
usado na execução original.
