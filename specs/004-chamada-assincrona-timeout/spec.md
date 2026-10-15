# K05 — Chamada assíncrona à IA com timeout

Responsável: **Vinícius (Pessoa 1)**. Prazo: **16/10/2026**.
Sprint: 15–20/10/2026. Entrega parcial da [issue #4](https://github.com/Solution-Explores/SigmaTI/issues/4).
Base conferida: `dev@900dcc409e72fd973be12a76330233ce163f62ed`.

Estado: implementação e validação local concluídas; revisão independente pendente.
Revisor: **a definir com a equipe**. A autorização para implementar não é aprovação
técnica independente. Consulte [atividades](tasks.md) e [evidências](evidencias.md).

## Solução

- O código permanece em `main.py`; `specs/` contém somente registros da entrega.
- HTTPX2 2.13.1 substitui Requests na execução. A versão já usada pelo TestClient
  na K02 é reaproveitada; não se adiciona outro cliente HTTP nem plugin de testes.
- Um `AsyncClient` por aplicação é aberto e fechado pelo `lifespan` do FastAPI.
  A dependência `get_provider_client` permite simular o provedor nos testes.
- A rota usa `await`, com timeout HTTP de 14 s em conexão, leitura, escrita e pool,
  complementado por `asyncio.timeout(14.0)` para a espera total. Não há retry
  automático nem seguimento de redirects. O limite também cobre leitura contínua
  e lenta do corpo, que não necessariamente dispara timeout por inatividade.
- Cancelamentos externos se propagam; não são transformados em diagnóstico.

## Contrato e falhas

Entrada e sucesso de `POST /api/alertas` permanecem iguais. Configuração K02,
anonimização e frontend são preservados. HTTP 200 retorna os três campos atuais:
`status`, `dados_enviados_nuvem` e `diagnostico_ia`.

Timeouts, erros HTTP/transporte, JSON inválido, estrutura inesperada ou diagnóstico
que não seja texto não vazio retornam no último campo:

> Diagnóstico de IA indisponível no momento. Tente novamente mais tarde.

HTTP 200 preserva a apresentação atual do painel e não comprova sucesso da IA ou
persistência em banco. O log WARNING contém categoria (`timeout`, `http`,
`transport`, `invalid_response` ou `unexpected`), classe da exceção, status HTTP
quando conhecido e duração em milissegundos. Não inclui texto arbitrário da
exceção, traceback, credenciais, prompt ou corpo bruto do provedor.

## Dependências, critérios e limites

- K02 já integrada é dependência funcional. #2/#3 não bloqueiam testes isolados
  da API; seus validadores continuam parte da regressão do conjunto.
- Aceite K05: sucesso compatível; provedor lento cancelado e resposta em até 15 s
  no teste controlado; uma chamada pendente não impede outra; erros genéricos com
  logs sem dados sensíveis; cliente reutilizado e fechado; regressão K02 preservada.
- Os 14 s deixam margem para serialização/resposta; não constituem garantia de
  latência ponta a ponta em produção. Não se utilizou IA real.
- A implementação abrange erros da IA previstos nesta K05; demais restrições K06,
  validação completa K07, autenticação, revisão da anonimização e infraestrutura
  não foram ampliadas nesta tarefa. A issue #4 permanece aberta.
- A equipe precisa indicar outro integrante para revisar e reproduzir os testes
  antes da integração à `main`, conforme o [fluxo do TCC](../../doc/fluxo-de-trabalho-tcc.md).

## Referências técnicas

- [HTTPX2 2.13.1](https://pypi.org/project/httpx2/2.13.1/).
- [Timeouts por etapa](https://pydantic.dev/docs/httpx2/advanced/timeouts/).
- [Prazo global e cancelamento asyncio](https://docs.python.org/3.12/library/asyncio-task.html#timeouts).
- [Lifespan do FastAPI](https://fastapi.tiangolo.com/advanced/events/).
