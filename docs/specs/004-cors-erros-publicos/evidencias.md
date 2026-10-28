# Evidências — K06 / issue #4

Data: 15/10/2026 (America/Manaus). Responsável: Vinícius.
Base: `dev@d5460397d2212548d58977ac839a2499d0b84670`, atualizada por fast-forward.
Estado: **Revisão e testes**. Implementação publicada na `dev`, validação local e
CI aprovados; revisão independente e aprovação pendentes.

Implementação: [a9c2b0f](https://github.com/Solution-Explores/SigmaTI/commit/a9c2b0f4e74fc9d596f983d14d1d9114d9d4c50d).

## Ambiente e reprodução

Windows, Python 3.12.14, FastAPI 0.142.2, Starlette 1.8.0, HTTPX2 2.13.1,
pytest 9.1.1, dependências de `requirements-dev.txt` em `.venv`.
Somente dados fictícios e provedor simulado, sem chaves reais nem chamadas à IA.

```powershell
python -m pytest -q -p no:cacheprovider tests/test_public_errors.py
python -m pytest -q -p no:cacheprovider --junitxml=test-results/api.xml
python -m pip check
git diff --check
```

| Verificação | Esperado | Obtido |
|---|---|---|
| Suíte K06 | Matriz de origens, preflights e erros seguros | **61 aprovados em 0,92 s**, sem avisos |
| Regressão completa K02/K04/K05/K06 | Nenhuma regressão | **180 aprovados em 22,31 s**, zero falhas/erros/ignorados no JUnit |
| K02 isolada após instalar política K06 | Configuração e contrato preservados | **61 aprovados em 6,05 s** |
| Provedor lento com prazo real K05 | Timeout/retorno em até 15 s | Aprovado; caso no JUnit: 14,023 s incluindo seu setup |
| `pip check` | Dependências compatíveis | Nenhuma dependência quebrada |
| `git diff --check` | Sem problemas de whitespace | Aprovado |
| Diff de Compose, lock de imagens, frontend e configuração K02 | Preservados | Sem alterações |
| CI remoto API de `a9c2b0f` | Testes e dependências aprovados | **Sucesso**, [execução 38799402425](https://github.com/Solution-Explores/SigmaTI/actions/runs/38799402425) |
| CI remoto infraestrutura de `a9c2b0f` | Validadores K03/K04 aprovados | **Sucesso**, [execução 38799402543](https://github.com/Solution-Explores/SigmaTI/actions/runs/38799402543) |
| Artefato remoto | Relatório JUnit disponível | `api-test-results`, id `12002784087`, não expirado na conferência |

JUnit: `test-results/api.xml`, ignorado pelo Git e publicado pelo workflow como
`api-test-results`. Não confundir esse relatório local com resultado remoto do CI.

## Cobertura e autorrevisão

- Origens permitidas testadas no preflight e na chamada real; Vary: Origin e
  resposta com origem exata, sem compartilhamento de credenciais/cookies.
- Origens não permitidas, vazias, null, com esquema/porta/sufixo/caminho diferentes
  e duplicadas recusadas. POST simples text/plain/form e JSON não executam
  anonimização nem provedor. Chamadas sem Origin permanecem funcionais.
- Preflights com DELETE/GET, Authorization, header arbitrário e rede privada
  recusados com corpo genérico; entradas não são refletidas na resposta ou log.
- JSON inválido e payload incorreto retornam 422 genérico; 404/405, HTTPException
  e falha interna 500 também seguem o contrato, com CORS para origem permitida.
- Corpo/headers arbitrários das exceções e chaves/detalhes fictícios não aparecem
  nas respostas/logs. Allow do roteador permanece correto; OpenAPI corresponde.
- Regressão K05 mantém indisponibilidade da IA em HTTP 200, concorrência, timeout
  e fechamento; cancelamentos externos propagam e não há segunda resposta ASGI.

Autorrevisão do agente: conferidos pedido completo, middleware instalado da
Starlette, ordem de tratamento de erros/CORS, diff e evidências. Nenhum achado
adicional identificado no escopo. **Isso não substitui revisão independente.**

## Rastreabilidade e pendências

- [Registro inicial na issue #4](https://github.com/Solution-Explores/SigmaTI/issues/4#issuecomment-6200955458),
  publicado pela sessão autenticada do navegador (conector de escrita ainda restrito).
- Revisor solicitado ao usuário; indicação nominal e aprovação aguardadas.
- Cartão K06 informado pela equipe: [Trello](https://trello.com/c/C9pNKEwW/11-k06-restringir-cors-e-padronizar-erros-p%C3%BAblicos).
  Movido de A fazer para Em andamento e depois **Revisão e testes**, com a lista
  confirmada no cabeçalho. Não foi marcado como concluído.
- [Entrega e pedido de revisão na issue #4](https://github.com/Solution-Explores/SigmaTI/issues/4#issuecomment-6201277632),
  publicação confirmada também pela leitura do conector GitHub.
- [Evidências e pedido de revisão no cartão](https://trello.com/c/C9pNKEwW/11-k06-restringir-cors-e-padronizar-erros-p%C3%BAblicos#comment-6ad133348ecf98ba6180ea5a),
  com commit, issue, documentação, CIs e pendências vinculados; salvamento confirmado.
- Nenhum PR de integração K06 identificado; apenas PR #1 histórico, já fechado.
  Vincular o PR de integração quando existir após revisão e validação conjunta.
- Sem integração à `main` ou fechamento da issue #4. K07 e revisão do conjunto
  continuam pendentes. Esta entrega não implementa autenticação ou amplia a anonimização.

## Conferência de conclusão

| Requisito | Evidência e situação |
|---|---|
| Restringir CORS e padronizar erros públicos | Implementação `a9c2b0f`, 61 testes K06 e regressão completa aprovados |
| Sem segredo no código e falha ao iniciar sem chave | Configuração K02 preservada; testes de configuração/importação aprovados no conjunto de 180 |
| Origem não autorizada recusada | POST simples/JSON e preflight testados; provedor e anonimização não executam nos POSTs recusados |
| Timeout ≤ 15 s e erro genérico com provedor simulado | Regressão K05 aprovada, incluindo orçamento real e falhas; contrato HTTP 200 mantido |
| Evidências vinculadas | CI, artefato JUnit, issue e comentário Trello vinculados acima |
| Documentação pertinente | README, `.env.example`, B4/B5, especificação e atividades atualizados |
| Revisão de outro integrante | **Pendente**; solicitada na issue e no cartão, aguardando indicação/validação da equipe |
| Aprovação, integração à main e conclusão do cartão | **Pendentes**, condicionadas à revisão e validação conjunta; não realizadas |

A implementação técnica está pronta para revisão; a tarefa completa **ainda não
está concluída** pelo fluxo do TCC. Não há evidência de aprovação independente,
e a issue #4 permanece aberta.
