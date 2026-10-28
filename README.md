# SIGMA

Sistema de monitoramento ativo de rede com apoio de IA, desenvolvido como TCC para a equipe de TI de um hospital oncológico (fundação pública).

## Problema que resolve

A equipe de TI trabalha sem visibilidade em tempo real da rede e só descobre as falhas quando os usuários reclamam. Isso causa:

- demora para detectar e consertar incidentes (MTTD e MTTR altos);
- técnicos sobrecarregados com tarefas manuais;
- falta de histórico para prevenir falhas.

Em um hospital, a queda da rede afeta prontuários eletrônicos e equipamentos médicos. O SIGMA troca o suporte reativo por monitoramento contínuo, sem custo de licenças.

## Funcionalidades

- **Alertas em tempo real:** o painel exibe qualquer anomalia em até 5 segundos após a detecção (RF01).
- **Captura de tráfego e alertas:** integração com o firewall pfSense e com uma sonda própria de análise de pacotes (RF02).
- **Diagnóstico assistido por IA:** resposta no painel em até 15 segundos (RF03, RNF04).
- **Privacidade (LGPD):** logs e mensagens são generalizados antes de ir à IA. IPs viram sub-redes, equipamentos viram categorias, e nomes e identificadores médicos são removidos. Se o filtro falhar, nada é enviado (RF05).
- **Histórico de incidentes:** PostgreSQL com volume persistente e backup diário (RF04, RNF06).
- **Relatórios automáticos:** o n8n calcula métricas como o MTTR e envia relatórios à coordenação (RF06).
- **Controle de acesso:** login com perfis (Suporte N1, Analista de Redes e Gestor de TI). O n8n só é acessível pela VLAN de gerência ou por VPN (RF07).
- **Segurança de origens:** cada sonda e o pfSense usam chave exclusiva, com HTTPS, revogação e rotação (RNF07).

## Tecnologias

| Camada | Tecnologia | Onde roda |
|---|---|---|
| Backend e API | Python e FastAPI | Host |
| Tempo real | SSE | API |
| Banco de dados | PostgreSQL | Contêiner |
| Frontend | React e Vite | Host |
| Automação e relatórios | n8n | Contêiner |
| Análise de pacotes | Analisador customizado, com Wireshark de apoio | Host |
| Firewall | pfSense | Rede |
| IA (LLM) | OpenRouter e Groq (camadas gratuitas) | Nuvem |
| Implantação | Docker e Docker Compose | Servidor on-premise |

Detalhes em [Stack de tecnologia](docs/arquitetura/stack-de-tecnologia.md).

## Arquitetura

```
pfSense ───────────┐  (chave + HTTPS)
                   ├──► API (Python) ──► PostgreSQL ──► Backup diário
Sonda de pacotes ──┘        │                │
(host, chave própria)       │                └──► n8n (VLAN de gerência / VPN) ──► Relatórios
                            │
                            ├──► Generalização ──► Groq / OpenRouter ──► sugestão genérica
                            │
                            │ SSE
                            ▼
Técnicos (login + perfil) ──► Frontend (alerta original + diagnóstico com IA)
```

A implantação é híbrida. O Docker Compose orquestra `db` (PostgreSQL) e `n8n`. A API e o frontend rodam no host por enquanto, e a conteinerização deles está planejada. Zabbix e Grafana, uma stack de observabilidade opcional, entram com `--profile monitoring`. A sonda roda no host, porque precisa da interface física de rede. O pfSense fica na rede.

## Para quem trabalha no TCC

O desenvolvimento segue o [Git Flow](docs/processo/gitflow.md): branches `feature/*` e `fix/*` entram na `develop` por PR, com testes, evidências e revisão, e uma `release/*` prepara a `main`. Comece pelo [fluxo de trabalho do TCC](docs/processo/fluxo-de-trabalho-tcc.md), que explica as etapas, as colunas do quadro e quando uma issue pode ser encerrada.

Toda a documentação está indexada em [docs/README.md](docs/README.md).

## Estado do desenvolvimento

- A demonstração controlada segue o [plano de demonstração](docs/planejamento/plano-demonstracao-2026-10-27.md). O [plano de conclusão de 20/10](docs/planejamento/plano-conclusao-2026-10-20.md) registra a ordem de implementação, os cortes de escopo e as dependências externas. Itens planejados não são funcionalidades entregues.
- A API exige `SIGMA_JWT_SECRET` e a configuração da IA. Para usuários, use `SIGMA_DATABASE_URL` (PostgreSQL, recomendado) ou `SIGMA_USERS_FILE` (arquivo, só laboratório). Veja a [instalação](docs/operacao/instalacao.md).
- Com `SIGMA_USERS_FILE`, sessões e usuários alterados ficam em memória. Com PostgreSQL, eles persistem ([identidades e sessões](engenharia/docs/07-persistencia-identidades.md)).
- O [estado operacional no PostgreSQL](engenharia/docs/08-estado-operacional.md) cobre esquema, recuperação de aprovações e execuções, medições, retenção e APIs. A coleta contínua e as páginas de gestão são os próximos incrementos. Veja também a [coleta de eventos e o SSE](engenharia/docs/09-coleta-eventos.md).
- O experimento E6 avalia cada identificador anotado, e seus resultados valem só para o corpus sintético.
- As issues #5 e #6 continuam abertas.
- A resposta `Incidente Registrado` é um contrato legado e não comprova a gravação de um incidente no PostgreSQL.
- As correções de sessão, painel e anonimização estão nas [evidências da recuperação da sprint](docs/specs/011-recuperacao-sprint/evidencias.md), integradas à `develop` pelo [PR #32](https://github.com/Solution-Explores/SigmaTI/pull/32).

## Como instalar

O passo a passo, com comandos de Windows e Linux, está em [Instalação para desenvolvimento](docs/operacao/instalacao.md). Este README resume os pontos principais.

Pré-requisitos: Docker, Docker Compose e um servidor ou VM Linux com acesso à interface de rede monitorada. O núcleo `sigma_eng` é instalado por pip, sem `PYTHONPATH`:

```bash
python -m pip install -e "./engenharia[api,dev]"
```

### Instalação nova

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

### Atualização de uma instalação com dados

Não aplique a instalação nova sobre uma base existente. Se existir um volume legado `sigma_data`, migre os dados logicamente para `sigma-db-data` e preserve a origem para recuperação. O [roteiro de migração](docs/operacao/migracao-volume-postgresql.md) cobre pré-requisitos, backup, restauração, conferência e reversão. A migração só pode ser feita depois de identificar e homologar a instalação real, e ainda não foi executada. Renomear um volume não basta.

### Credenciais da infraestrutura

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

### Portas e versões da infraestrutura

Os bancos não publicam portas no host. n8n (`5678`), Grafana (`3000`) e Zabbix (`10051`) escutam em `127.0.0.1` por padrão. O Zabbix fica no perfil `monitoring`, e o repositório não tem configuração de coletor externo.

As imagens usam releases explícitas e digests SHA-256 em [`docker-images.lock.json`](docker-images.lock.json): PostgreSQL 15.19 (Alpine 3.24), n8n 1.80.0, Zabbix 6.4.21 e Grafana 10.4.0. Não há atualização automática. Fixar o digest garante a referência escolhida, não a ausência de vulnerabilidades. **O Zabbix 6.4 está sem suporte**, e a migração para uma linha suportada exige tarefa própria.

Leia [Portas e imagens](docs/operacao/politica-imagens-e-portas.md) antes de mudar binds ou imagens. Para conferir a configuração de teste e os manifests oficiais, sem iniciar contêineres:

```bash
python scripts/validate_infrastructure.py --verify-registry
```

O validador usa cenários fictícios. Ele não lê nem homologa o `.env` do servidor, não instala firewall nem VPN e não verifica o alcance das portas em execução.

### Executar a API no desenvolvimento

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

Em outro terminal, rode `npm ci` e `npm run dev` em `sigma-frontend`. Se o Vite usar outra porta, ajuste a origem no ambiente e reinicie a API. Homologação e produção usam o mesmo código. Configure chave, modelo e origens HTTPS do ambiente antes de iniciar. A chave nunca vai ao frontend, e não há seleção automática de `.env.production` ou similares.

O Compose não inicia a API nem injeta variáveis no processo Python do host. Validar o Compose não valida a configuração da API.

### Origens e erros públicos

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

Veja a [especificação](docs/specs/004-cors-erros-publicos/spec.md), as [evidências](docs/specs/004-cors-erros-publicos/evidencias.md) e as [tarefas de revisão](docs/specs/004-cors-erros-publicos/tasks.md).

### Chamada à IA e indisponibilidade

A API usa um cliente HTTPX assíncrono, compartilhado durante a vida da aplicação e fechado no desligamento. O prazo global de espera pelo provedor é de **14 segundos**, com timeouts HTTP de 14 segundos por etapa, sem retentativas nem redirects. O prazo global também interrompe respostas que chegam devagar, em blocos pequenos, o que um timeout só de leitura não faria.

`POST /api/alertas` mantém o HTTP 200 e os campos `status`, `dados_enviados_nuvem` e `diagnostico_ia`. Se a IA estourar o prazo, recusar a requisição, falhar na comunicação ou devolver uma resposta inválida, o diagnóstico será: **"Diagnóstico de IA indisponível no momento. Tente novamente mais tarde."** O HTTP 200 mantém a compatibilidade com o painel. Ele não indica sucesso do provedor nem prova a gravação do incidente em banco.

O log técnico registra categoria, classe da exceção, status HTTP (quando conhecido) e duração. Não registra chave, prompt, corpo bruto da IA nem texto da exceção. Os 14 segundos deixam margem para responder dentro da meta de 15 segundos nos testes controlados. Eles não garantem a latência da rede, a carga do servidor nem a resposta de um modelo real em produção.

Veja a [especificação](docs/specs/004-chamada-assincrona-timeout/spec.md), as [evidências](docs/specs/004-chamada-assincrona-timeout/evidencias.md) e as [pendências](docs/specs/004-chamada-assincrona-timeout/tasks.md). A cobertura complementar e a correção da coleta estão nas [evidências K07 e K08](docs/specs/007-008-ci-provedor-simulado/evidencias.md). O aceite integral da issue #4 continua separado, e as entregas atuais são parciais.

Para rodar os testes sem chave real nem chamadas externas:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q -p no:cacheprovider
```

## Como usar

1. Acesse o painel e faça login com o seu perfil.
2. Acompanhe os alertas e o status da rede em tempo real.
3. Peça à IA uma sugestão de diagnóstico. Ela devolve uma resposta genérica, e o painel mostra o alerta original para você ligá-la ao equipamento exato.
4. O Gestor de TI acessa o n8n (VLAN de gerência ou VPN) para os relatórios e gerencia usuários e chaves.

### Permissões por perfil

| Função | Suporte N1 | Analista de Redes | Gestor de TI |
|---|---|---|---|
| Ver alertas e status da rede | Sim | Sim | Sim |
| Usar o diagnóstico com a IA | Sim | Sim | Sim |
| Ver histórico e detalhes de pacotes | Não | Sim | Sim |
| Ver relatórios gerenciais | Não | Não | Sim |
| Gerenciar usuários e chaves | Não | Não | Sim |
| Acessar o n8n | Não | Não | Sim |

## Painel operacional

O frontend fica em `sigma-frontend/` e usa a API de `VITE_API_URL` (padrão `http://localhost:8000`). Rode `npm ci` e `npm run dev` nessa pasta. A API precisa de `SIGMA_DATABASE_URL`, das migrações aplicadas e de usuários cadastrados, conforme os guias de [identidades](engenharia/docs/07-persistencia-identidades.md) e de [coleta](engenharia/docs/09-coleta-eventos.md). Sem persistência operacional, as áreas mostram indisponibilidade (503), sem dados fictícios no lugar.

| Perfil | Áreas do painel |
|---|---|
| `suporte_n1` | Saúde dos serviços e diagnóstico |
| `analista_redes` | Áreas anteriores, incidentes e aprovações |
| `gestor_ti` | Todas as áreas, incluindo auditoria |

A API também aplica a autorização. Esconder a navegação não substitui o controle de acesso por perfil. O tema claro ou escuro muda no cabeçalho. Sessão e cursor SSE ficam em memória, então recarregar exige login. O SSE usa Bearer e `Last-Event-ID`, reconecta com espera progressiva e atualiza os dados ao conectar. Há uma consulta de recuperação a cada 15 segundos.

A área de saúde distingue dados ausentes ou desatualizados de disponibilidade. O orçamento parcial é um limite máximo, e a projeção exige cobertura integral da janela. O MTTD aparece sem amostras enquanto não houver um início real de falha registrado. Aprovar ou rejeitar exige justificativa na interface, outro operador e o papel mínimo. Essa página registra decisões e não executa comandos. A integridade JSONL mostrada na auditoria cobre a trilha de sondas, e os eventos do PostgreSQL aparecem à parte.

Testes:

```bash
npm test                      # componentes
npm run test:e2e              # diagnóstico, no navegador
python scripts/validate_postgres.py --tests "backend/tests/test_panel_api.py backend/tests/test_panel_e2e.py"
```

O último comando faz o ensaio completo com um banco descartável. Ele prepara um schema isolado e publica capturas em `test-results/`. Instale o Chromium com `npx playwright install chromium`. No Windows, `SIGMA_BROWSER_CHANNEL=chrome` usa o Chrome já instalado.

Validação e limites: [evidências do painel](docs/specs/017-painel-operacional/brief.md).

## Backup, restauração e smoke

O procedimento está em [Backup, restauração e atualização](docs/operacao/backup-restauracao.md). Em resumo:

- `scripts/backup.sh` e `scripts/restore.sh` envolvem o CLI Python `scripts/recovery.py`. Exigem escritores parados, chave fora do pacote e destino novo.
- `scripts/smoke.sh` exercita, em contêineres descartáveis, uma falha real, o SSE, o backup autenticado, a restauração e a recriação.
- O CI publica só o relatório, sem dump nem chave.

O ensaio em outra máquina e a ativação do modelo systemd continuam pendentes. A validação local não equivale ao aceite integral da issue #25.

## Segurança e privacidade

- Chaves e senhas ficam em variáveis de ambiente, nunca no código.
- Não há tabela de correspondência (de/para) entre dados originais e generalizados.
- O histórico bruto fica dentro da infraestrutura da instituição, protegido por login, chaves e backup com acesso restrito.
- Evidências e testes usam **só dados fictícios**, nos blocos reservados `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (RFC 5737) e `2001:db8::/32` (RFC 3849).
- A conformidade com o art. 12 da LGPD depende da homologação do DPO ou do jurídico da instituição.

## Validação

| Requisito | Meta |
|---|---|
| RF01 | Alerta no painel em até 5 s |
| RNF04 | Diagnóstico da IA em até 15 s |
| RNF06 | Backup restaurável e sem perda de dados ao recriar contêineres |
| RNF07 | Requisição sem chave, inválida ou revogada é recusada (401 ou 403) |
| RNF08 | Zero vazamentos de dados sensíveis para a IA |

A validação completa está na seção 6 do [estudo de caso](docs/arquitetura/estudo-de-caso.md). O registro de testes e achados corrigidos está em [revisão K01 a K06](docs/specs/revisao-k01-k06/validacao.md).

## Limitações conhecidas

- Sem disco ou local de rede separado, o backup fica no mesmo servidor e não protege contra falha física total.
- As metas de 5 s e 15 s dependem das camadas gratuitas de IA. Com a IA fora do ar, o alerta continua no painel, sem diagnóstico.
- A generalização é feita por regras: reduz o risco, mas não o elimina. Por isso existe a falha segura.
- Arredondar horários e mascarar sub-redes pode reduzir a precisão do diagnóstico. O RNF08 mede essa perda com dados fictícios.
- O servidor on-premise e a VLAN ou VPN de gerência ainda precisam ser confirmados pela instituição.

## Estrutura do projeto

```
backend/                      API FastAPI: main.py, routers/, persistence/, migrations/ e tests/
sigma-frontend/               painel em React
engenharia/                   núcleo sigma_eng, testes e experimentos
scripts/                      validação, backup e utilitários
deploy/                       unidade systemd e overlays do Compose
docs/                         documentação, specs e evidências
docker-compose.yml            orquestração dos contêineres
.env.example                  modelo de variáveis de ambiente
```

## Status

MVP (TCC).

## Autores

Discentes:

- **Iohand Jheremy**: [LinkedIn](https://www.linkedin.com/in/iohan-jheremy/)
- **Joyce Yasmin**: LinkedIn pendente
- **Vinícius Gomes**: [LinkedIn](https://www.linkedin.com/in/viniciusgomesdev/)

Docente:

- **Euler Azevedo**: [LinkedIn](https://www.linkedin.com/in/eulerazevedo/)
