# K06 — Restringir CORS e padronizar erros públicos

Responsável: **Vinícius (Pessoa 1)**. Prazo: **16/10/2026**.
Sprint: 15–20/10. Entrega parcial da [issue #4](https://github.com/Solution-Explores/SigmaTI/issues/4).
Base atualizada: `dev@d5460397d2212548d58977ac839a2499d0b84670`.
Estado: **Revisão e testes** no quadro; implementação publicada na `dev`, testes
locais e CI aprovados. Commit: [a9c2b0f](https://github.com/Solution-Explores/SigmaTI/commit/a9c2b0f4e74fc9d596f983d14d1d9114d9d4c50d).
Revisão independente e aprovação ainda pendentes.
Revisor: **a definir pela equipe**; a autorrevisão não substitui outro integrante.

## Dependências e escopo

K02 fornece a configuração obrigatória e a lista de origens. K05 fornece o cliente
assíncrono, timeout e tratamento de falhas da IA. Ambas já estão na base. #2/#3
não bloqueiam esta alteração isolada da API; suas configurações são preservadas.

Esta entrega cobre a recusa efetiva de Origin não autorizado, restrições de
preflight e padronização de erros HTTP/validação/internos. Não muda anonimização,
autenticação, frontend, Compose ou o contrato HTTP 200 da K05. K07 e revisão final
do conjunto continuam separadas. Não fechar a issue #4 somente pela K06.

## Comportamento e interfaces

- Lista exata de `SIGMA_CORS_ORIGINS`; sem regex, curingas ou normalização que
  aceite outra origem, esquema ou porta. Origin ausente permite clientes de serviço;
  Origin vazio, `null`, duplicado ou fora da lista é recusado antes da rota/IA.
- Requisições comuns recusadas retornam 403, sem `Access-Control-Allow-Origin`.
  Preflight recusado retorna 400; origens duplicadas retornam 403 em qualquer caso.
  Preflight permitido retorna 200, com POST, Content-Type e cabeçalhos simples do
  padrão CORS. Cabeçalhos arbitrários, outros métodos e rede privada são recusados.
- `allow_credentials=False`: o painel atual não usa cookies no fetch. Futura
  autenticação precisa reavaliar essa decisão. CORS não autentica o remetente;
  clientes não navegador podem omitir ou forjar Origin.
- Erros usam `{"detail": "mensagem pública"}` com status preservado: 400 inválida;
  401 autenticação necessária; 403 não permitida; 404 recurso não encontrado;
  405 método não permitido; 422 dados inválidos; 429 limite excedido; outras falhas
  4xx usam mensagem de requisição inválida; 5xx usam erro interno genérico.
- Erros de validação não devolvem `input`, `ctx` ou corpo recebido. Erros HTTP não
  devolvem `detail` nem headers arbitrários da exceção; o Allow do 405 mantém
  somente métodos HTTP conhecidos. Falhas internas não expõem traceback.
- Log técnico: categoria, classe, status e duração quando disponível, sem dados
  recebidos, Origin, path/query, headers, chave ou texto arbitrário de exceção.
- CORS envolve a barreira de erros ASGI; assim 4xx/500 também podem ser lidos pela
  origem permitida. Falhas depois de headers enviados não iniciam outra resposta;
  cancelamentos externos se propagam. A rota atual é JSON não streaming.
- OpenAPI descreve `PublicError` nos erros 403/422/500 de `POST /api/alertas`.
  Sucesso e indisponibilidade da IA mantêm HTTP 200 e os três campos da K05.

## Código e validação

Política em `api_errors.py`, instalada por `main.py`; documentação em `specs/`
não contém cópias de código executável. Testes em `tests/test_public_errors.py`
cobrem a matriz de origens/preflights, recusa antes da rota, validação, erros do
roteador, HTTPException, 500 com CORS, logs seguros, contrato K05 e OpenAPI.

Consulte [evidências](evidencias.md) e [atividades](tasks.md). Revisão por outro
integrante, aprovação e validação conjunta na `dev` antecedem qualquer integração
à `main`, conforme o [fluxo do TCC](../../doc/fluxo-de-trabalho-tcc.md).

## Referências

- [Issue #4 e pedido completo do orientador](https://github.com/Solution-Explores/SigmaTI/issues/4).
- [Comentário inicial da K06](https://github.com/Solution-Explores/SigmaTI/issues/4#issuecomment-6200955458).
- [FastAPI: handlers de erros e validação](https://fastapi.tiangolo.com/tutorial/handling-errors/).
- A ordem dos middlewares e o comportamento dos preflights foram conferidos no
  código instalado da Starlette 1.8.0, usado pela suíte local.
