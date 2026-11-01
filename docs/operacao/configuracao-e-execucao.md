# Configuração e execução

Passo a passo de instalação, credenciais, portas, execução da API e comportamento de origens, erros e IA. Parte do conteúdo que antes estava no README. O resumo está no [README](../../README.md#início-rápido).

O passo a passo, com comandos de Windows e Linux, está em [Instalação para desenvolvimento](instalacao.md).

Pré-requisitos: Docker, Docker Compose e um servidor ou VM Linux com acesso à interface de rede monitorada. O núcleo `sigma_eng` é instalado por pip, sem `PYTHONPATH`:

```bash
python -m pip install -e "./engenharia[api,dev]"
```

## Instalação nova

Ainda não há máquina de implantação, e nenhuma base com dados foi indicada para migração. A primeira instalação usa o volume `sigma-db-data` do Compose. O nome efetivo inclui o projeto Compose, então mantenha a pasta e o nome do projeto nas execuções seguintes. Não mude a imagem para renomear dados: imagem e volume têm ciclos de vida diferentes.

Este roteiro configura o núcleo Docker e a API de desenvolvimento. A sonda e a integração com o pfSense continuam planejadas, sem procedimento de instalação.

1. Clone a branch `develop` e registre a referência:
   ```bash
   git clone --branch develop https://github.com/Solution-Explores/SigmaTI.git
   cd SigmaTI
   git branch --show-current
   git rev-parse HEAD
   ```
2. Crie o `.env` e preencha as [credenciais da infraestrutura](#credenciais-da-infraestrutura). Configure as variáveis da API, das sondas e da IA conforme o componente. Nunca versione o `.env`.
   ```bash
   cp .env.example .env
   ```
3. Valide a configuração. Os comandos não iniciam contêineres:
   ```bash
   docker compose config --quiet
   docker compose --profile monitoring config --quiet
   ```
4. Inicie os serviços:
   ```bash
   # Núcleo: banco de dados e automação
   docker compose up -d

   # Opcional: Zabbix e Grafana
   docker compose --profile monitoring up -d
   ```
5. Inicie a API e o frontend conforme [Executar a API no desenvolvimento](#executar-a-api-no-desenvolvimento). O Compose não os inicia.

A sonda, o pfSense e a implantação operacional continuam pendentes. Não trate o MVP como instalação hospitalar homologada. A API exige JWT nas rotas protegidas.

## Atualização de uma instalação com dados

Não aplique a instalação nova sobre uma base existente. Se existir um volume legado `sigma_data`, migre os dados logicamente para `sigma-db-data` e preserve a origem para recuperação. O [roteiro de migração](migracao-volume-postgresql.md) cobre pré-requisitos, backup, restauração, conferência e reversão. A migração só pode ser feita depois de identificar e homologar a instalação real, e ainda não foi executada. Renomear um volume não basta.

## Credenciais da infraestrutura

O Compose exige seis variáveis, definidas no `.env` ou no ambiente do processo. Se alguma faltar ou estiver vazia, a configuração é recusada e informa o nome da variável. Não existe senha padrão.

| Variáveis obrigatórias | Uso |
|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD` | Banco principal da aplicação. |
| `ZABBIX_DB_USER`, `ZABBIX_DB_PASS` | Banco do Zabbix, com os mesmos valores no banco e no servidor Zabbix. |
| `GF_SECURITY_ADMIN_USER`, `GF_SECURITY_ADMIN_PASSWORD` | Conta inicial do Grafana em uma instalação nova. |

Preencha também as credenciais do perfil `monitoring` quando usar só o núcleo, porque o Compose interpola as variáveis antes de filtrar os perfis. Os serviços de monitoramento continuam opcionais e só iniciam com `--profile monitoring`. O `.env.example` tem campos vazios e não inicia uma instalação sem preenchimento. Variáveis definidas no processo têm prioridade sobre o arquivo.

**Instalação nova:** escolha os usuários e gere uma senha distinta por serviço. Rode o comando abaixo uma vez por senha e copie o resultado só para o `.env` local ou para o ambiente do servidor:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Instalação existente:** informe as credenciais realmente gravadas. Mudar o `.env` não troca a senha nem o usuário já gravados no PostgreSQL ou no Grafana. A rotação exige um procedimento separado e aprovado, que não migra nem apaga volumes. Se as credenciais antigas forem inseguras, a correção continua pendente até essa rotação.

**n8n:** ele tem login próprio. Em uma instalação nova, abra o painel local e crie a conta owner pelo fluxo nativo. Em uma existente, use a conta já cadastrada. As variáveis antigas `N8N_USER`, `N8N_PASS` e `N8N_BASIC_AUTH_*` não configuram essa conta e foram retiradas do Compose. Não há migração de usuários nem proxy nesta etapa.

Para validar a configuração sem usar o seu `.env`, sem revelar senhas e sem iniciar contêineres:

```bash
python scripts/validate_compose_credentials.py
```

O script gera credenciais fictícias só na memória, confere as configurações padrão, `monitoring` e template, e verifica a recusa de valores ausentes ou vazios. Exige Python 3.12+, Docker Compose e um checkout Git. Não usa chaves da IA nem imprime credenciais, e não precisa do Docker Engine ativo.

## Portas e versões da infraestrutura

Os bancos não publicam portas no host. n8n (`5678`), Grafana (`3000`) e Zabbix (`10051`) escutam em `127.0.0.1` por padrão. O Zabbix fica no perfil `monitoring`, e o repositório não tem configuração de coletor externo.

As imagens usam releases explícitas e digests SHA-256 em [`docker-images.lock.json`](../../docker-images.lock.json): PostgreSQL 15.19 (Alpine 3.24), n8n 1.80.0, Zabbix 6.4.21 e Grafana 10.4.0. Não há atualização automática. Fixar o digest garante a referência escolhida, não a ausência de vulnerabilidades. **O Zabbix 6.4 está sem suporte**, e a migração para uma linha suportada exige tarefa própria.

Leia [Portas e imagens](politica-imagens-e-portas.md) antes de mudar binds ou imagens. Para conferir a configuração de teste e os manifests oficiais, sem iniciar contêineres:

```bash
python scripts/validate_infrastructure.py --verify-registry
```

O validador usa cenários fictícios. Ele não lê nem homologa o `.env` do servidor, não instala firewall nem VPN e não verifica o alcance das portas em execução.

## Executar a API no desenvolvimento

Use Python 3.12 ou superior. Na raiz do repositório, crie o ambiente virtual e instale as dependências:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` (`Copy-Item .env.example .env` no PowerShell, `cp .env.example .env` no Linux/macOS) e preencha:

| Variável obrigatória | Conteúdo |
|---|---|
| `OPENROUTER_API_KEY` | Chave da sua conta OpenRouter. Guarde só no ambiente ou no `.env`, que o Git ignora. |
| `SIGMA_LLM_MODEL` | Identificador do modelo disponível na sua conta. Não há modelo padrão no código. |
| `SIGMA_CORS_ORIGINS` | Origens exatas do painel, separadas por vírgula, como `http://localhost:5173,http://127.0.0.1:5173`. |
| `SIGMA_JWT_SECRET` | Segredo local aleatório de pelo menos 32 bytes. Não há valor padrão. |
| `SIGMA_USERS_FILE` | Caminho absoluto do arquivo de hashes criado por `scripts/create_demo_users.py`. Alternativa em arquivo (laboratório) ao PostgreSQL. |

O backend lê só o `.env` da raiz, de qualquer pasta de execução. Variáveis já definidas no processo têm prioridade, mesmo vazias. Os valores do arquivo são literais, sem interpolação de `${...}`. O arquivo pode faltar se todas as variáveis obrigatórias estiverem no ambiente.

A API não inicia se alguma configuração faltar, estiver vazia ou tiver origens inválidas. A chave aceita só caracteres ASCII visíveis, sem espaços. Nas origens, não use caminhos, barra final, credenciais, curingas nem itens vazios, e escreva domínios internacionalizados em punycode.

```bash
python -m uvicorn --app-dir backend main:app --host 127.0.0.1 --port 8000 --reload
```

Em outro terminal, rode `npm ci` e `npm run dev` em `frontend`. Se o Vite usar outra porta, ajuste a origem no ambiente e reinicie a API. Homologação e produção usam o mesmo código. Configure chave, modelo e origens HTTPS do ambiente antes de iniciar. A chave nunca vai ao frontend, e não há seleção automática de `.env.production` ou similares.

O Compose não inicia a API nem injeta variáveis no processo Python do host. Validar o Compose não valida a configuração da API.

## Origens e erros públicos

A API aceita só as origens exatas de `SIGMA_CORS_ORIGINS`. Um `Origin` não autorizado, vazio, `null` ou duplicado é recusado **antes de executar a rota ou chamar a IA**. Chamadas comuns recusadas recebem HTTP 403. Preflights recusados recebem 400, ou 403 se a origem for duplicada.

O preflight permite `GET` e `POST`, os cabeçalhos `Content-Type` e `Authorization` e os cabeçalhos simples do padrão CORS. O painel envia um Bearer JWT, sem cookies, e guarda o token só em memória. Recarregar exige novo login, e o logout revoga a sessão no servidor. Não há curingas nem autorização de rede privada.

Clientes de serviço sem `Origin` continuam possíveis. Fora do navegador o cabeçalho pode ser omitido ou forjado, então **essa política não substitui a autenticação da API**.

Os erros HTTP usam JSON `{"detail": "mensagem pública"}`, sem refletir a entrada, o corpo, o caminho, a origem, a chave ou o texto da exceção. As respostas 4xx e 500 para uma origem permitida também levam os cabeçalhos CORS, para o painel poder lê-las.

| HTTP | Mensagem pública |
|---|---|
| 400 | Requisição inválida. |
| 403 | Requisição não permitida. |
| 404 | Recurso não encontrado. |
| 405 | Método não permitido. |
| 422 | Dados da requisição inválidos. |
| 500 e outras falhas internas | Erro interno do servidor. |

O log registra categoria, classe da falha, status e duração, quando disponíveis. Não inclui entradas, query, cabeçalhos nem traceback. O OpenAPI documenta o formato `PublicError`. As respostas 200 de sucesso e de IA indisponível seguem o contrato descrito na próxima seção.

Veja a [especificação](../specs/004-cors-erros-publicos/spec.md), as [evidências](../specs/004-cors-erros-publicos/evidencias.md) e as [tarefas de revisão](../specs/004-cors-erros-publicos/tasks.md).

## Chamada à IA e indisponibilidade

A API usa um cliente HTTPX assíncrono, compartilhado durante a vida da aplicação e fechado no desligamento. O prazo global de espera pelo provedor é de **14 segundos**, com timeouts HTTP de 14 segundos por etapa, sem retentativas nem redirects. O prazo global também interrompe respostas que chegam devagar, em blocos pequenos, o que um timeout só de leitura não faria.

`POST /api/alertas` mantém o HTTP 200 e os campos `status`, `dados_enviados_nuvem` e `diagnostico_ia`. Se a IA estourar o prazo, recusar a requisição, falhar na comunicação ou devolver uma resposta inválida, o diagnóstico será: **"Diagnóstico de IA indisponível no momento. Tente novamente mais tarde."** O HTTP 200 mantém a compatibilidade com o painel. Ele não indica sucesso do provedor nem prova a gravação do incidente em banco.

O log técnico registra categoria, classe da exceção, status HTTP (quando conhecido) e duração. Não registra chave, prompt, corpo bruto da IA nem texto da exceção. Os 14 segundos deixam margem para responder dentro da meta de 15 segundos nos testes controlados. Eles não garantem a latência da rede, a carga do servidor nem a resposta de um modelo real em produção.

Veja a [especificação](../specs/004-chamada-assincrona-timeout/spec.md), as [evidências](../specs/004-chamada-assincrona-timeout/evidencias.md) e as [pendências](../specs/004-chamada-assincrona-timeout/tasks.md). A cobertura complementar e a correção da coleta estão nas [evidências K07 e K08](../specs/007-008-ci-provedor-simulado/evidencias.md). O aceite integral da issue #4 continua separado, e as entregas atuais são parciais.

Para rodar os testes sem chave real nem chamadas externas:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q -p no:cacheprovider
```
