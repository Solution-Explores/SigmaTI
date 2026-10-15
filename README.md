# SIGMA

Sistema de monitoramento ativo de rede com apoio de IA, desenvolvido como TCC para a equipe de TI de um hospital oncológico (fundação pública).

## Como trabalhamos no TCC

**Comece pelo [fluxo de trabalho do TCC e orientações para issues](doc/fluxo-de-trabalho-tcc.md).**
O desenvolvimento acontece na `dev`, com testes, evidências e revisão por outro
integrante antes da integração à `main`. O guia explica as etapas, as correções,
as colunas do quadro e quando uma issue pode ser encerrada.

## Problema que resolve

A equipe de TI trabalha sem visibilidade em tempo real da rede. Descobre as falhas só quando os usuários reclamam, o que gera:

- Demora para detectar e consertar incidentes (MTTD e MTTR altos).
- Técnicos sobrecarregados com tarefas manuais.
- Ausência de histórico para prevenir falhas.

Em um hospital, a queda da rede afeta prontuários eletrônicos e equipamentos médicos. O SIGMA troca o suporte reativo por um monitoramento contínuo, com custo zero de licenças.

## Funcionalidades

- **Alertas em tempo real:** o painel exibe qualquer anomalia em até 5 segundos após a detecção (RF01).
- **Captura de tráfego e alertas:** integração com o firewall pfSense e com uma sonda própria de análise de pacotes (RF02).
- **Diagnóstico assistido por IA:** chat no painel, com resposta em até 15 segundos (RF03, RNF04).
- **Privacidade (LGPD):** logs e mensagens são generalizados antes de ir à IA. IPs viram sub-redes, equipamentos viram categorias, nomes e identificadores médicos são removidos. Se o filtro falhar, nada é enviado (RF05).
- **Histórico de incidentes:** PostgreSQL com volume persistente e backup diário (RF04, RNF06).
- **Relatórios automáticos:** o n8n calcula métricas como o MTTR e envia relatórios à coordenação (RF06).
- **Controle de acesso:** login com perfis (Suporte N1, Analista de Redes, Gestor de TI). O n8n só é acessível por VLAN de gerência ou VPN (RF07).
- **Segurança de origens:** cada sonda e o pfSense usam chave exclusiva, com HTTPS, revogação e rotação (RNF07).

## Tecnologias

| Camada | Tecnologia | Onde roda |
|---|---|---|
| Backend / API | Python (FastAPI recomendado) | Contêiner |
| Tempo real | SSE (alertas) + WebSocket (chat) | Contêiner (API) |
| Banco de dados | PostgreSQL | Contêiner |
| Frontend | Vue.js ou React | Contêiner |
| Automação e relatórios | n8n | Contêiner |
| Análise de pacotes | Analisador customizado + Wireshark (apoio) | Host |
| Firewall | pfSense | Rede |
| IA (LLM) | OpenRouter / Groq (camadas gratuitas) | Nuvem |
| Implantação | Docker e Docker Compose | Servidor on-premise |

## Arquitetura

```
pfSense ───────────┐  (chave + HTTPS)
                   ├──► API (Python) ──► PostgreSQL ──► Backup diário
Sonda de pacotes ──┘        │                │
(host, chave própria)       │                └──► n8n (VLAN de gerência / VPN) ──► Relatórios
                            │
                            ├──► Generalização ──► Groq / OpenRouter ──► sugestão genérica
                            │
                            │ SSE / WebSocket
                            ▼
Técnicos (login + perfil) ──► Frontend (alerta original + chat com IA)
```

Implantação híbrida: `db` (PostgreSQL) e `n8n` orquestrados via Docker Compose. Os serviços `api` e `frontend` estão em fase de conteinerização. A stack de observabilidade legada/opcional (Zabbix e Grafana) está disponível via perfil (`--profile monitoring`). A sonda roda no host, porque precisa de acesso à interface física de rede. O pfSense fica na rede.

## Como instalar

Pré-requisitos: Docker, Docker Compose e um servidor ou VM Linux com acesso à interface de rede a ser monitorada.

1. Clone o repositório:
   ```bash
   git clone [URL do repositório]
   cd [nome-da-pasta]
   ```
2. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
   Preencha as credenciais obrigatórias do Compose conforme a seção abaixo. As
   variáveis da API, das sondas e da IA são configuradas conforme o componente
   utilizado. **Nunca versione o `.env`.**
3. Suba os serviços em contêiner:
   ```bash
   # Núcleo da aplicação (banco de dados e automação)
   docker compose up -d

   # (Opcional) Incluir stack de observabilidade (Zabbix e Grafana)
   docker compose --profile monitoring up -d
   ```
4. Inicie a sonda no host:
   ```bash
   [comando de execução da sonda]
   ```
5. Configure o pfSense para enviar logs à API, com a chave própria e por HTTPS.

### Credenciais da infraestrutura

O Compose exige as seis variáveis abaixo, definidas no `.env` ou no ambiente do
processo. Se alguma estiver ausente ou vazia, a configuração é recusada, indicando
o nome da variável sem fornecer uma senha padrão.

| Variáveis obrigatórias | Uso |
|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD` | Banco principal da aplicação. |
| `ZABBIX_DB_USER`, `ZABBIX_DB_PASS` | Banco do Zabbix, com os mesmos valores no banco e no servidor Zabbix. |
| `GF_SECURITY_ADMIN_USER`, `GF_SECURITY_ADMIN_PASSWORD` | Conta inicial do Grafana em uma instalação nova. |

Preencha também as credenciais do perfil `monitoring` quando usar somente o
núcleo: o Compose faz a interpolação antes de filtrar perfis. Os serviços de
monitoramento continuam opcionais e só iniciam com `--profile monitoring`.
O `.env.example` contém campos vazios e não deve iniciar uma instalação sem
preenchimento. Variáveis já definidas no processo têm prioridade sobre o arquivo.

Para **uma instalação nova**, escolha os usuários e gere uma senha distinta por
serviço. Execute o comando a seguir uma vez para cada senha e copie o resultado
somente para o `.env` local ou para o ambiente do servidor:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Instalações existentes:** informe as credenciais efetivamente persistidas.
Alterar o `.env` não troca a senha nem o usuário já gravados no PostgreSQL ou no
Grafana. A rotação dessas credenciais exige um procedimento separado e aprovado;
esta configuração não migra nem apaga volumes. Se credenciais antigas forem
inseguras, a correção operacional continua pendente até essa rotação.

O n8n instalado usa o próprio login. Em uma instalação nova, abra o painel local
depois da inicialização e crie a conta **owner** pelo fluxo nativo. Em uma
instalação existente, use a conta já cadastrada. As variáveis antigas
`N8N_USER`/`N8N_PASS` e `N8N_BASIC_AUTH_*` não configuram essa conta e foram
retiradas do Compose. Não há migração de usuários ou implantação de proxy nesta etapa.

Para validar a configuração sem usar seu `.env`, sem revelar senhas e sem iniciar
contêineres:

```bash
python scripts/validate_compose_credentials.py
```

Esse comando gera credenciais fictícias temporárias somente na memória, confere
as configurações padrão, `monitoring` e template e verifica rejeições de valores
ausentes/vazios. Requer Python 3.12+, Docker Compose e um checkout Git. Não usa
chaves da IA, não imprime valores de credenciais e não precisa do Docker Engine ativo.

### Portas e versões da infraestrutura

Os bancos não publicam portas no host. n8n (`5678`), Grafana (`3000`) e Zabbix
(`10051`) usam `127.0.0.1` por padrão. O Zabbix permanece no perfil `monitoring`;
não foi encontrada configuração de coletor externo no repositório.

As imagens usam releases explícitas e digests SHA-256 registrados em
[`docker-images.lock.json`](docker-images.lock.json): PostgreSQL 15.19/Alpine 3.24,
n8n 1.80.0, Zabbix 6.4.21 e Grafana 10.4.0. Não há atualização automática de imagem.
Fixar um digest garante a referência escolhida, não a ausência de vulnerabilidades.
**Zabbix 6.4 está sem suporte**; a migração para uma linha suportada exige tarefa
separada e não foi executada nesta entrega.

Leia a [política de portas e atualização de imagens](doc/politica-imagens-e-portas.md)
antes de alterar os binds ou as imagens. Para conferir a configuração de teste
e a disponibilidade dos manifests oficiais, sem iniciar contêineres:

```bash
python scripts/validate_infrastructure.py --verify-registry
```

O validador testa cenários fictícios; não lê nem homologa o `.env` real do servidor,
não instala firewall/VPN e não verifica o alcance de portas em execução.

### Executar a API no desenvolvimento

Use Python 3.12 ou superior. Na raiz do repositório, crie um ambiente virtual e
instale as dependências:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` (`Copy-Item .env.example .env` no PowerShell ou
`cp .env.example .env` no Linux/macOS) e preencha as configurações da API:

| Variável obrigatória | Conteúdo |
|---|---|
| `OPENROUTER_API_KEY` | Chave da sua conta OpenRouter; mantenha-a somente no ambiente ou no `.env` ignorado pelo Git. |
| `SIGMA_LLM_MODEL` | Identificador do modelo disponível na sua conta OpenRouter; sem modelo padrão fixo no código. |
| `SIGMA_CORS_ORIGINS` | Origens HTTP/HTTPS exatas do painel, separadas por vírgulas, como `http://localhost:5173,http://127.0.0.1:5173`. |

O backend carrega exclusivamente o `.env` da raiz, independentemente da pasta de
execução. Variáveis já definidas no processo têm prioridade, inclusive se vazias;
os valores do arquivo são literais, sem interpolação de `${...}`. O arquivo pode
ser omitido quando as três variáveis estiverem definidas no ambiente. Configuração
ausente, vazia ou com origens inválidas impede a inicialização. A chave aceita
somente caracteres ASCII visíveis, sem espaços internos. Não inclua caminhos,
barra final, credenciais, curingas ou itens vazios na lista de origens. Domínios
internacionalizados devem ser escritos em punycode.

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Em outro terminal, execute `npm ci` e `npm run dev` dentro de `sigma-frontend`.
Se o Vite usar outra porta, ajuste a origem no ambiente e reinicie a API.
Homologação e produção usam o mesmo código: configure chave, modelo e origens
HTTPS do respectivo ambiente antes de iniciar o processo. A chave nunca é enviada
ao frontend. Não há seleção automática de arquivos `.env.production` ou similares.

O Compose atual inicia banco e automação; ele não inicia a API nem injeta suas
variáveis no processo Python do host. Validar o Compose não valida a configuração
obrigatória da API.

O CORS controla o acesso pelo navegador. Preflights de origens não autorizadas
recebem HTTP 400; chamadas diretas sem navegador não passam a exigir autenticação.

### Chamada à IA e indisponibilidade (K05)

A API usa um cliente HTTPX2 assíncrono compartilhado durante a vida da aplicação,
fechado no desligamento. A espera pelo provedor tem prazo global de **14 segundos**
e timeouts HTTP de 14 segundos por etapa, sem retentativas automáticas nem redirects.
O prazo global também interrompe respostas recebidas lentamente em pequenos blocos;
um timeout apenas de leitura não limitaria essa duração total.

`POST /api/alertas` preserva HTTP 200 e os campos `status`,
`dados_enviados_nuvem` e `diagnostico_ia`. Se a IA exceder o prazo, recusar a
requisição, falhar na comunicação ou devolver uma resposta inválida, o diagnóstico
será: **“Diagnóstico de IA indisponível no momento. Tente novamente mais tarde.”**
O HTTP 200 mantém a compatibilidade com o painel e não indica sucesso do provedor
nem comprova persistência do incidente em banco.

O log técnico registra categoria, classe da exceção, status HTTP quando conhecido
e duração. Não registra chave, prompt, corpo bruto da IA ou texto da exceção.
Os 14 segundos reservam margem para responder dentro da meta de 15 segundos nos
testes controlados; não garantem latência de rede, carga do servidor ou resposta
de um modelo real em produção.

Veja a [solução K05](specs/004-chamada-assincrona-timeout/spec.md),
as [evidências](specs/004-chamada-assincrona-timeout/evidencias.md) e
as [pendências de revisão](specs/004-chamada-assincrona-timeout/tasks.md).
Demais atividades K06/K07 e a revisão independente continuam pendentes; a K05
é uma entrega parcial da issue #4.

Para executar os testes sem uma chave real ou chamadas externas:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q -p no:cacheprovider
```

## Como usar

1. Acesse o painel e faça login com o seu perfil.
2. Acompanhe alertas e o status da rede em tempo real.
3. Abra o chat com a IA para receber a sugestão de diagnóstico. A IA devolve uma resposta genérica, e o painel mostra o alerta original para você ligá-la ao equipamento exato.
4. O Gestor de TI acessa o n8n (VLAN de gerência ou VPN) para os relatórios e gerencia usuários e chaves.

### Permissões por perfil

| Função | Suporte N1 | Analista de Redes | Gestor de TI |
|---|---|---|---|
| Ver alertas e status da rede | Sim | Sim | Sim |
| Usar o chat com a IA | Sim | Sim | Sim |
| Ver histórico e detalhes de pacotes | Não | Sim | Sim |
| Ver relatórios gerenciais | Não | Não | Sim |
| Gerenciar usuários e chaves | Não | Não | Sim |
| Acessar o n8n | Não | Não | Sim |

## Estrutura do projeto

```
[frontend/]  -> painel e chat com a IA
[api/]       -> API, autenticação, generalização e integrações
[probe/]     -> sonda de análise de pacotes (roda no host)
[n8n/]       -> fluxos de relatórios
[docs/]      -> estudo de caso e documentação do TCC
docker-compose.yml -> orquestração dos contêineres
.env.example       -> modelo de variáveis de ambiente
```

> Ajuste os nomes das pastas para a estrutura real do repositório.

## Validação

| Requisito | Meta |
|---|---|
| RF01 | Alerta no painel em até 5 s |
| RNF04 | Diagnóstico da IA em até 15 s |
| RNF06 | Backup restaurável e sem perda de dados ao recriar contêineres |
| RNF07 | Requisição sem chave, inválida ou revogada é recusada (401/403) |
| RNF08 | Zero vazamentos de dados sensíveis para a IA |

A validação completa está no estudo de caso (seção 6).

## Segurança e privacidade

- Chaves e senhas ficam em variáveis de ambiente, nunca no código.
- Não há tabela de correspondência (de/para) entre dados originais e generalizados.
- O histórico bruto fica dentro da infraestrutura da instituição, protegido por login, chaves e backup com acesso restrito.
- Evidências e testes usam **somente dados fictícios**, nos blocos reservados `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (RFC 5737) e `2001:db8::/32` (RFC 3849).
- A premissa de conformidade com o art. 12 da LGPD depende de homologação do DPO ou do jurídico da instituição.

## Limitações conhecidas

- Sem disco ou local de rede separado, o backup fica no mesmo servidor e não protege contra falha física total.
- As metas de 5 s e 15 s dependem das camadas gratuitas de IA. Com a IA fora do ar, o alerta continua no painel, sem o diagnóstico.
- A generalização é baseada em regras: reduz o risco, mas não o elimina. Por isso existe a falha segura.
- Arredondar horários e mascarar sub-redes pode reduzir a precisão do diagnóstico. O RNF08 mede essa perda com dados fictícios.
- O servidor on-premise e a VLAN ou VPN de gerência ainda precisam ser confirmados pela instituição.

## Status

MVP (TCC).

## Autores

### Discentes

- **Iohand Jheremy** — [LinkedIn](https://www.linkedin.com/in/iohan-jheremy/)
- **Joyce Yasmin** — LinkedIn: Pendente
- **Vinicis Gomes** — [LinkedIn](https://www.linkedin.com/in/viniciusgomesdev/)

### Docente

- **Euler Azevedo** — [LinkedIn](https://www.linkedin.com/in/eulerazevedo/)
