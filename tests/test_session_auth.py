"""Testes de autenticação, JWT de sessão e matriz RBAC (RF07 / Issue #6)."""

import importlib
import os
import sys
import tempfile
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
import httpx2 as httpx
import pytest

from auth import (
    criar_token_sessao,
    decodificar_token_sessao,
    hash_senha,
    rate_limiter,
    usuario_repo,
    verificar_senha,
)
from sigma_eng.audit_chain import AuditChain

FAKE_OPENROUTER_KEY = "sk-or-v1-permanent-server-secret-never-expose"
SUCCESS_IA = {"choices": [{"message": {"content": "Diagnóstico validado"}}]}


@pytest.fixture
def auth_app(monkeypatch, tmp_path, temporary_identity):
    audit_file = str(tmp_path / "audit_test.jsonl")
    monkeypatch.setenv("OPENROUTER_API_KEY", FAKE_OPENROUTER_KEY)
    monkeypatch.setenv("SIGMA_LLM_MODEL", "test-provider/test-model")
    monkeypatch.setenv("SIGMA_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("SIGMA_AUDIT_PATH", audit_file)
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")

    # Limpa tentativas de rate limiting acumuladas
    rate_limiter._tentativas.clear()

    previous = sys.modules.pop("main", None)
    module = importlib.import_module("main")

    provider_handler = AsyncMock(return_value=httpx.Response(200, json=SUCCESS_IA))

    def client_factory():
        return httpx.AsyncClient(
            transport=httpx.MockTransport(provider_handler),
            timeout=httpx.Timeout(module.IA_TIMEOUT_SECONDS),
        )

    monkeypatch.setattr(module, "create_provider_client", client_factory)

    try:
        with TestClient(module.app) as client:
            yield client, audit_file
    finally:
        sys.modules.pop("main", None)
        if previous is not None:
            sys.modules["main"] = previous


class TestHashingESenhas:
    """Valida armazenamento seguro de senhas com PBKDF2-HMAC-SHA256."""

    def test_hash_gera_salts_unicos(self):
        h1 = hash_senha("MinhaSenhaForte123")
        h2 = hash_senha("MinhaSenhaForte123")
        assert h1 != h2, "Hashes de mesma senha devem possuir salts criptográficos distintos"
        assert verificar_senha("MinhaSenhaForte123", h1)
        assert verificar_senha("MinhaSenhaForte123", h2)
        assert not verificar_senha("SenhaIncorreta", h1)

    def test_verificar_senha_formato_invalido(self):
        assert not verificar_senha("senha", "formato_invalido_sem_cifrao")
        assert not verificar_senha("senha", "md5$1000$salt$hash")


class TestFluxoLoginESessaoJWT:
    """Valida ciclo de vida do token de sessão JWT e proteção de segredos do servidor."""

    def test_login_sucesso_retorna_jwt_e_nao_expoe_chave_permanente(self, auth_app, temporary_identity):
        client, _ = auth_app
        payload = {"username": "analista.redes", "password": temporary_identity}
        response = client.post("/api/auth/login", json=payload)

        assert response.status_code == 200
        dados = response.json()
        assert "access_token" in dados
        assert dados["token_type"] == "bearer"
        assert dados["expires_in"] > 0
        assert dados["usuario"] == "analista.redes"
        assert dados["papel"] == "analista_redes"

        # Critério de aceite: a chave permanente do servidor NUNCA deve ser devolvida
        assert FAKE_OPENROUTER_KEY not in response.text
        assert "sk-or-" not in response.text

        # Valida que o token retornado é decodificável e contém as claims corretas
        token_claims = decodificar_token_sessao(dados["access_token"])
        assert token_claims["sub"] == "analista.redes"
        assert token_claims["papel"] == "analista_redes"
        assert token_claims["exp"] > token_claims["iat"]

    def test_rota_me_e_logout(self, auth_app, temporary_identity):
        client, audit_file = auth_app
        login_res = client.post("/api/auth/login", json={"username": "suporte.n1", "password": temporary_identity})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # GET /api/auth/me
        me_res = client.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json() == {"usuario": "suporte.n1", "papel": "suporte_n1"}

        # POST /api/auth/logout
        logout_res = client.post("/api/auth/logout", headers=headers)
        assert logout_res.status_code == 200
        assert logout_res.json()["status"] == "sucesso"

        # Verifica registro na trilha de auditoria
        audit = AuditChain(audit_file)
        assert len(audit) >= 2
        acoes = [e["acao"] for e in audit.entradas]
        assert "auth.login.success" in acoes
        assert "auth.logout" in acoes

    def test_token_expirado_rejeitado_com_401(self, auth_app):
        client, _ = auth_app
        # Gera token intencionalmente expirado (expira_em_segundos negativo)
        token_expirado = criar_token_sessao("suporte.n1", "suporte_n1", expira_em_segundos=-60)

        response = client.get("/api/status", headers={"Authorization": f"Bearer {token_expirado}"})
        assert response.status_code == 401

    def test_token_assinatura_invalida_rejeitado_com_401(self, auth_app):
        client, _ = auth_app
        token = criar_token_sessao("suporte.n1", "suporte_n1")
        partes = token.split(".")
        # Altera payload mantendo assinatura original
        token_adulterado = f"{partes[0]}.eyJrZXkiOiJpbnZhbGlkIn0.{partes[2]}"

        response = client.get("/api/status", headers={"Authorization": f"Bearer {token_adulterado}"})
        assert response.status_code == 401


class TestRateLimitingEAuditoria:
    """Valida contenção de força bruta e registro na AuditChain."""

    def test_bloqueio_apos_5_tentativas_e_registro_na_auditchain(self, auth_app):
        client, audit_file = auth_app

        # 5 tentativas incorretas consecutivas
        for i in range(5):
            res = client.post("/api/auth/login", json={"username": "gestor.ti", "password": "SenhaErrada"})
            assert res.status_code == 401

        # 6ª tentativa deve retornar 429 Too Many Requests (Lockout)
        res_bloqueado = client.post("/api/auth/login", json={"username": "gestor.ti", "password": "SenhaErrada"})
        assert res_bloqueado.status_code == 429

        # Verifica se o evento de bloqueio foi gravado na AuditChain
        audit = AuditChain(audit_file)
        ok, idx = audit.verificar()
        assert ok, "A cadeia de hashes da AuditChain deve permanecer íntegra"
        acoes = [e["acao"] for e in audit.entradas]
        assert "auth.login.failed" in acoes
        assert "auth.login.locked" in acoes


class TestMatrizPermissoesRBAC:
    """Valida todas as linhas da matriz de permissões (README / stack-de-tecnologia).

    Perfis:
      - suporte_n1 (nível 1)
      - analista_redes (nível 2)
      - gestor_ti (nível 3)

    Critérios de aceite:
      - 401 sem token (ou token inválido) para cada linha da matriz
      - 403 quando o perfil for insuficiente
      - 200 quando o perfil atender ou superar o requisito
    """

    ROTAS_MATRIZ = [
        # (metodo, caminho, payload, papel_minimo)
        ("GET", "/api/status", None, "suporte_n1"),
        ("GET", "/api/alertas", None, "suporte_n1"),
        ("POST", "/api/alertas", {"equipamento": "sw-core", "ip_origem": "10.0.0.1", "descricao_erro": "queda link"}, "suporte_n1"),
        ("GET", "/api/pacotes", None, "analista_redes"),
        ("GET", "/api/incidentes", None, "analista_redes"),
        ("GET", "/api/relatorios", None, "gestor_ti"),
        ("GET", "/api/usuarios", None, "gestor_ti"),
        ("POST", "/api/usuarios", {"username": "novo.user", "password": "NovaSenha123", "papel": "suporte_n1"}, "gestor_ti"),
        ("POST", "/api/chaves/rotacao", None, "gestor_ti"),
        ("GET", "/api/n8n/acesso", None, "gestor_ti"),
        # Rotas do Núcleo de Engenharia (/api/eng/*)
        ("POST", "/api/eng/probe", {"host": "127.0.0.1", "port": 80, "kind": "tcp", "count": 1}, "analista_redes"),
        ("POST", "/api/eng/slo/avaliar", {"alvo_pct": 99.9, "janela_dias": 30, "indisponibilidades": []}, "analista_redes"),
        ("POST", "/api/eng/incidentes/metricas", [], "analista_redes"),
        ("POST", "/api/eng/anomalias", {"serie": [1.0, 1.2, 1.1, 1.3], "metodo": "ewma"}, "analista_redes"),
        ("GET", "/api/eng/auditoria/verificar", None, "gestor_ti"),
    ]

    def _fazer_requisicao(self, client, metodo: str, caminho: str, payload: dict | list | None, headers: dict | None = None):
        headers = headers or {}
        if metodo == "GET":
            return client.get(caminho, headers=headers)
        elif metodo == "POST":
            return client.post(caminho, json=payload if payload is not None else {}, headers=headers)
        raise ValueError(f"Método não suportado: {metodo}")

    @pytest.mark.parametrize("metodo,caminho,payload,papel_minimo", ROTAS_MATRIZ)
    def test_requisicao_sem_token_retorna_401(self, auth_app, metodo, caminho, payload, papel_minimo):
        client, _ = auth_app
        res = self._fazer_requisicao(client, metodo, caminho, payload, headers=None)
        assert res.status_code == 401, f"{metodo} {caminho} deve recusar requisição sem token com 401"

    @pytest.mark.parametrize("metodo,caminho,payload,papel_minimo", ROTAS_MATRIZ)
    def test_matriz_perfil_suporte_n1(self, auth_app, metodo, caminho, payload, papel_minimo):
        client, _ = auth_app
        token_n1 = criar_token_sessao("suporte.n1", "suporte_n1")
        headers = {"Authorization": f"Bearer {token_n1}"}

        res = self._fazer_requisicao(client, metodo, caminho, payload, headers=headers)

        if papel_minimo == "suporte_n1":
            assert res.status_code == 200, f"Suporte N1 deve ter acesso a {metodo} {caminho}"
        else:
            assert res.status_code == 403, f"Suporte N1 deve receber 403 em {metodo} {caminho} (exige {papel_minimo})"

    @pytest.mark.parametrize("metodo,caminho,payload,papel_minimo", ROTAS_MATRIZ)
    def test_matriz_perfil_analista_redes(self, auth_app, metodo, caminho, payload, papel_minimo):
        client, _ = auth_app
        token_analista = criar_token_sessao("analista.redes", "analista_redes")
        headers = {"Authorization": f"Bearer {token_analista}"}

        res = self._fazer_requisicao(client, metodo, caminho, payload, headers=headers)

        if papel_minimo in ("suporte_n1", "analista_redes"):
            assert res.status_code == 200, f"Analista de Redes deve ter acesso a {metodo} {caminho}"
        else:
            assert res.status_code == 403, f"Analista de Redes deve receber 403 em {metodo} {caminho} (exige {papel_minimo})"

    @pytest.mark.parametrize("metodo,caminho,payload,papel_minimo", ROTAS_MATRIZ)
    def test_matriz_perfil_gestor_ti(self, auth_app, metodo, caminho, payload, papel_minimo):
        client, _ = auth_app
        token_gestor = criar_token_sessao("gestor.ti", "gestor_ti")
        headers = {"Authorization": f"Bearer {token_gestor}"}

        res = self._fazer_requisicao(client, metodo, caminho, payload, headers=headers)

        # Gestor de TI tem o nível mais alto (3), deve ter acesso a TODAS as rotas
        assert res.status_code == 200, f"Gestor de TI deve ter acesso irrestrito a {metodo} {caminho}"
