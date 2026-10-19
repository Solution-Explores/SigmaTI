# Evidências e revisão — K08 / K07

Data: 19/10/2026. Base: `dev@f4c2a5e`. Ambiente: Windows, Python 3.12.14,
pytest 9.1.1, FastAPI 0.142.2, HTTPX2 2.13.1 e Docker Compose v5.5.1.

## Escopo e resultado local

O [fluxo de trabalho do TCC](../../doc/fluxo-de-trabalho-tcc.md) foi incorporado à
execução: leitura dos cartões e da issue, implementação na `dev`, testes,
registro de evidências e revisão técnica. O usuário solicitou que a revisão
fosse feita nesta conversa, sem aguardar outro integrante. Implementação,
execução dos testes e revisão: **Codex**. Não se declara revisão independente
nem execução manual de testes pelo usuário ou por outro integrante.

| Verificação | Resultado |
|---|---|
| Baseline, `python -m pytest --collect-only -q -p no:cacheprovider` | 280 testes coletados; cinco erros `No module named sigma_eng`; testes HTTP de engenharia não eram executados pelo skip de `httpx`. |
| `python -m pip check` | Nenhuma incompatibilidade de dependências. |
| Comando de CI: `python -m pytest -q -p no:cacheprovider --junitxml=test-results/api.xml` (acrescido de `--durations=5` somente para medir esta execução) | **346 aprovados em 55,09 s; zero falhas, erros e ignorados.** |
| Timeout real da K07 com login/JWT ativo | Caso aprovado; duração da chamada do teste: **14,03 s**. O teste mede a requisição, exige 14 ≤ tempo ≤ 15 s e comprova cancelamento do provedor. |
| `python -m pytest engenharia/tests -q -p no:cacheprovider` | **58 aprovados em 3,03 s**, sem depender de importar `main.py` antes da coleta. |
| Correção do teste de porta fechada: `python -m pytest engenharia/tests/test_stats_probe.py -q -p no:cacheprovider` | **10 aprovados em 1,57 s** no Windows após reservar a porta sem iniciar listener. Validação Linux pelo CI indicada abaixo. |
| `python scripts/validate_compose_credentials.py` | **32 verificações aprovadas** com credenciais fictícias, sem iniciar contêineres. |
| `python scripts/validate_infrastructure.py --verify-registry` | **12 cenários aprovados**, com confirmação dos quatro manifests oficiais e digests; nenhum contêiner iniciado ou camada baixada. |
| `git diff --check` | Aprovado. |

Artefatos locais ignorados pelo Git: `test-results/api.xml`,
`test-results/k07-k08-final.txt`, `test-results/k08-engineering-only.txt`,
`test-results/k08-compose.txt` e `test-results/k08-infrastructure.txt`.
O CI publica seu próprio JUnit em `api-test-results`.

As primeiras execuções no sandbox falharam ao reabrir diretórios temporários
privados do pytest/Compose no Windows. Redirecionar TEMP também não resolveu a
restrição. Os resultados aprovados acima foram obtidos repetindo os comandos
com acesso normal aos temporários, sem alterar permissões, remover testes ou
reutilizar o `.env` antigo. Uma execução de revisão encontrou um teste de runbook
sem aspas no executável em caminho com espaços: corrigido e conjunto reexecutado.

## Cobertura da K07

| Comportamento | Evidência |
|---|---|
| Sucesso, modelo/chave configurados, contrato da resposta, cliente compartilhado e encerramento | `tests/test_provider.py` e `tests/test_config.py`. |
| Falhas HTTP, timeouts HTTP, transporte, JSON/formato inválido e logs sem detalhes privados | `tests/test_provider.py`, incluindo sucesso e três modos de falha após login real. |
| Prazo total, fluxo lento em blocos, concorrência e cancelamento externo | `tests/test_provider.py`, incluindo teste real com prazo de 14 s. |
| Token ausente (sem cabeçalho), vazio, inválido ou expirado | Quatro cenários retornam 401 e verificam que o handler do provedor não foi chamado. |
| CORS, preflights e erros públicos | `tests/test_public_errors.py` e `tests/test_config.py`; política existente preservada. |
| Falha da sanitização impede chamada e sucesso envia dados generalizados | `tests/test_fail_closed.py` e asserções do payload em `tests/test_provider.py`. |

A alteração não usa um provedor real, não modifica o contrato público nem
adiciona dependências. Parte dos testes legados continua isolando autenticação
pela fixture existente; os cenários novos da K07 e os HTTP de engenharia mantêm
`SIGMA_AUTH_ENFORCED=1`. Os 67 testes dedicados de autenticação também permanecem
incluídos na regressão.

## Achados da revisão

| Achado | Decisão / evidência |
|---|---|
| Importação de `sigma_eng` dependia de configuração externa do caminho. | **Corrigido na K08** por configuração do pytest da raiz; execução isolada da engenharia aprovada. Empacotamento instalável permanece issue #9. |
| `importorskip("httpx")` escondia os testes HTTP apesar de HTTPX2 ser a dependência instalada. | **Corrigido na K08**: imports obrigatórios e JWT de gestor no cliente de teste; quatro testes reativados. |
| Executável de runbook sem aspas em caminho Windows com espaços. | **Corrigido na K08** no teste; preservado `shell=False` e a verificação de `;` como argumento literal. |
| Teste de porta fechada criava servidor em thread e fechava o socket enquanto `accept()` aguardava; no Linux a conexão ainda era aceita. | **Corrigido na K08**: socket reservado sem `listen()`, mantido durante a sondagem. Evita tanto o listener residual quanto a reutilização da porta por outro processo. |
| Preflight da origem permitida com `content-type,authorization` recebe 400. | **K11, prioridade alta**: CORS ainda permite somente Content-Type. Reproduzido em processo isolado com TestClient; bloqueia o painel autenticado. |
| Login → status 200 → logout 200 → mesmo token ainda acessa status com 200. | **K11 / issue #6**: logout registra auditoria, mas não revoga a sessão. Reproduzido sem provedor externo. |
| Chave JWT possui fallback literal; contas de demonstração e usuários em memória permanecem. | **K11 / issue #6**: inspeção de `auth.py`. A proposta da issue pede usuários em PostgreSQL e Argon2id/bcrypt; implementação usa memória/PBKDF2. Não declarar aceite integral da issue #6. |
| `auth.py` lê SIGMA_JWT_SECRET antes de `load_settings()` carregar `.env`. | **K11 / issue #6**: inspeção da ordem de imports em `main.py`. Roteiro K08 orienta definir a chave no processo antes da inicialização. |

Reprodução dos achados dinâmicos preservada localmente em
`test-results/review-findings.py` e `test-results/k11-findings.txt`, com apenas
dados fictícios e sem imprimir JWT ou credenciais.

## Limites e próximas tarefas

- **K08:** coleta/execução do CI corrigida e roteiro de instalação preparado.
- **K07:** cobertura conferida e complementada com autenticação ativa.
- **K09:** executar instalação limpa e confirmar inicialização/acesso dos serviços.
  O Docker Engine está inativo nesta máquina; não houve inicialização de contêineres.
- **K10:** executar o aceite integrado, incluindo navegador, autenticação e serviços.
  Testes locais com IA simulada não comprovam latência real ou funcionamento hospitalar.
- **K11/K12:** tratar os achados nos respectivos escopos; nenhuma issue encerrada.

## Publicação

Implementação inicial publicada na `dev` em
[`6c8533e`](https://github.com/Solution-Explores/SigmaTI/commit/6c8533e9b99bd4375cf76eec716e7bdcd2f0dcd0).
O [CI de infraestrutura](https://github.com/Solution-Explores/SigmaTI/actions/runs/39264758423)
foi aprovado. O [CI da API](https://github.com/Solution-Explores/SigmaTI/actions/runs/39264758284)
coletou as duas suítes corretamente, mas expôs a corrida do teste de porta fechada
no Linux: 345 aprovados e uma falha, sem testes ignorados. Não houve tentativa de
mascarar a falha reexecutando o mesmo código até obter sucesso.

Conforme o fluxo, a correção foi isolada na branch
`codex/fix-k08-porta-fechada`, testada localmente e integrada à `dev` no commit
[`7975c00`](https://github.com/Solution-Explores/SigmaTI/commit/7975c00).

Conjunto corrigido conferido no GitHub:

- [API e engenharia — sucesso](https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110405):
  **346 testes aprovados em 22,31 s**, em Ubuntu / Python 3.12.15.
- [Artefato JUnit do CI](https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110405/artifacts/12193086123).
- [Infraestrutura — sucesso](https://github.com/Solution-Explores/SigmaTI/actions/runs/39265110475).

A revisão técnica está concluída nesta conversa. Os cartões K07/K08 recebem o
registro atualizado e passam a **Revisão e testes**, com a revisão já realizada
e os links de CI. A etapa remanescente é a integração do conjunto na K13, após
conferir o aceite K10 e os achados K11/K12; não é espera por outro revisor.
Não integrar automaticamente os commits anteriores de autenticação e
anonimização nem encerrar as issues #4/#5/#6 como efeito desta entrega parcial.
