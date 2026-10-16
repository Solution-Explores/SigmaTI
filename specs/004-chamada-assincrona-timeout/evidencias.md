# Evidências — K05 / issue #4

Data: 15/10/2026 (America/Manaus). Responsável: Vinícius.
Base: `dev@900dcc409e72fd973be12a76330233ce163f62ed`, confirmada por `git pull --ff-only origin dev`.
Estado: **publicada na dev para Revisão e testes**; validação local e CI aprovados,
revisão de outro integrante pendente.

Implementação publicada: [d7a3e0d](https://github.com/Solution-Explores/SigmaTI/commit/d7a3e0d1b965128426424f399d9005de158bdb32).

## Ambiente e reprodução

Windows, Python 3.12.14 em `.venv`, com dependências de `requirements-dev.txt`.
FastAPI 0.142.2, Uvicorn 0.54.0, HTTPX2 2.13.1, python-dotenv 1.2.4 e pytest 9.1.1.
Somente dados fictícios e provedor simulado; nenhuma chamada real ao OpenRouter.

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q -p no:cacheprovider --junitxml=test-results/api.xml
python -m pip check
git diff --check
```

## Resultados

| Verificação | Esperado | Obtido |
|---|---|---|
| Testes K02 + K05 | Sucesso, erros seguros, concorrência, cancelamento e lifecycle | 94 aprovados em 20,61 s, sem avisos |
| Provedor simulado aguardando 20 s | Cancelar aos 14 s; responder em até 15 s | 14,031 s, cancelamento confirmado |
| Corpo recebido continuamente em blocos lentos | Prazo global interrompe e fecha stream | Aprovado com orçamento reduzido de 0,1 s |
| Falhas HTTP 301/401/403/429/500/502 | Mensagem genérica, sem retry/redirect | Aprovado |
| Timeouts de conexão/leitura/escrita/pool e falhas de transporte | Mensagem genérica, categoria e classe no log | Aprovado |
| JSON/estrutura/diagnóstico inválidos | Não refletir conteúdo bruto nem exceção | Aprovado |
| Chamada lenta concorrente com outra | Segunda conclui antes de liberar primeira | Aprovado no mesmo event loop |
| Reuso, fechamento e cancelamento externo | Um cliente por lifespan, fechado; CancelledError propagado | Aprovado |
| Regressão completa, `python -m pytest -q -p no:cacheprovider --junitxml=test-results/api.xml` | Todos os casos aprovados | **119 aprovados em 20,87 s, sem avisos**, zero falhas/erros/ignorados no JUnit |
| `python -m pip check` | Dependências compatíveis | Nenhuma dependência quebrada |
| `git diff --check` | Sem erros de whitespace | Aprovado |
| Validador K03, `python scripts/validate_compose_credentials.py` | Credenciais obrigatórias e Compose válido | **32 verificações aprovadas**; nenhum contêiner iniciado |
| Validador K04, `python scripts/validate_infrastructure.py` | Portas e imagens preservadas | **12 cenários aprovados**; nenhum contêiner iniciado |
| CI remoto da API | Sucesso para `d7a3e0d` | **Aprovado**: [execução 38794814488](https://github.com/Solution-Explores/SigmaTI/actions/runs/38794814488) |
| CI remoto da infraestrutura | Sucesso para `d7a3e0d` | **Aprovado**: [execução 38794814430](https://github.com/Solution-Explores/SigmaTI/actions/runs/38794814430) |

Comando da primeira execução: `python -m pytest -q -p no:cacheprovider tests/test_provider.py tests/test_config.py -rP`.
Os logs de falha contêm somente categoria, classe, status quando conhecido e duração;
os testes conferem ausência da chave fictícia, texto privado do provedor e dados brutos.

O relatório JUnit local está em `test-results/api.xml` (ignorado pelo Git). O workflow
da API executa a suíte completa, verifica dependências e publica `api-test-results`
como artefato, inclusive em caso de falha dos testes.

O primeiro validador K03 executado no sandbox recusou avisos de acesso negado ao
arquivo de configuração local do Docker, embora o Compose retornasse código 0.
Uma tentativa com diretório Docker vazio não encontrou o plugin Compose. A execução
do comando original com acesso aprovado à configuração passou nas 32 verificações,
sem alterar o validador ou usar/imprimir credenciais reais. O K04 e os testes de política
passaram no sandbox. Os scripts e arquivos de infraestrutura não foram alterados.

## Autorrevisão

Conferidos o pedido da issue, o fluxo do TCC, o diff e os cenários de falha. A suíte
cobre cancelamento real, progresso concorrente, fechamento do stream lento, ausência
de retentativas/redirects e logs sem conteúdo arbitrário. O transporte da produção
tem limites explícitos verificados em teste. Nenhum achado adicional identificado
no escopo K05. Esta conferência foi feita pelo mesmo agente, não por outro integrante.

## Processo e pendências

- O revisor será indicado pela equipe. Autorrevisão e testes não substituem essa aprovação.
- O conector GitHub recusou o comentário inicial com HTTP 403 (`Resource not accessible by integration`).
  A tentativa não publicou comentário. A alternativa pelo navegador foi verificada:
  a sessão está sem login e exige autenticação para comentar. O [texto da entrega](registro-issue.md)
  está pronto para publicação pela equipe. Nenhuma aprovação foi atribuída artificialmente.
- Quadro externo não acessado: nenhuma movimentação de cartão é declarada.
- Sem integração à `main`, PR novo ou encerramento da issue. K06/K07 continuam separadas.
- As três imagens locais não versionadas foram preservadas.
- O prazo foi validado no ambiente controlado; não comprova latência da IA ou do servidor em produção.
