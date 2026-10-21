"""Testes de conformidade fail-closed e auditoria para o RF05."""

import importlib
import sys
from unittest.mock import AsyncMock, Mock

import httpx2 as httpx
import pytest
from fastapi.testclient import TestClient

from sanitizer import (
    SanitizationError,
    SanitizationResidualError,
    anonimizar_dados,
    sanitizar_texto,
)

FAKE_KEY = "fake-key-for-fail-closed-tests"
SUCCESS_PAYLOAD = {"choices": [{"message": {"content": "Diagnóstico de teste"}}]}


@pytest.fixture
def api(monkeypatch, legacy_identity):
    monkeypatch.setenv("OPENROUTER_API_KEY", FAKE_KEY)
    monkeypatch.setenv("SIGMA_LLM_MODEL", "test-provider/test-model")
    monkeypatch.setenv("SIGMA_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")

    previous = sys.modules.pop("main", None)
    module = importlib.import_module("main")
    legacy_identity(module)
    provider_handler = AsyncMock(return_value=httpx.Response(200, json=SUCCESS_PAYLOAD))

    def client_factory():
        return httpx.AsyncClient(
            transport=httpx.MockTransport(provider_handler),
            timeout=httpx.Timeout(module.IA_TIMEOUT_SECONDS),
        )

    monkeypatch.setattr(module, "create_provider_client", client_factory)

    try:
        with TestClient(module.app) as client:
            yield module, client, provider_handler
    finally:
        sys.modules.pop("main", None)
        if previous is not None:
            sys.modules["main"] = previous


class TestFailClosedSanitizacao:
    """Garante que qualquer falha na anonimização impede chamadas externas à IA."""

    def test_falha_injetada_no_anonimizador_impede_chamada_externa(self, api, monkeypatch):
        module, client, provider_handler = api
        alerta = {
            "equipamento": "sw-core-01",
            "ip_origem": "192.168.1.10",
            "descricao_erro": "Falha na interface eth0",
        }

        # Simula erro fatal no módulo de anonimização (injeção de falha)
        falha_injetada = Mock(side_effect=RuntimeError("Erro simulado durante a sanitização"))
        monkeypatch.setattr(module, "anonimizar_dados", falha_injetada)

        response = client.post(
            "/api/alertas",
            json=alerta,
            headers={"Origin": "http://localhost:5173"},
        )

        # O endpoint não pode ter feito nenhuma requisição externa ao provedor de IA
        provider_handler.assert_not_called()
        falha_injetada.assert_called_once()
        # Resposta deve ser tratada com segurança
        assert response.status_code == 500

    def test_deteccao_residual_aciona_fail_closed_e_auditoria(self, caplog):
        # Quando há resíduo detectado na saída da segunda passada, dispara SanitizationResidualError
        import sanitizer

        # Força detecção residual injetando um detector que encontra PII residual
        monkeypatch_fun = pytest.MonkeyPatch()
        try:
            # Texto contendo resíduo que viola a inspeção final
            texto_com_falha = "Texto de teste"

            # Mock do sanitizar_texto para simular resíduo na segunda passada
            def mock_sanitizar_com_residuo(t):
                return sanitizer.ResultadoSanitizacao(
                    sucesso=False,
                    texto_sanitizado=t,
                    identificadores_removidos=[],
                    residuos=["cpf_residual", "mac_residual"],
                    motivo_bloqueio="Resíduo de CPF e MAC detectado",
                )

            monkeypatch_fun.setattr(sanitizer, "sanitizar_texto", mock_sanitizar_com_residuo)

            with pytest.raises(SanitizationResidualError) as exc_info:
                anonimizar_dados(texto_com_falha)

            assert "bloqueou o envio externo" in str(exc_info.value)
            # Verifica se foi registrado evento na trilha de auditoria
            assert any("AUDIT_PRIVACY" in record.getMessage() for record in caplog.records)
        finally:
            monkeypatch_fun.undo()

    def test_auditoria_indisponivel_mantem_erro_de_sanitizacao(self, monkeypatch):
        import auth
        import sanitizer

        def auditoria_indisponivel():
            raise RuntimeError("Auditoria indisponível.")

        monkeypatch.setattr(auth, "obter_auditor", auditoria_indisponivel)
        with pytest.raises(SanitizationError, match="Auditoria de privacidade indisponível"):
            sanitizer.registrar_auditoria_privacidade("sanitization_failed", "teste")

    def test_fluxo_completo_com_dados_sensiveis_sanitiza_e_chama_ia(self, api):
        module, client, provider_handler = api
        alerta = {
            "equipamento": "sw-core-bloco-a",
            "ip_origem": "192.168.1.50",
            "descricao_erro": "Queda de porta no IP 192.168.1.50 aberto por dr.joao",
        }

        response = client.post(
            "/api/alertas",
            json=alerta,
            headers={"Origin": "http://localhost:5173"},
        )

        assert response.status_code == 200
        dados = response.json()
        assert dados["status"] == "Incidente Registrado"

        # Verifica que o prompt enviado para a IA foi devidamente generalizado
        prompt_enviado = dados["dados_enviados_nuvem"]
        assert "192.168.1.50" not in prompt_enviado
        assert "192.168.1.0/24" in prompt_enviado
        assert "dr.joao" not in prompt_enviado
        assert "[USUARIO_MEDICO]" in prompt_enviado
        assert "[SWITCH_REDE]" in prompt_enviado

        # Confirma que a chamada ao provedor foi realizada com dados sanitizados
        provider_handler.assert_called_once()
