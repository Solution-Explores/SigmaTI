# tests/test_fail_closed.py

- api · function · L23-L47 — def api(monkeypatch)
- client_factory · function · L33-L37 — def client_factory()
- TestFailClosedSanitizacao · class · L50-L135 — class TestFailClosedSanitizacao
- test_falha_injetada_no_anonimizador_impede_chamada_externa · method · L53-L75 — def test_falha_injetada_no_anonimizador_impede_chamada_externa(self, api, monkeypatch)
- test_deteccao_residual_aciona_fail_closed_e_auditoria · method · L77-L106 — def test_deteccao_residual_aciona_fail_closed_e_auditoria(self, caplog): # Quando há resíduo detectado na saída da segunda passada, dispara SanitizationResidualError
- mock_sanitizar_com_residuo · function · L88-L95 — def mock_sanitizar_com_residuo(t)
- test_fluxo_completo_com_dados_sensiveis_sanitiza_e_chama_ia · method · L108-L135 — def test_fluxo_completo_com_dados_sensiveis_sanitiza_e_chama_ia(self, api)
