# Stack de Tecnologias do Projeto SIGMA

---

## Visão Geral

| Camada | Tecnologia | Função principal | Onde roda |
|---|---|---|---|
| Backend | Python (FastAPI recomendado) | API central, autenticação, generalização e orquestração | Contêiner |
| Comunicação em tempo real | SSE + WebSocket | Alertas e métricas (SSE); chat com IA (WebSocket) | Contêiner (API) |
| Banco de dados | PostgreSQL | Histórico de incidentes e tabela de usuários | Contêiner |
| Frontend | Vue.js ou React | Dashboard leve e responsivo, com login e chat de IA | Contêiner |
| Automação | n8n | Fluxos periódicos, métricas e relatórios (acesso por VLAN/VPN) | Contêiner |
| Análise de tráfego | Analisador customizado + Wireshark (apoio) | Sonda ativa e troubleshooting profundo | Host |
| Firewall | pfSense | Proteção da rede e envio de alertas | Rede |
| IA (LLM) | OpenRouter / Groq | Diagnósticos no painel e relatórios | Nuvem |
| Implantação | Docker e Docker Compose | Empacotamento e isolamento dos serviços | Servidor |

---

## 1. Núcleo da Aplicação (Backend e Banco de Dados)

### Python (FastAPI ou Django REST)
- Base da API: recebe logs, processa alertas automáticos e integra os serviços do sistema.
- Responsabilidades:
  - Receber os alertas da rede (pfSense e sonda), **validando a chave de cada origem**.
  - **Autenticar os usuários do painel** e aplicar as permissões de cada perfil.
  - **Generalizar** logs e mensagens do chat antes de qualquer envio à IA na nuvem.
  - Orquestrar as integrações entre os componentes.
- **Escolha do framework:** decisão final em conjunto com a equipe técnica. O **FastAPI** é a opção mais defensável:
  - É nativamente assíncrono e gerencia com eficiência o fluxo contínuo de dados, essencial para alertas em tempo real.
  - Gera a documentação da API automaticamente (Swagger/OpenAPI).

### PostgreSQL
- Banco relacional para o histórico estruturado de incidentes (alertas, tempo de detecção, tempo de reparo).
- Guarda a **tabela de usuários** (login, hash da senha e cargo).
- **Não guarda tabela de correspondência (de/para)** entre identificadores originais e generalizados (RF05).
- O histórico permanece **dentro da infraestrutura** e pode conter dados brutos. É protegido por login, chaves e backup com acesso restrito.
- Usa **volume persistente** e tem **backup diário automatizado** (seção 6).
- Oferece um **usuário somente leitura** para o n8n, limitado a dados agregados ou generalizados (mínimo privilégio).

---

## 2. Interface do Usuário (Frontend)

### Vue.js ou React
- Escolha a critério da familiaridade da equipe.
- Painel (dashboard) **leve e responsivo**, com visibilidade da infraestrutura em tempo real.
- **Exige login** (RF07).
- Abriga o **chat interativo com a IA**.
- **Exibe o alerta original (dado exato) ao técnico**, para ele correlacionar a sugestão genérica da IA ao equipamento real (RNF08).

### Protocolo de comunicação em tempo real (API ↔ painel)

| Mecanismo | Tipo de fluxo | Uso | Motivo |
|---|---|---|---|
| **SSE** | Unidirecional (servidor → cliente) | Alertas e métricas da rede | Simples e com reconexão automática nativa |
| **WebSocket** | Bidirecional | Chat com a IA | Permite troca contínua de mensagens |

**Alternativa simplificada:** WebSocket unificado, se a equipe preferir uma única tecnologia.

**Meta de desempenho (RF01):** alerta no painel em até **5 segundos** após a detecção.

---

## 3. Monitoramento e Segurança de Rede

### pfSense
- Firewall de código aberto que protege a rede.
- Envia os logs de anomalias para a API, **com chave e por HTTPS** (RNF07).
- Roda fora do servidor da aplicação.

### Analisador de Tráfego Customizado (código do professor) e Wireshark
- **Analisador customizado (padrão):** sonda ativa que intercepta e analisa pacotes.
  - **Roda no host**, porque o isolamento de rede padrão do Docker impede a captura na interface física.
  - Conecta-se à API com **chave exclusiva por sonda** e HTTPS (RNF07).
- **Wireshark (apoio opcional):** investigação profunda quando o diagnóstico automático não bastar.

---

## 4. Inteligência Artificial (Custo Zero) e Privacidade

### OpenRouter / Groq
- LLMs em camadas gratuitas, em duas frentes:
  1. Diagnósticos interativos no painel.
  2. Relatórios automatizados no backoffice.
- **Meta de desempenho (RNF04):** diagnóstico no painel em até **15 segundos** após a falha.
- **Contingência:** se a IA estiver indisponível, o alerta de 5 s continua no painel, sem o diagnóstico.

### Anonimização e generalização (RF05)

| Dado original | O que a IA recebe |
|---|---|
| IP específico | Máscara de sub-rede |
| Equipamento exato | Categoria do equipamento |
| Nome de pessoa, identificador médico | Removido ou mascarado |
| Horário, setor e equipamento únicos combinados | Generalizado ou descartado (ex.: horário arredondado) |
| Mensagens digitadas no chat | Mesmo tratamento dos logs |

- **Sem pseudonimização:** não há tabela de/para.
- **Premissa de conformidade:** o **provedor de IA** não tem meios razoáveis de reidentificar os dados.
- **Limite reconhecido:** como a Fcecon guarda os logs brutos, a reidentificação interna é possível em tese, por cruzamento de horários.
- **Homologação:** a premissa frente ao art. 12 da LGPD precisa ser validada pelo **DPO ou pelo jurídico** da instituição.
- **Falha segura:** se a generalização falhar, o envio à IA é bloqueado.

### Testes de vazamento e custo da generalização (RNF08)

**Etapa 1: bloqueio de vazamentos**
- Injeção de logs falsos complexos, incluindo **identificação contextual** e texto livre do chat.
- Critério: **zero vazamentos**, repetido a cada mudança nas regras de filtro.

**Etapa 2: custo da generalização**
- Pergunta: arredondar horários ou mascarar sub-redes degrada a capacidade do LLM de **correlacionar eventos e emitir diagnósticos precisos**?
- Método:
  1. Preparar o mesmo cenário em duas versões **fictícias**: original e generalizada.
  2. Enviar as duas ao mesmo modelo, com os mesmos parâmetros.
  3. Repetir cada caso várias vezes, porque o LLM pode variar a resposta.
  4. Comparar os diagnósticos e registrar a taxa de equivalência.
- **A versão "original" também é mock.** Enviar log real à nuvem só para servir de referência seria o vazamento que o projeto quer evitar.
- Meta de equivalência: **a definir**.
- Objetivo: equilíbrio entre privacidade e eficiência.
- A IA devolve uma sugestão genérica e o técnico a liga ao equipamento exato pelo alerta original.

### Proteção de topologia e documentação acadêmica (RNF09)
- Evidências do TCC **somente com dados fictícios**, em formato realista e com valores inventados.
- **Proibido** mimetizar as faixas reais da Fcecon, inclusive as faixas privadas (RFC 1918).
- Blocos permitidos:

| Tipo | Bloco | Norma |
|---|---|---|
| IPv4 | `192.0.2.0/24` | RFC 5737 |
| IPv4 | `198.51.100.0/24` | RFC 5737 |
| IPv4 | `203.0.113.0/24` | RFC 5737 |
| IPv6 | `2001:db8::/32` | RFC 3849 |

- A proteção vale também para **nomes de host, VLANs, setores, modelos de equipamento e padrões de nomenclatura**.
- Para testar várias sub-redes, os blocos /24 são subdivididos (por exemplo, em /26 ou /28).
- Logs reais nunca entram no TCC.

---

## 5. Automação e Relatórios (Backoffice)

### n8n
- Orquestra os fluxos automáticos, com **volume persistente**.
- **Acesso restrito (RF07):** a interface não fica exposta na rede hospitalar geral. Só é acessível por **rede de gerência (VLAN isolada)** ou **túnel seguro (VPN)**, com credenciais próprias limitadas ao Gestor de TI.
- Fluxo programado:
  1. Extrair dados do PostgreSQL (usuário somente leitura).
  2. Calcular métricas (como o MTTR).
  3. Enviar ao OpenRouter **somente dados agregados ou generalizados**.
  4. Disparar relatórios executivos (PDF ou e-mail) para a coordenação.

---

## 6. Infraestrutura, Implantação e Persistência

### Modelo de implantação híbrido

| Onde | Componentes | Motivo |
|---|---|---|
| **Contêineres Docker** (Docker Compose) | `frontend`, `api`, `db`, `n8n` | Portabilidade e isolamento |
| **Host** (servidor ou VM) | Sonda de análise de pacotes | Acesso à interface física |
| **Rede** | pfSense | Firewall da rede |

### Exposição de portas
- A porta do **n8n** é publicada **apenas no endereço da interface de gerência** do servidor (ou acessada via VPN), e não em todas as interfaces.
- Regra de firewall complementar: só a VLAN de gerência alcança essa porta.
- A porta do **PostgreSQL** não é publicada fora da rede interna do Docker.

### Persistência de dados
- PostgreSQL e n8n usam **volumes persistentes** no disco físico do servidor.
- Recriar contêineres **não apaga** o histórico (RF04).

### Backup automatizado e controle de acesso
- **Backup diário** do PostgreSQL (por exemplo, `pg_dump` agendado via cron).
- Cópia em **disco ou local de rede fisicamente separado**. Sem esse destino, registra-se a **limitação conhecida**.
- Logs brutos podem conter IPs e identificadores, então os backups têm **controle estrito de acesso** (permissões restritas e, se possível, criptografia).
- O teste de restauração faz parte da validação.

---

## 7. Segurança e Autenticação de Origens (RNF07)

| Item | Decisão |
|---|---|
| Quem se autentica | Cada sonda de captura e o pfSense |
| Mecanismo | API Key ou token, **exclusivo por origem** |
| Onde é validado | Na API, em toda requisição de entrada |
| Transporte | HTTPS |
| Onde as chaves ficam | **Variáveis de ambiente do servidor**, nunca no código-fonte |
| Revogação e rotação | Mecanismo administrativo na API, restrito ao Gestor de TI |
| Chave inválida ou revogada | Requisição recusada (HTTP 401/403) |

---

## 8. Controle de Acesso ao Painel e ao Backoffice (RF07)

- Login obrigatório para o painel e o chat.
- Usuários no PostgreSQL, com **hash de senha** (bcrypt ou Argon2).
- Matriz de acesso (**proposta** a validar com a equipe):

| Função | Suporte N1 | Analista de Redes | Gestor de TI |
|---|---|---|---|
| Ver alertas e status da rede | Sim | Sim | Sim |
| Usar o chat com a IA | Sim | Sim | Sim |
| Ver histórico de incidentes e detalhes de pacotes | Não | Sim | Sim |
| Ver relatórios gerenciais | Não | Não | Sim |
| Gerenciar usuários | Não | Não | Sim |
| Revogar e rotacionar chaves (RNF07) | Não | Não | Sim |
| Acessar o n8n (VLAN de gerência ou VPN) | Não | Não | Sim |

---

## Fluxo de Dados

```
pfSense (rede) ──────┐  (chave + HTTPS)
                     ├──► API (Python) ──► PostgreSQL ──► Backup diário
Sonda de pacotes ────┘        │                │          (local separado,
(host, chave própria)         │                │           acesso restrito)
                              │                │ leitura somente de dados
                              │                ▼ agregados ou generalizados
                              │          n8n (VLAN de gerência / VPN)
                              │             │
                              │             └──► Generalização ──► OpenRouter ──► Relatórios
                              │
                              ├──► Generalização (falha segura) ──► Groq / OpenRouter
                              │      (logs e chat, sem tabela de/para)       │
                              │                                              ▼
                              │                          sugestão genérica da IA
                              │ SSE / WebSocket                              │
                              ▼                                              │
Técnicos (login + perfil) ──► Frontend (alerta original + chat IA) ◄─────────┘
                              (o técnico liga a sugestão ao equipamento exato)

Validação (fora do fluxo de produção): mocks em blocos RFC 5737 / RFC 3849
  → Etapa 1 (zero vazamentos) e Etapa 2 (custo da generalização) → Anexo A

Contêineres (Docker Compose): frontend, api, db, n8n
Host: sonda de pacotes
Rede: pfSense
```