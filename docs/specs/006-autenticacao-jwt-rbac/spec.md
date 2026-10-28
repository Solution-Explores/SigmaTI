> Atualização 19/10/2026: entrega parcial em correção/revisão. As afirmações de conclusão abaixo são históricas e não equivalem ao aceite integral. Consulte [a revisão da sprint](../011-recuperacao-sprint/evidencias.md).

# Feature Specification: Autenticação e Perfis (RF07): Login com JWT de Sessão e RBAC #6

**Feature Branch**: `006-autenticacao-jwt-rbac`  
**Created**: 2026-10-18  
**Status**: Concluído / Pronto para Revisão  
**Input**: Issue #6 — Autenticação e perfis (RF07): login com JWT de sessão e RBAC (Bloqueador B9 de `engenharia/docs/05-seguranca-e-pendencias.md`, requisitos RF07 e RNF07).

---

## Contexto e Motivação

Anteriormente, nenhuma rota da API exigia autenticação. O `README.md` e a documentação de arquitetura (`doc/stack-de-tecnologia.md`, `doc/estudo-de-Caso.md`) definiam três perfis operacionais com responsabilidades bem delimitadas:
1. **Suporte N1**: visualização de alertas, status da rede e interação com o chat de IA;
2. **Analista de Redes**: todas as permissões de N1 somadas à visualização de pacotes, incidentes e ferramentas operacionais do núcleo de engenharia (`/api/eng/*`);
3. **Gestor de TI**: permissão irrestrita, englobando relatórios gerenciais, gestão de usuários, rotação de credenciais, auditoria e acesso ao n8n via rede restrita de gerência.

Além disso, as rotas `/api/eng/*` portadas do Sentinel Vigilark estavam marcadas como pendência de segurança com risco explícito: *"Rotas `/api/eng/*` sem autenticação. Não expor fora do laboratório antes de RF07"* (Bloqueador B9).

A Issue #6 estabelece a implementação formal de autenticação por JWT de sessão de curta duração com controle de acesso baseado em papéis (RBAC), herança do fluxo do Sentinel Vigilark (`routers/auth` e `test_session_auth`), senhas criptografadas em hash seguro e registro à prova de adulteração na `AuditChain`.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Login com JWT de Sessão Curta e Proteção de Segredos (Priority: P1) 🎯 MVP

Como operador do sistema hospitalar (Suporte N1, Analista de Redes ou Gestor de TI),  
Quero me autenticar via endpoint `/api/auth/login` utilizando credenciais corporativas e receber um token JWT de sessão de curta duração (RFC 7519),  
Para acessar exclusivamente as funções autorizadas para meu perfil sem que segredos permanentes do servidor sejam transmitidos ao meu cliente.

**Why this priority**: É o alicerce de identidade do RF07 e elimina a exposição desprotegida da API.

**Independent Test**: Testado em `tests/test_session_auth.py::TestFluxoLoginESessaoJWT` emitindo tokens válidos, validando tempo de expiração e verificando que a chave permanente do servidor (`OPENROUTER_API_KEY`) nunca é retornada no corpo ou headers.

**Acceptance Scenarios**:
1. **Given** credenciais válidas cadastradas, **When** enviadas para `POST /api/auth/login`, **Then** o sistema retorna HTTP 200 com `access_token` JWT (HS256), `token_type: "bearer"`, `expires_in: 3600`, `usuario` e `papel`.
2. **Given** a resposta de autenticação, **When** inspecionada, **Then** nenhuma chave permanente do servidor (`OPENROUTER_API_KEY`, senhas de banco) está presente.
3. **Given** um token JWT expirado ou com assinatura adulterada, **When** apresentado a uma rota protegida, **Then** o sistema recusa a requisição com HTTP 401 (`Autenticação necessária.`).
4. **Given** um operador autenticado, **When** requisitar `GET /api/auth/me`, **Then** recebe os dados da sua identidade e papel atual.
5. **Given** um operador autenticado, **When** requisitar `POST /api/auth/logout`, **Then** a sessão é encerrada com registro na `AuditChain`.

---

### User Story 2 — Controle de Acesso Baseado em Papéis (RBAC) e Matriz de Permissões (Priority: P1)

Como encarregado de segurança e conformidade hospitalar,  
Quero que cada rota do SIGMA e do núcleo de engenharia aplique a dependência `exige_papel(papel_minimo)`,  
Para assegurar estrita segregação de funções conforme a matriz do `README.md`.

**Why this priority**: Garante o princípio do menor privilégio e impede elevação de privilégios entre operadores e gestores.

**Independent Test**: Testado exaustivamente em `tests/test_session_auth.py::TestMatrizPermissoesRBAC` para todas as linhas da matriz de permissões com 3 perfis e requisições sem token (45 combinações testadas).

**Acceptance Scenarios**:
1. **Given** qualquer requisição sem token Bearer, **When** submetida a qualquer endpoint da matriz, **Then** recebe HTTP 401.
2. **Given** um usuário com perfil `suporte_n1` (nível 1):
   - Acesso permitido (HTTP 200) a `GET /api/status`, `GET /api/alertas` e `POST /api/alertas`;
   - Acesso proibido (HTTP 403) a `GET /api/pacotes`, `GET /api/incidentes`, `/api/eng/*`, relatórios e gerência.
3. **Given** um usuário com perfil `analista_redes` (nível 2):
   - Acesso permitido (HTTP 200) a status, alertas, pacotes, incidentes e operações do núcleo de engenharia (`/api/eng/probe`, `/api/eng/slo/avaliar`, `/api/eng/incidentes/metricas`, `/api/eng/anomalias`);
   - Acesso proibido (HTTP 403) a `GET /api/relatorios`, `GET/POST /api/usuarios`, `POST /api/chaves/rotacao`, `GET /api/n8n/acesso` e `/api/eng/auditoria/verificar`.
4. **Given** um usuário com perfil `gestor_ti` (nível 3):
   - Acesso permitido (HTTP 200) a 100% dos endpoints do sistema, incluindo auditoria e gerência.

---

### User Story 3 — Contenção de Força Bruta e Rastreabilidade na AuditChain (Priority: P1)

Como analista do SOC hospitalar,  
Quero que sucessivas tentativas inválidas de login sejam bloqueadas e que todos os eventos de autenticação sejam gravados na `AuditChain`,  
Para mitigar ataques de adivinhação de senhas e garantir integridade forense à prova de adulteração.

**Why this priority**: Requisito explícito da Issue #6 para compliance e prevenção contra força bruta.

**Independent Test**: Testado em `tests/test_session_auth.py::TestRateLimitingEAuditoria` executando 5 tentativas incorretas, confirmando HTTP 429 na 6ª tentativa, e verificando a integridade da cadeia de hash com `AuditChain.verificar()`.

**Acceptance Scenarios**:
1. **Given** 5 falhas consecutivas de autenticação para a mesma tupla IP/usuário, **When** ocorrer nova tentativa, **Then** o sistema retorna HTTP 429 (`Limite de requisições excedido.`).
2. **Given** eventos de login com sucesso, falha, bloqueio (lockout) ou logout, **When** ocorrem, **Then** são registrados na trilha de auditoria estruturada com campos `ator`, `acao`, `recurso`, `detalhes` e hash criptográfico encadeado.
3. **Given** a trilha de auditoria resultante, **When** submetida a `AuditChain.verificar()`, **Then** a integridade é confirmada (`integra=True, primeira_invalida=None`).

---

## Matriz Oficial de Permissões RBAC (README.md)

| Linha / Recurso | Endpoint | Suporte N1 | Analista de Redes | Gestor de TI |
|---|---|:---:|:---:|:---:|
| Ver alertas e status da rede | `GET /api/status`, `GET /api/alertas` | Sim (200) | Sim (200) | Sim (200) |
| Usar o chat com a IA | `POST /api/alertas` | Sim (200) | Sim (200) | Sim (200) |
| Ver histórico e detalhes de pacotes | `GET /api/pacotes`, `GET /api/incidentes` | Não (403) | Sim (200) | Sim (200) |
| Operações de Engenharia (Sonda/SLO/Métricas/Anomalias) | `/api/eng/probe`, `/slo/avaliar`, `/incidentes/metricas`, `/anomalias` | Não (403) | Sim (200) | Sim (200) |
| Ver relatórios gerenciais | `GET /api/relatorios` | Não (403) | Não (403) | Sim (200) |
| Gerenciar usuários e chaves | `GET/POST /api/usuarios`, `POST /api/chaves/rotacao` | Não (403) | Não (403) | Sim (200) |
| Acessar o n8n (VLAN/VPN) | `GET /api/n8n/acesso` | Não (403) | Não (403) | Sim (200) |
| Verificar integridade da auditoria | `GET /api/eng/auditoria/verificar` | Não (403) | Não (403) | Sim (200) |

---

## Edge Cases

1. **Tentativas com Senhas Vazias ou Inválidas**: Pydantic valida os limites mínimos e máximos e rejeita requisições malformadas com 422 antes do processamento.
2. **Token com Algoritmo Incompatível**: Assinaturas que tentarem utilizar algoritmos `none` ou chaves assimétricas não configuradas são rejeitadas com 401.
3. **Relógio Fora de Sincronia**: O campo `exp` é validado em segundos UTC de acordo com o padrão RFC 7519.
4. **Isolamento de Testes Unitários Anteriores**: Testes legados de conformidade CORS/erros públicos (K05/K06) continuam operando normalmente via fallback controlado em `conftest.py`, sem exigir adaptação dos mocks originais.
