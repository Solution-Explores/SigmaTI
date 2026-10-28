# K02 — Configuração da API por ambiente

**Referência:** planejamento da sprint, K02; parte de configuração da [issue #4](https://github.com/Solution-Explores/SigmaTI/issues/4).

**Base da implementação:** `dev@b7ebe2c69bda6806fdbbfd4f16efd9bc7c3258b7`.

**Base atualizada para a publicação:** `dev@ece353f5f5e4c566939a09b11115f5668a6ec7cc`.

**Estado no fluxo:** Revisão e testes — implementada, com autorrevisão e testes
locais; aguardando revisão e validação de outro integrante antes de `main`.
A autorização de publicação na `dev` não substitui essa revisão técnica.

Consulte as [evidências](evidencias.md), as [atividades](tasks.md) e a
[revisão da K01](revisao-k01.md). Esta entrega é parcial para a issue #4.

## Solução e decisões

- A configuração executável permanece em [`config.py`](../../../config.py) e é
  consumida por [`main.py`](../../../main.py); `specs/` registra a solução e suas
  evidências, sem receber cópias de código executável.
- Uma configuração imutável é carregada antes de criar a aplicação para impedir
  que uma configuração incompleta só seja percebida na primeira requisição.
- O ambiente do processo prevalece sobre o arquivo de desenvolvimento, permitindo
  usar o mesmo código em cada ambiente. Valores do `.env` são literais para não
  alterar chaves que contenham uma sequência como `${...}`.
- Chave e modelo não têm fallback no código. As origens são explícitas para não
  manter o curinga existente. O contrato da rota e o transporte HTTP atual são
  preservados, limitando a mudança à K02.
- Os [testes](../../../tests/test_config.py) usam valores fictícios e um provedor
  simulado; não dependem de uma conta ou de chamadas reais à IA.

## Comportamento

- `OPENROUTER_API_KEY`, `SIGMA_LLM_MODEL` e `SIGMA_CORS_ORIGINS` são obrigatórias.
- O backend lê o `.env` da raiz usando `python-dotenv`, com `override=False`, sem
  interpolação de valores. O ambiente do processo prevalece, inclusive se vazio.
- As configurações são validadas ao importar a aplicação, antes de atender HTTP.
  Ausência, valor vazio ou origem inválida interrompem a inicialização com uma
  mensagem contendo somente o nome da variável e a regra violada.
- A chave aceita apenas ASCII visível, sem espaços internos, evitando que valores
  inválidos provoquem erros de cabeçalho que reflitam seu conteúdo na rota legada.
- Origens são valores HTTP/HTTPS explícitos separados por vírgulas. Espaços nas
  bordas são removidos; curingas, caminhos, credenciais, itens vazios e portas
  inválidas são recusados. O template usa localhost e loopback na porta 5173.
- A chamada ao OpenRouter usa a chave e o modelo configurados; não há segredo
  nem modelo padrão no código. A chave fica excluída da representação de Settings.
- O contrato de `POST /api/alertas` permanece inalterado.

## Aceite

- Inicializa com configuração válida, inclusive sem `.env` quando há variáveis.
- Não inicializa com qualquer configuração obrigatória ausente/vazia.
- Ambiente prevalece sobre `.env`; a pasta de execução não muda o arquivo lido.
- Testes verificam o payload e Authorization com um provedor simulado.
- Preflight de origem permitida retorna 200; origem não autorizada retorna 400
  sem `Access-Control-Allow-Origin`. CORS não substitui autenticação da API.
- Template, instruções, dependências e workflow de testes acompanham a alteração.

## Limites

K05 (cliente assíncrono/timeout), K06 (demais restrições e erros públicos) e K07
(testes completos da API com provedor simulado) permanecem posteriores. Os testes
desta entrega cobrem apenas a configuração e a integração mínima necessária.
A issue #4 não pode ser encerrada somente com a K02. Não inclui conteinerizar a
API, mudar o frontend, alterar o Compose da K01 ou integrar na `main`.

## Referências técnicas

- [python-dotenv](https://pypi.org/project/python-dotenv/): carga sem sobrescrever o ambiente.
- [Starlette CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware): preflight e restrição de origens no navegador.
