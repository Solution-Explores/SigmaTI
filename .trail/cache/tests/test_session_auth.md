# tests/test_session_auth.py

- auth_app · function · L28-L59 — def auth_app(monkeypatch, tmp_path)
- client_factory · function · L45-L49 — def client_factory()
- TestHashingESenhas · class · L62-L75 — class TestHashingESenhas
- test_hash_gera_salts_unicos · method · L65-L71 — def test_hash_gera_salts_unicos(self)
- test_verificar_senha_formato_invalido · method · L73-L75 — def test_verificar_senha_formato_invalido(self)
- TestFluxoLoginESessaoJWT · class · L78-L143 — class TestFluxoLoginESessaoJWT
- test_login_sucesso_retorna_jwt_e_nao_expoe_chave_permanente · method · L81-L102 — def test_login_sucesso_retorna_jwt_e_nao_expoe_chave_permanente(self, auth_app)
- test_rota_me_e_logout · method · L104-L125 — def test_rota_me_e_logout(self, auth_app)
- test_token_expirado_rejeitado_com_401 · method · L127-L133 — def test_token_expirado_rejeitado_com_401(self, auth_app)
- test_token_assinatura_invalida_rejeitado_com_401 · method · L135-L143 — def test_token_assinatura_invalida_rejeitado_com_401(self, auth_app)
- TestRateLimitingEAuditoria · class · L146-L167 — class TestRateLimitingEAuditoria
- test_bloqueio_apos_5_tentativas_e_registro_na_auditchain · method · L149-L167 — def test_bloqueio_apos_5_tentativas_e_registro_na_auditchain(self, auth_app)
- TestMatrizPermissoesRBAC · class · L170-L253 — class TestMatrizPermissoesRBAC
- _fazer_requisicao · method · L204-L210 — def _fazer_requisicao(self, client, metodo: str, caminho: str, payload: dict | list | None, headers: dict | None = None)
- test_requisicao_sem_token_retorna_401 · method · L213-L216 — def test_requisicao_sem_token_retorna_401(self, auth_app, metodo, caminho, payload, papel_minimo)
- test_matriz_perfil_suporte_n1 · method · L219-L229 — def test_matriz_perfil_suporte_n1(self, auth_app, metodo, caminho, payload, papel_minimo)
- test_matriz_perfil_analista_redes · method · L232-L242 — def test_matriz_perfil_analista_redes(self, auth_app, metodo, caminho, payload, papel_minimo)
- test_matriz_perfil_gestor_ti · method · L245-L253 — def test_matriz_perfil_gestor_ti(self, auth_app, metodo, caminho, payload, papel_minimo)
