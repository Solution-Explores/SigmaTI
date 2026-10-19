# Registro de Análise e Resolução de Issue

## Metadados da Issue
- **Número/Identificador**: Issue #6
- **Título**: Autenticação e perfis (RF07): login com JWT de sessão e RBAC
- **Requisito Associado**: RF07 (Controle de Acesso e Restrição de Rede), RNF07 (Recusa de requisição não autorizada)
- **Bloqueador Relacionado**: B9 (`engenharia/docs/05-seguranca-e-pendencias.md`)
- **Data de Resolução**: 2026-10-18
- **Status**: Resolvido e Validado com Testes Automatizados

---

## 1. Contexto e Problema Identificado

Nenhuma rota do SIGMA possuía mecanismo de autenticação ou autorização. O `README.md` estabelecia três perfis operacionais e uma matriz de permissões para controle de acesso:
- **Suporte N1**: alertas e status da rede; uso do chat com a IA.
- **Analista de Redes**: histórico de pacotes e incidentes; ferramentas do núcleo de engenharia.
- **Gestor de TI**: relatórios gerenciais, gestão de usuários, rotação de chaves e acesso ao n8n via rede de gerência.

Além disso, as rotas `/api/eng/*` portadas do Sentinel Vigilark não tinham proteção, representando um vetor de exploração e impedindo a homologação fora do laboratório de testes.

---

## 2. Proposta Implementada

1. **Herança do Sentinel Vigilark**:
   - Criação de `routers/auth.py` expondo `/api/auth/login`, `/api/auth/logout` e `/api/auth/me`.
   - Emissão de JWT de sessão de curta duração (1 hora) assinado com HMAC-SHA256 (RFC 7519), contendo `sub`, `papel`, `iat`, `exp` e `jti`.
   - Garantia de que a chave permanente do servidor (`OPENROUTER_API_KEY`) nunca é transmitida ao cliente.
2. **Criptografia e Repositório de Usuários**:
   - Módulo `auth.py` com hashing de senhas via PBKDF2-HMAC-SHA256 (100.000 iterações e salt criptográfico individual).
   - Repositório `UsuarioRepository` compatível com PostgreSQL / in-memory.
3. **Controle de Acesso RBAC**:
   - Hierarquia de permissões idêntica ao `approvals.py`: `suporte_n1 (1) < analista_redes (2) < gestor_ti (3)`.
   - Dependência FastAPI `exige_papel(papel_minimo)` aplicada a cada linha da matriz do README e às rotas `/api/eng/*`.
4. **Rate Limiting e AuditChain**:
   - Proteção contra força bruta: limite de 5 tentativas consecutivas com bloqueio temporário (lockout) de 15 minutos (HTTP 429).
   - Gravação de eventos `auth.login.success`, `auth.login.failed`, `auth.login.locked` e `auth.logout` na `AuditChain`.

---

## 3. Critérios de Aceite e Validação

| Critério de Aceite | Status | Evidência de Validação |
|---|---|---|
| HTTP 401 sem token para cada linha da matriz | **Aprovado** | 15 testes em `test_requisicao_sem_token_retorna_401` |
| HTTP 403 com papel insuficiente para cada linha | **Aprovado** | 30 testes em `test_matriz_perfil_suporte_n1` e `test_matriz_perfil_analista_redes` |
| HTTP 200 com papel suficiente | **Aprovado** | 15 testes em `test_matriz_perfil_gestor_ti` |
| Token expira; chave permanente nunca é devolvida | **Aprovado** | `test_token_expirado_rejeitado_com_401` e `test_login_sucesso_retorna_jwt_e_nao_expoe_chave_permanente` |
| Limite de 5 tentativas e trilha na AuditChain | **Aprovado** | `test_bloqueio_apos_5_tentativas_e_registro_na_auditchain` com `AuditChain.verificar()` íntegra |
| Testes automatizados da matriz completa | **Aprovado** | 67 testes em `tests/test_session_auth.py` |

---

## 4. Conclusão

A Issue #6 foi completamente solucionada, encerrando o Bloqueador B9 de segurança e estabelecendo conformidade com os requisitos RF07 e RNF07 do TCC. Todas as 334 asserções de testes do projeto estão verdes (100% de aprovação).
