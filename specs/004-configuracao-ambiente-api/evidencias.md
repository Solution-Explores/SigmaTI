# Evidências — K02 e revisões K01 → K02

## Entrega

K02 implementada em checkout separado, a partir de
`dev@b7ebe2c69bda6806fdbbfd4f16efd9bc7c3258b7`, e integrada à base atualizada
`dev@ece353f5f5e4c566939a09b11115f5668a6ec7cc` para publicação. A pasta original
do usuário e suas alterações locais foram preservadas.

**Estado no fluxo: Revisão e testes.** A implementação passou por autorrevisão e
testes locais. A revisão técnica por outro integrante está **pendente**; somente
depois dela e da validação do conjunto poderá seguir para a `main`. A autorização
do usuário para publicar na `dev` não foi registrada como revisão independente.
A entrega atende apenas a parte K02 da issue #4, que deve permanecer aberta.

Ordem executada: implementação K02 → validação inicial → revisão K01 → revisão
K02 e correções → validação final → integração à `dev` atualizada e repetição dos
testes → publicação parcial para revisão por outro integrante.

## Implementação e interface

- Configuração central em `config.py`; chave excluída de `repr(Settings)`.
- Variáveis obrigatórias `OPENROUTER_API_KEY`, `SIGMA_LLM_MODEL`, `SIGMA_CORS_ORIGINS`.
- `.env` da raiz com `python-dotenv`, sem sobrescrever o ambiente do processo,
  sem interpolação e com suporte a UTF-8 com BOM do PowerShell.
- Falha antes de atender HTTP se alguma variável estiver ausente/vazia, a chave
  contiver caracteres impróprios para um Bearer header ou a origem não for válida.
- Chave/modelo conectados à chamada existente; origens conectadas ao CORS.
- Contrato de `POST /api/alertas` preservado.
- Template, README, dependências Python e workflow `api-config.yml` adicionados
  ou atualizados. O workflow verifica PRs/pushes em `dev` e `main`.
- Nenhuma chave real foi usada ou copiada. Chave e modelo ficam vazios no template;
  o usuário deve preenchê-los no ambiente antes de executar a aplicação.

## Testes executados

Ambiente local: Windows, Python 3.12.14; FastAPI 0.142.2, Uvicorn 0.54.0,
Requests 2.34.2, python-dotenv 1.2.4, HTTPX2 2.13.1, pytest 9.1.1.

| Verificação | Resultado |
|---|---|
| Suíte inicial da implementação | 50 testes aprovados; um aviso da dependência HTTPX legada |
| Regressão de chaves malformadas antes da correção | 4 falhas reproduzidas, sem chamadas externas |
| Suíte final `tests/test_config.py` | **61 aprovados em 14,95 s, sem avisos** |
| `python -m pip check` | Nenhuma incompatibilidade encontrada |
| `git diff --check` | Aprovado |
| `git check-ignore .env` | `.env` ignorado |
| Compose padrão, monitoring e `.env.example` | Todos com código 0, sem avisos |
| Arquivos de infraestrutura da K01 comparados à base | Sem alterações |

## Validação após integrar a documentação atual da dev

A base de publicação inclui o fluxo de trabalho, os autores e o status MVP do
commit `ece353f`. O código executável permanece nos locais da aplicação; as
especificações concentram decisões, evidências e pendências. O README destaca
o fluxo no início e vincula a solução e as evidências da K02.

Resultados depois da integração, antes da publicação:

| Verificação | Resultado |
|---|---|
| Suíte `tests/test_config.py` na base atualizada | **61 aprovados em 14,70 s, sem avisos** |
| `python -m pip check` | Nenhuma incompatibilidade encontrada |
| Três validações do Compose | 3/3 aprovadas, código 0 |
| Fluxo, autores e MVP publicados anteriormente | Preservados |
| Compose e workflow originais da K01 | Preservados |

As validações locais não substituem a execução remota do CI nem a revisão do colega.

O comando público para reproduzir a suíte, depois de instalar
`requirements-dev.txt`, é `python -m pytest -q -p no:cacheprovider`. No sandbox
Windows desta execução, o runner local ajustou a criação de diretórios temporários
para contornar ACLs de diretórios com modo 0700. Esse ajuste é exclusivo do runner
local e não foi incluído na aplicação nem nos testes entregues.

Os testes cobrem configuração válida; cada variável ausente, vazia e composta
apenas de espaços; leitura e prioridade do `.env`; independência da pasta de
execução; BOM e valores literais; origens inválidas e explícitas; importação real
da aplicação em subprocessos; preflights autorizados e recusados; chave/modelo
no provedor simulado; formato integral da resposta HTTP; template sem chave real.
As falhas de configuração não refletem os valores nos seus erros.

## Revisão da K01

O relatório completo está em [revisao-k01.md](revisao-k01.md).

| Prioridade | Achado | Tratamento |
|---|---|---|
| P1 | Senhas conhecidas continuam como fallback | Relatado; correção para K03 |
| P1 | Volume alterado de `sigma_data` para `sigma-db-data`, sem roteiro de migração | Relatado; avaliar antes de atualizar uma instalação com dados |
| P2 | `N8N_BASIC_AUTH_*` não configura login na versão de n8n escolhida | Relatado; corrigir configuração/instruções em tarefa própria |
| P2 | Tags PostgreSQL e Zabbix continuam mutáveis | Relatado; correção para K04 |

O Compose da `dev` passou nas três validações e contém os serviços esperados.
A `main` consultada no GitHub ainda contém conflitos; a revisão não realizou a
integração. Contêineres não foram iniciados e volumes não foram acessados.

## Revisão final da K02

**Achado corrigido:** chaves contendo CR, LF, tabulação ou caracteres Unicode
eram aceitas como configuração. Cabeçalhos inválidos podem gerar exceções com
fragmentos da chave, e a rota legada ainda reflete exceções. A configuração passou
a rejeitar essas chaves antes da chamada. Quatro testes de regressão comprovam a
rejeição sem refletir o valor. Isso não altera a padronização geral de erros,
que permanece na K06.

**Ajuste de compatibilidade:** o TestClient da Starlette instalada recomenda
HTTPX2. A dependência de teste foi ajustada e fixada em 2.13.1; a suíte final passou
sem o aviso inicial. O transporte da aplicação continua usando Requests.

Não foram identificados outros problemas pendentes dentro do escopo da K02 após
as correções e a suíte final. Esta revisão foi realizada pelo mesmo agente;
não é uma revisão independente nem uma homologação em produção.

## Limites e próximos passos

- K05/K06/K07 e os demais critérios da issue #4 permanecem posteriores.
- Não houve teste com IA real ou confirmação de disponibilidade de um modelo.
- O CORS limita o navegador e não implementa autenticação nem bloqueio universal
  de clientes HTTP; origem não permitida é recusada no preflight.
- O workflow será acionado pelo push à `dev`. Seu resultado remoto deve ser
  conferido em [GitHub Actions](https://github.com/Solution-Explores/SigmaTI/actions);
  as evidências acima são de execução local.
- Nenhum merge à `main` ou encerramento da issue #4 faz parte desta publicação.
- A próxima etapa é outro integrante revisar o commit, reproduzir os testes e
  registrar aprovação ou achados na issue #4.
