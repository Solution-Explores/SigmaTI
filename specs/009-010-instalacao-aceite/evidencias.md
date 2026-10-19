# Evidências e revisão — K09 / K10

**Resultado: K09 bloqueada na instalação dos contêineres; K10 reprovada no fluxo integrado.**

Execução e revisão pelo Codex em 19/10/2026, nesta conversa, conforme solicitado
pelo usuário. Não há revisão independente ou homologação manual de outro
integrante declarada. O fluxo do TCC foi aplicado até as falhas, com achados
encaminhados para K11/K12.

## Ambiente e isolamento

- Checkout remoto independente `dev@142efd229151f88ebd5ed65521663c82d3020368`,
  em `test-results/k09-clean-20261019`; Git limpo antes e depois dos testes.
- Outro `.venv`: Python 3.12.14 e dependências fixadas instaladas do zero;
  nenhum `.env` ou ambiente virtual da cópia antiga foi reutilizado.
- Node.js 24.19.0, npm 12.0.2 e Vite 8.3.2 conforme lockfile; Windows.
- Docker Engine/CLI 29.8.1, Compose v5.5.1. Docker Desktop foi iniciado;
  outros projetos existentes foram identificados e preservados.
- Projeto exclusivo `sigmati-k09-20261019`; nomes com prefixo `sigma-k09-`,
  volumes novos e portas locais 15678, 13000 e 15051. Imagens/digests preservados.
- Credenciais geradas somente no `.env` ignorado do checkout de teste;
  nenhum valor de senha, token ou segredo consta neste relatório.

## K09 — instalação limpa

| Verificação | Resultado |
|---|---|
| Clone independente, instalação Python e pip check | Aprovados; nenhuma incompatibilidade. |
| Regressão no ambiente novo | **346 aprovados em 54,46 s**, sem falhas, erros ou ignorados. |
| Primeiro npm ci | Concluiu, mas omitiu `@rolldown/binding-win32-x64-msvc@1.2.12`; build falhou com `Cannot find native binding`. O pacote já consta no lockfile. |
| Download para cache e segundo npm ci --include=optional | Instalação completa **sem alterar versões ou o lockfile**. Causa original da omissão não determinada; não foi necessário apagar/regenerar o lockfile. |
| npm run build | **Aprovado**, 17 módulos transformados; saída em dist/. |
| npm run lint | **Reprovado**: `src/App.jsx:38:14`, variável err não usada (`no-unused-vars`). K12. |
| Compose isolado: config --quiet | Aprovado; nenhum volume do projeto existia antes. |
| up -d com perfil monitoring | **Bloqueado no download**: `failed to copy: local error: tls: bad record MAC`, exit 1. Duas tentativas falharam; o erro TLS foi capturado na segunda. Imagens e validação TLS preservadas. |
| Prontidão, autenticação e persistência dos serviços | **Não verificadas**: imagens não terminaram de baixar; nenhum contêiner ou volume do projeto foi criado. |

Artefatos locais ignorados: `test-results/k09-python.xml` e `.txt`,
`k09-docker-failure.txt`, `k09-installation.json`, `k09-compose.py` e
`k09-override.yml`. As credenciais, dependências e logs também permanecem locais.
Validar manifests, como na K08, não prova inicialização dos serviços.

## K10 — API real, IA simulada

Comando executado na raiz:

```text
.venv/Scripts/python.exe scripts/validate_api_acceptance.py --checkout test-results/k09-clean-20261019 --output test-results/k10-acceptance.json --port 8000 --keep-server
```

Uvicorn serviu a API do checkout independente em loopback, com autenticação ativa,
JWT de teste no ambiente, auditoria isolada e HTTPX2 MockTransport. Nenhuma chamada
ao OpenRouter real. Manter o servidor permitiu observar o painel; não é deploy.

**16 verificações aprovadas, duas reprovadas; exit 1.**

| Critério | Resultado |
|---|---|
| Token obrigatório antes do provedor | Aprovado: 401, zero chamadas. |
| Login de sessão, sem devolver chave permanente | Aprovado: 200 e JWT no contrato. |
| Perfil insuficiente | Aprovado: 403. |
| Alerta autenticado, contrato e generalização | Aprovado: 200, três campos esperados, sem IP/identificador original ou chave de API. |
| CORS da resposta para origem permitida | Aprovado. |
| Provedor 503 e JSON inválido | Aprovados: mensagem pública genérica, sem detalhes privados. |
| Provedor lento e cancelamento | **Aprovado: 14,016 s**, dentro de 15 s; cancelamento registrado. |
| Origem recusada, payload inválido e falha do sanitizador | Aprovados: 403/422/500, sem novas chamadas ao provedor. |
| Preflight com Content-Type | Aprovado: 200. |
| Preflight com Content-Type e Authorization | **Reprovado: 400**, esperado 200 para origem autorizada. K11. |
| Logout revoga sessão | **Reprovado:** logout 200 e mesmo token ainda recebe 200; esperado 401. K11 / issue #6. |
| Inicialização sem chave, modelo ou origem | Três verificações aprovadas: processo recusa iniciar. |
| Logs sem detalhes privados, chave ou token | Aprovado. |

Snapshot sanitizado em [resultados/aceite-k09-k10-2026-10-19.json](../../resultados/aceite-k09-k10-2026-10-19.json).
Artefatos locais: `test-results/k10-acceptance.json`, `.txt`, `.server.log` e
`.events.jsonl`; eventos contêm somente fases do provedor.

## Fluxo no navegador

| Fronteira | Resultado |
|---|---|
| Painel renderiza em http://localhost:5173 | Aprovado; Vite do checkout independente. |
| Botão envia alerta fictício | Executado com IP de documentação 192.0.2.10. |
| Painel → API | **Reprovado:** formulário não envia JWT; API recusa com 401. Não há login no painel. |
| Resposta → mensagem ao usuário | **Reprovado:** informa que não conseguiu conectar ao FastAPI, embora o servidor esteja ativo e tenha recusado autenticação. |
| Diagnóstico no painel | **Não alcançado**; verificação parou na primeira fronteira quebrada. |

Captura local: `test-results/k10-browser-failure.jpg`. A API registrou 401; o
console do navegador não apresentou entradas adicionais. Nenhum token foi
injetado no navegador para mascarar a ausência do fluxo de login.

## Encaminhamento e revisão

- **K11:** permitir Authorization no CORS com origem restrita; implementar login
  no painel e mensagens distintas para 401/403; revogar sessão no logout.
- **K12:** investigar TLS no download das camadas Docker, completar instalação
  com imagens fixadas, corrigir lint e documentar instalação das dependências
  opcionais no Windows. Causa de TLS não determinada; certificados não desativados.
- **K09/K10:** repetir prontidão/autenticação/persistência dos serviços e fluxo
  integrado após as correções. Sem aceite para concluir tarefas, integrar à main
  ou encerrar issues nesta execução.

A revisão distingue sucesso, falha confirmada e etapa não executada. Regressão
aprovada não altera a reprovação deste aceite.
