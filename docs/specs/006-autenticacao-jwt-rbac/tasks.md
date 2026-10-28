> Atualização 19/10/2026: entrega parcial em correção/revisão. As afirmações de conclusão abaixo são históricas e não equivalem ao aceite integral. Consulte [a revisão da sprint](../011-recuperacao-sprint/evidencias.md).

# Tasks: Autenticação e Perfis (RF07): Login com JWT de Sessão e RBAC #6

**Feature**: `006-autenticacao-jwt-rbac`  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)  
**Status**: Concluído (100%)

---

## Checklist de Tarefas

### Fase 1: Arquitetura Criptográfica e Modelagem de Dados
- [x] **T01**: Criar `auth.py` com implementação segura de hashing de senhas via PBKDF2-HMAC-SHA256 (100.000 iterações, salt criptográfico de 16 bytes).
- [x] **T02**: Implementar codificador e decodificador de JWT RFC 7519 em Python puro (HS256) com tempo de expiração (`iat`, `exp`, `jti`, `sub`, `papel`) e verificação de integridade em tempo constante.
- [x] **T03**: Definir hierarquia de papéis RBAC idêntica ao `approvals.py` (`suporte_n1: 1`, `analista_redes: 2`, `gestor_ti: 3`).
- [x] **T04**: Implementar repositório de usuários em memória compatível com PostgreSQL (`UsuarioRepository`) pré-carregado com usuários de teste padrão.
- [x] **T05**: Implementar `LoginRateLimiter` com bloqueio temporário de 15 minutos após 5 falhas consecutivas para a tupla IP/usuário.
- [x] **T06**: Criar helper `obter_auditor` para integração dinâmica com a `AuditChain` do núcleo de engenharia.
- [x] **T07**: Desenvolver dependências FastAPI `obter_usuario_atual` e factory `exige_papel(papel_minimo)`.

### Fase 2: Roteador de Autenticação e Integração ao Sistema
- [x] **T08**: Criar `routers/__init__.py` e `routers/auth.py` herdados do Sentinel Vigilark.
- [x] **T09**: Implementar rota `POST /api/auth/login` retornando token de sessão JWT sem expor segredos permanentes do servidor.
- [x] **T10**: Implementar rota `GET /api/auth/me` para consulta do perfil da sessão ativa.
- [x] **T11**: Implementar rota `POST /api/auth/logout` com registro formal na `AuditChain`.
- [x] **T12**: Atualizar `main.py` registrando `auth_router` e `eng_router`.
- [x] **T13**: Aplicar `Depends(exige_papel("suporte_n1"))` na rota `POST /api/alertas`.
- [x] **T14**: Implementar rotas representativas da matriz do `README.md` (`/api/status`, `/api/alertas`, `/api/pacotes`, `/api/incidentes`, `/api/relatorios`, `/api/usuarios`, `/api/chaves/rotacao`, `/api/n8n/acesso`).
- [x] **T15**: Proteger todas as rotas `/api/eng/*` em `engenharia/sigma_eng/api.py` com `exige_papel("analista_redes")` para operações e `exige_papel("gestor_ti")` para auditoria.

### Fase 3: Trilha de Auditoria e Ajuste do Núcleo
- [x] **T16**: Corrigir avaliação de verdade booleana de `AuditChain` (`__bool__ = True`) em `engenharia/sigma_eng/audit_chain.py` para evitar armadilha de `__len__ == 0`.
- [x] **T17**: Registrar eventos `auth.login.success`, `auth.login.failed`, `auth.login.locked` e `auth.logout` na `AuditChain`.

### Fase 4: Testes Automatizados e Cobertura Completa
- [x] **T18**: Criar `tests/conftest.py` com fixture para isolamento de ambiente e compatibilidade de testes unitários anteriores.
- [x] **T19**: Criar `tests/test_session_auth.py` com 67 testes automatizados cobrindo:
  - Hashing de senhas e diversidade de salts;
  - Ciclo de vida de tokens de sessão, expiração e adulteração de assinatura;
  - Contenção de força bruta (HTTP 429) e integridade da `AuditChain`;
  - Matriz completa de permissões (15 rotas x 3 perfis + requisições sem token).
- [x] **T20**: Ajustar invocação de subprocesso em `tests/test_config.py` para compatibilidade com Python 3.14 no Windows.
- [x] **T21**: Tornar `test_executor_real_sem_shell` em `engenharia/tests/test_runbooks.py` multiplataforma (suportando Windows e Linux).
- [x] **T22**: Executar bateria de regressão: 280 testes em `tests/` e 54 testes em `engenharia/tests/` aprovados com 100% de sucesso.

### Fase 5: Documentação no Padrão Spec-Kit
- [x] **T23**: Atualizar documento de pendências `engenharia/docs/05-seguranca-e-pendencias.md` marcando Bloqueador B9 e risco de `/api/eng/*` como resolvidos.
- [x] **T24**: Gerar `docs/specs/006-autenticacao-jwt-rbac/spec.md`.
- [x] **T25**: Gerar `docs/specs/006-autenticacao-jwt-rbac/plan.md`.
- [x] **T26**: Gerar `docs/specs/006-autenticacao-jwt-rbac/tasks.md`.
- [x] **T27**: Gerar `docs/specs/006-autenticacao-jwt-rbac/registro-issue.md`.
- [x] **T28**: Gerar `docs/specs/006-autenticacao-jwt-rbac/evidencias.md`.
