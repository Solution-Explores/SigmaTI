# Trail-Code — fase 1 e conferência do repositório

Conferência em 20/10/2026 (UTC−4), após atualizar as referências com
`git fetch origin --prune`. Este registro não inicia a fase 2.

## Instalação neste computador

- Pacote oficial validado no registro npm: `@trailhq/trail-code@0.23.0`.
- Origem declarada: <https://github.com/trailhq/Trail-Code>.
- Requisito do pacote: Node >=20. Ambiente usado: Node 24.19.0, npm 12.0.2,
  Windows.
- CLI global instalada; `trail --version` retornou `0.23.0` e as ajudas de
  `trail` e `trail init` responderam normalmente.
- Telemetria desativada com `trail telemetry disable`. Conferência sem
  `DO_NOT_TRACK` confirmou a preferência persistente e zero eventos na fila.
- Não foram executados `trail init`, `trail build`, importação de históricos,
  conexão com workspace ou geração de resumos por LLM.

Comandos para reproduzir a instalação em outro computador (PowerShell):

```powershell
$env:DO_NOT_TRACK = '1'
$env:TRAIL_NO_FETCH = '1'
npm install --global @trailhq/trail-code@0.23.0 --no-audit --no-fund
trail telemetry disable
trail --version
trail --help
```

Essas variáveis valem apenas para o processo atual. A preferência salva por
`trail telemetry disable` persiste. A proteção contra importação de históricos
precisará ser aplicada também à configuração dos agentes na fase correspondente.

As tentativas de download pelo npm encontraram falhas TLS. A instalação terminou
após baixar a dependência `openai@7.39.0` pelo `curl.exe` do Windows, adicioná-la
ao cache npm e instalar offline, mantendo verificação de integridade. Nenhuma
configuração global de TLS ou de certificados foi relaxada.

O npm bloqueou scripts de instalação do pacote e de dependências tree-sitter.
A CLI passou nos testes acima; os parsers e a geração do grafo ainda precisam
ser validados na fase 2. Não foi liberada uma política global de scripts npm.

## Comparativo entre GitHub e computador

| Referência | Estado confirmado |
|---|---|
| `main` em `75118ad` | Linha de versões; `develop` possui 38 commits adicionais, sem commits exclusivos de `main` nessa comparação. |
| `develop` em `8cb1e23` | Igual à branch local `develop`; integra os PRs #34–#40: pacote, identidades, estado operacional, sondagem, coleta/SSE, painel e backup/restauração. |
| `feature/conferencia-issues-base` em `9b7556c` | Era o checkout local inicial, igual ao remoto; PR #42 aberto, com diagnóstico documental. |
| `feature/25-roteiro-validacao-vm` em `574acda` | Local e remoto iguais; PR #41 aberto. Planejamento não comprova aceite em outra máquina. |
| `fix/base-issues` em `a97fe1b` | Já publicado no GitHub; PR #43 aberto para `develop`, com correção de auditoria e diagnóstico da coleta. |
| `fix/coleta` em `4350632` | Já publicado no GitHub; PR #44 aberto sobre `fix/base-issues`, com persistência em lotes e espera por vagas do scheduler. |
| `dev` remoto em `feef975` | Contém configuração do Trail enviada por outro autor; diverge de `develop`: 31 commits exclusivos de `develop` e um exclusivo de `dev`. |
| `dev` local em `001d304` | Referência antiga: quatro commits à frente e um atrás de `origin/dev`; esses quatro commits já estão em `origin/develop`. Não há trabalho exclusivo a republicar. |

No início da conferência, não havia arquivos versionados modificados, arquivos
novos não ignorados, stashes ou commits locais ausentes de todas as referências
remotas. Há um único worktree registrado neste clone.

Os PRs #43/#44 existem no remoto, mas suas alterações não estavam aplicadas ao
checkout inicial. Estar publicado numa branch não significa estar integrado em
`develop`. A descrição do PR #44 informa validações de carga e regressão;
esses testes não foram reexecutados nesta conferência.

## Configuração Trail já enviada por outro autor

O commit `feef975` acrescenta sete arquivos/alterações: instruções para agentes,
configuração MCP do Gemini e regras para ignorar o cache. Não contém configuração
específica de Codex/Claude equivalente ao escopo escolhido neste chat.

As instruções apontam o mapa para `.trail/cache/`, enquanto a regra de exclusão
acrescentada menciona `/graft/`. Esse comportamento deve ser reconciliado com a
versão instalada antes de aproveitar o commit.

Não substituir `develop` pela árvore de `dev`: a comparação aponta ausência de
diversas entregas recentes nessa linha antiga. Se a configuração do outro autor
for aproveitada depois, transportar apenas a alteração pertinente por PR,
preservando as instruções do usuário e ajustando o escopo para Codex/Claude.

## Atualização em 23/10/2026

Após `git fetch origin --prune`, o quadro acima mudou e deve ser lido como
histórico do dia 20/10:

- `develop` está em `75b1874` e já integra os PRs #43 (auditoria compartilhada e
  diagnóstico de carga) e #44 (coleta em lotes e espera por vagas). `fix/base-issues`
  (`8661916`) e `fix/coleta` (`ddd4840`) estão contidas em `develop`.
- `main` está 48 commits atrás de `develop`, sem commit exclusivo.
- Seguem abertos, sem integração: `feature/conferencia-issues-base` (#42),
  `feature/25-roteiro-validacao-vm` (#41), `fix/teste-sonda-instavel`,
  `feature/design-system-joyce` e `feature/trail-fase1`; todas ficaram 10 commits
  atrás de `develop`. As duas primeiras ainda criam arquivos em `doc/` e precisam
  ser ajustadas para `docs/` antes do merge.
- `candidato/rodada-5` tem árvore idêntica à de `develop` e `origin/pr-44` é
  apenas um documento de revisão do PR já integrado.
- `origin/dev` continua divergente (41 commits atrás, 1 exclusivo): a configuração
  Trail dele aponta `.trail/cache/` nas instruções, mas ignora `/graft/`.

## O que esta publicação entrega

Este documento torna o resultado local da fase 1 consultável pelo repositório.
Executáveis globais, perfil de telemetria, dependências, ambientes virtuais,
credenciais, caches e resultados brutos permanecem no computador.

Não houve merge, force-push, remoção de branches ou alteração dos PRs #41–#44.
Antes da fase 2, atualizar novamente as referências e respeitar a ordem de
integração de #43 e #44. Não integrar automaticamente entregas pendentes para
instalar uma ferramenta de desenvolvimento.

Referências: [PR #41](https://github.com/Solution-Explores/SigmaTI/pull/41),
[PR #42](https://github.com/Solution-Explores/SigmaTI/pull/42),
[PR #43](https://github.com/Solution-Explores/SigmaTI/pull/43),
[PR #44](https://github.com/Solution-Explores/SigmaTI/pull/44) e
[configuração na dev](https://github.com/Solution-Explores/SigmaTI/commit/feef975b1e5699cdb887c8dc72e64b5c19733bc1).
