# Feature Specification: Eliminar Respostas 2xx sem Efeito nas Rotas da API (#57)

**Feature Branch**: `fix/57-rotas-sem-efeito`  
**Created**: 2026-11-07  
**Status**: Concluído / Pronto para Revisão  
**Input**: Issue #57 — Rotas da API que respondem sucesso (HTTP 200) sem realizar a ação ou com dados fictícios fixos.

---

## Contexto e Escopo

Diversas rotas definidas na matriz RBAC original (`backend/main.py`) respondiam HTTP 200 com payloads estáticos que simulavam efeitos inexistentes ou mascaravam ausência de persistência:
- `POST /api/alertas`: respondia `status: "Incidente Registrado"`, embora a rota apenas consulte o provedor de IA após anonimização e não grave registro na tabela `incidentes` (que exige `alvo_id` e nasce de medição);
- `POST /api/chaves/rotacao`: respondia `200 {"status": "chaves_rotacionadas"}` sem rotacionar qualquer credencial (escopo planejado na #23);
- `GET /api/n8n/acesso`: respondia `200 {"status": "autorizado_vlan_gerencia", "url": "http://n8n-internal.hospital:5678"}` sem validar rede/VLAN e com endereço fictício fixo;
- `GET /api/alertas`, `GET /api/pacotes` e `GET /api/relatorios`: respondiam `200` com listas vazias fixas (`[]`), indistinguíveis de consultas reais sem registros (relatórios pertencem à #16);
- `GET /api/incidentes`: sem banco configurado (`operational_store is None`), devolvia `200 {"incidentes": []}` em vez de `503`, divergindo de `routers/operational.py`.

`GET /api/status` permanece registrado como débito técnico conhecido (responde `"operacional"` sem sondar dependências).

---

## Decisões de Contrato

| Rota | Antes | Depois (#57) |
|---|---|---|
| `POST /api/alertas` | `200 {"status": "Incidente Registrado", ...}` | `200 {"status": "Diagnóstico gerado", "dados_enviados_nuvem": ..., "diagnostico_ia": ...}` |
| `POST /api/chaves/rotacao` | `200 {"status": "chaves_rotacionadas"}` | `501 {"detail": "Recurso ainda não disponível."}` |
| `GET /api/alertas` | `200 {"alertas": []}` | `501 {"detail": "Recurso ainda não disponível."}` |
| `GET /api/pacotes` | `200 {"pacotes": []}` | `501 {"detail": "Recurso ainda não disponível."}` |
| `GET /api/relatorios` | `200 {"relatorios": []}` | `501 {"detail": "Recurso ainda não disponível."}` |
| `GET /api/incidentes` (sem banco) | `200 {"incidentes": []}` | `503 {"detail": "Erro interno do servidor."}` (via `HTTPException(503)`) |
| `GET /api/n8n/acesso` | `200 {"status": "autorizado_vlan_gerencia", "url": "http://n8n-internal.hospital:5678"}` | Sem `SIGMA_N8N_URL`: `501 {"detail": "Recurso ainda não disponível."}`<br>Com `SIGMA_N8N_URL` válida (`http`/`https`, sem credenciais): `200 {"url": "<SIGMA_N8N_URL>"}`<br>Com `SIGMA_N8N_URL` inválida ou com credenciais embutidas: `503` |

No painel (`frontend/src/api.js`), `ApiError` mapeia o código `501` para `'Recurso ainda não disponível.'`.

---

## Critérios de Aceite e Verificação

1. **Nenhuma rota não implementada responde 2xx:** verificado em `backend/tests/test_session_auth.py::TestRotasSemEfeitoFalso`, conferindo status `501` e corpo exato `{"detail": "Recurso ainda não disponível."}`.
2. **Matriz RBAC preservada (401 / 403 / status esperado):** verificado em `backend/tests/test_session_auth.py::TestMatrizPermissoesRBAC` para todas as 15 rotas e 3 perfis.
3. **Validação estrita de `SIGMA_N8N_URL`:** recusa esquemas fora de `http`/`https`, ausência de host, portas inválidas, espaços e credenciais embutidas (`user:pass@`), sem vazar o valor no corpo ou nos logs.
4. **Contrato de `POST /api/alertas` e aceite HTTP (K10):** verificado em `test_provider.py`, `test_config.py`, `test_fail_closed.py`, `test_public_errors.py` e `scripts/validate_api_acceptance.py`.
5. **Mapeamento de 501 no frontend:** verificado via Vitest em `frontend/src/stream.test.js`.

