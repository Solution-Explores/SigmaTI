"""K05: provedor simulado; nenhuma chave real ou conexão com a IA."""

import asyncio
import importlib
import json
import logging
import sys
from time import monotonic
from unittest.mock import AsyncMock

import httpx2 as httpx
import pytest
from fastapi.testclient import TestClient


ALERT = {
    "equipamento": "Switch de teste",
    "ip_origem": "192.0.2.10",
    "descricao_erro": "Falha dr.joao no IP 192.0.2.10",
}
FAKE_KEY = "fake-key-only-for-tests"
PRIVATE_DETAIL = "provider-private-detail-do-not-disclose"
SUCCESS = {"choices": [{"message": {"content": "Diagnóstico simulado"}}]}


@pytest.fixture
def module(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", FAKE_KEY)
    monkeypatch.setenv("SIGMA_LLM_MODEL", "test-provider/test-model")
    monkeypatch.setenv("SIGMA_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    previous = sys.modules.pop("main", None)
    app_module = importlib.import_module("main")
    try:
        yield app_module
    finally:
        sys.modules.pop("main", None)
        if previous is not None:
            sys.modules["main"] = previous


@pytest.fixture
def provider(module, monkeypatch):
    handler = AsyncMock(return_value=httpx.Response(200, json=SUCCESS))
    clients = []

    def factory():
        client = httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            timeout=httpx.Timeout(module.IA_TIMEOUT_SECONDS),
        )
        clients.append(client)
        return client

    monkeypatch.setattr(module, "create_provider_client", factory)
    return handler, clients


@pytest.fixture
def authenticated_client(module, provider, monkeypatch, tmp_path):
    """K07: exercita a rota real com login e autenticação habilitada."""
    monkeypatch.setenv("SIGMA_AUTH_ENFORCED", "1")
    monkeypatch.setenv("SIGMA_AUDIT_PATH", str(tmp_path / "audit.jsonl"))
    with TestClient(module.app) as client:
        login = client.post("/api/auth/login", json={
            "username": "suporte.n1", "password": "SenhaN1@123",
        })
        assert login.status_code == 200
        client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield client


def assert_generic(module, response):
    assert response.status_code == 200
    assert set(response.json()) == {"status", "dados_enviados_nuvem", "diagnostico_ia"}
    assert response.json()["status"] == "Incidente Registrado"
    assert response.json()["diagnostico_ia"] == module.IA_UNAVAILABLE
    assert FAKE_KEY not in response.text
    assert PRIVATE_DETAIL not in response.text


def assert_safe_log(caplog, category, status="None"):
    records = [record for record in caplog.records if record.name == "main"]
    assert len(records) == 1
    message = records[0].getMessage()
    assert f"category={category}" in message
    assert f"status={status}" in message
    assert "exception=" in message
    assert "duration_ms=" in message
    for secret in (FAKE_KEY, PRIVATE_DETAIL, ALERT["descricao_erro"], "Authorization", "Bearer"):
        assert secret not in caplog.text
    assert records[0].exc_info is None


def test_success_payload_and_shared_client_lifecycle(module, provider, caplog):
    handler, clients = provider
    with TestClient(module.app) as client:
        first = client.post("/api/alertas", json=ALERT)
        second = client.post("/api/alertas", json=ALERT)
        assert len(clients) == 1
        assert not clients[0].is_closed
        assert module.app.state.provider_client is clients[0]
    assert clients[0].is_closed
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json() == {
        "status": "Incidente Registrado",
        "dados_enviados_nuvem": "Equipamento: [SWITCH_REDE] | Erro: Falha [USUARIO_MEDICO] no IP 192.0.2.0/24. Forneça um diagnóstico de rede curto e direto.",
        "diagnostico_ia": "Diagnóstico simulado",
    }
    assert handler.await_count == 2
    request = handler.await_args.args[0]
    assert str(request.url) == module.OPENROUTER_URL
    assert request.headers["Authorization"] == f"Bearer {FAKE_KEY}"
    payload = json.loads(request.content)
    assert payload["model"] == "test-provider/test-model"
    assert payload["messages"][1]["content"] == first.json()["dados_enviados_nuvem"]
    assert ALERT["ip_origem"] not in request.content.decode()
    assert FAKE_KEY not in first.text
    assert not [r for r in caplog.records if r.name == "main"]


def test_production_client_has_bounded_timeouts_and_no_redirects(module):
    async def run():
        async with module.create_provider_client() as client:
            for phase in ("connect", "read", "write", "pool"):
                assert getattr(client.timeout, phase) == 14.0
            assert not client.follow_redirects
    asyncio.run(run())


@pytest.mark.parametrize("status", [301, 401, 403, 429, 500, 502])
def test_http_errors_are_generic_and_do_not_retry(module, provider, caplog, status):
    handler, _ = provider
    handler.return_value = httpx.Response(
        status,
        json={"error": {"message": f"{PRIVATE_DETAIL} {FAKE_KEY}"}},
        headers={"Location": "https://untrusted.example"},
    )
    with TestClient(module.app) as client:
        response = client.post("/api/alertas", json=ALERT)
    assert_generic(module, response)
    handler.assert_awaited_once()
    assert_safe_log(caplog, "http", str(status))
    assert "exception=HTTPStatusError" in caplog.text


@pytest.mark.parametrize("error_type,category", [
    (httpx.ConnectTimeout, "timeout"),
    (httpx.ReadTimeout, "timeout"),
    (httpx.WriteTimeout, "timeout"),
    (httpx.PoolTimeout, "timeout"),
    (httpx.ConnectError, "transport"),
    (httpx.RemoteProtocolError, "transport"),
    (RuntimeError, "unexpected"),
])
def test_transport_errors_hide_exception_details(module, provider, caplog, error_type, category):
    handler, _ = provider
    handler.side_effect = error_type(f"{PRIVATE_DETAIL} {FAKE_KEY}")
    with TestClient(module.app) as client:
        response = client.post("/api/alertas", json=ALERT)
    assert_generic(module, response)
    handler.assert_awaited_once()
    assert_safe_log(caplog, category)
    assert f"exception={error_type.__name__}" in caplog.text


@pytest.mark.parametrize("body", [
    None, [], "unexpected", {}, {"choices": []}, {"choices": None},
    {"choices": [None]}, {"choices": [{"message": {}}]},
    {"choices": [{"message": {"content": None}}]},
    {"choices": [{"message": {"content": ""}}]},
    {"choices": [{"message": {"content": " \n "}}]},
    {"choices": [{"message": {"content": 123}}]},
    {"choices": [{"message": {"content": ["unexpected"]}}]},
])
def test_malformed_diagnosis_is_generic(module, provider, caplog, body):
    handler, _ = provider
    handler.return_value = httpx.Response(200, content=json.dumps(body))
    with TestClient(module.app) as client:
        response = client.post("/api/alertas", json=ALERT)
    assert_generic(module, response)
    assert_safe_log(caplog, "invalid_response", "200")


def test_invalid_json_is_generic(module, provider, caplog):
    handler, _ = provider
    handler.return_value = httpx.Response(200, text=f"not-json: {PRIVATE_DETAIL} {FAKE_KEY}")
    with TestClient(module.app) as client:
        response = client.post("/api/alertas", json=ALERT)
    assert_generic(module, response)
    assert_safe_log(caplog, "invalid_response", "200")


def test_real_budget_cancels_slow_provider_within_15_seconds(
    module, provider, authenticated_client, caplog,
):
    handler, _ = provider
    cancelled = []

    async def slow(request):
        try:
            await asyncio.sleep(20)
            return httpx.Response(200, json=SUCCESS)
        except asyncio.CancelledError:
            cancelled.append(True)
            raise

    handler.side_effect = slow
    assert module.IA_TIMEOUT_SECONDS == 14.0
    start = monotonic()
    response = authenticated_client.post("/api/alertas", json=ALERT)
    elapsed = monotonic() - start
    assert 14.0 <= elapsed <= 15.0
    assert cancelled == [True]
    assert_generic(module, response)
    assert_safe_log(caplog, "timeout")
    handler.assert_awaited_once()
    print(f"K07 authenticated budget: response in {elapsed:.3f}s; provider cancelled")


@pytest.mark.parametrize("outcome", ["success", "http_error", "timeout", "invalid_json"])
def test_authenticated_alert_reaches_simulated_provider(
    module, provider, authenticated_client, caplog, outcome,
):
    handler, _ = provider
    if outcome == "http_error":
        handler.return_value = httpx.Response(503, text=PRIVATE_DETAIL)
    elif outcome == "timeout":
        handler.side_effect = httpx.ReadTimeout(PRIVATE_DETAIL)
    elif outcome == "invalid_json":
        handler.return_value = httpx.Response(200, text=PRIVATE_DETAIL)

    response = authenticated_client.post("/api/alertas", json=ALERT)
    handler.assert_awaited_once()
    if outcome == "success":
        assert response.status_code == 200
        assert response.json()["diagnostico_ia"] == "Diagnóstico simulado"
        payload = json.loads(handler.await_args.args[0].content)
        assert ALERT["ip_origem"] not in json.dumps(payload)
        assert "dr.joao" not in json.dumps(payload)
    else:
        assert_generic(module, response)
        category, status = {
            "http_error": ("http", "503"),
            "timeout": ("timeout", "None"),
            "invalid_json": ("invalid_response", "200"),
        }[outcome]
        assert_safe_log(caplog, category, status)


@pytest.mark.parametrize("authorization", [None, "", "Bearer invalid-token", "expired"])
def test_unauthenticated_alert_never_calls_provider(
    module, provider, authenticated_client, authorization,
):
    from auth import criar_token_sessao

    if authorization == "expired":
        token = criar_token_sessao("suporte.n1", "suporte_n1", expira_em_segundos=-1)
        authorization = f"Bearer {token}"
    if authorization is None:
        authenticated_client.headers.pop("Authorization")
        headers = {}
    else:
        headers = {"Authorization": authorization}
    response = authenticated_client.post(
        "/api/alertas", json=ALERT, headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Autenticação necessária."}
    provider[0].assert_not_awaited()


def test_continuous_slow_chunks_do_not_reset_total_budget(module, provider, monkeypatch, caplog):
    handler, _ = provider
    closed = []
    monkeypatch.setattr(module, "IA_TIMEOUT_SECONDS", 0.1)

    class SlowStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            while True:
                await asyncio.sleep(0.01)
                yield b" "

        async def aclose(self):
            closed.append(True)

    handler.return_value = httpx.Response(200, stream=SlowStream())
    with TestClient(module.app) as client:
        response = client.post("/api/alertas", json=ALERT)
    assert_generic(module, response)
    assert closed
    assert_safe_log(caplog, "timeout")


def test_pending_provider_does_not_block_another_alert(module, provider):
    handler, _ = provider

    async def run():
        started = asyncio.Event()
        release = asyncio.Event()

        async def respond(request):
            payload = json.loads(request.content)
            if not started.is_set():
                started.set()
                await release.wait()
            return httpx.Response(200, json=SUCCESS)

        handler.side_effect = respond
        async with module.app.router.lifespan_context(module.app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=module.app), base_url="http://testserver"
            ) as client:
                slow = asyncio.create_task(client.post(
                    "/api/alertas", json={**ALERT, "equipamento": "Slow switch"}
                ))
                try:
                    await asyncio.wait_for(started.wait(), timeout=2)
                    fast = await asyncio.wait_for(client.post("/api/alertas", json=ALERT), timeout=2)
                    assert fast.json()["diagnostico_ia"] == "Diagnóstico simulado"
                    assert not slow.done()
                    release.set()
                    result = await asyncio.wait_for(slow, timeout=2)
                    assert result.json()["diagnostico_ia"] == "Diagnóstico simulado"
                finally:
                    release.set()
                    if not slow.done():
                        slow.cancel()
                    await asyncio.gather(slow, return_exceptions=True)
    asyncio.run(run())


def test_external_cancellation_propagates_and_closes_client(module, provider, caplog):
    handler, clients = provider
    cancelled = []

    async def run():
        started = asyncio.Event()

        async def respond(request):
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.append(True)
                raise

        handler.side_effect = respond
        async with module.app.router.lifespan_context(module.app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=module.app), base_url="http://testserver"
            ) as client:
                task = asyncio.create_task(client.post("/api/alertas", json=ALERT))
                try:
                    await asyncio.wait_for(started.wait(), timeout=2)
                    task.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await task
                finally:
                    if not task.done():
                        task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
    asyncio.run(run())
    assert cancelled == [True]
    assert clients[0].is_closed
    assert not [r for r in caplog.records if r.name == "main" and r.levelno >= logging.WARNING]
