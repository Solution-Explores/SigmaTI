"""K06: política HTTP real com entradas e falhas inteiramente fictícias."""

import asyncio
import importlib
import sys
from unittest.mock import AsyncMock, Mock

from fastapi import HTTPException
from fastapi.testclient import TestClient
import httpx2 as httpx
import pytest

from api_errors import PublicErrorBoundary


ORIGINS = ("http://localhost:5173", "https://panel.example")
PRIVATE = "fake-private-detail-do-not-disclose"
KEY = "fake-api-key-only-for-tests"
ALERT = {"equipamento": "Switch fictício", "ip_origem": "192.0.2.10", "descricao_erro": "Falha em 192.0.2.10"}


@pytest.fixture
def api(monkeypatch, legacy_identity):
    monkeypatch.setenv("OPENROUTER_API_KEY", KEY)
    monkeypatch.setenv("SIGMA_LLM_MODEL", "test/model")
    monkeypatch.setenv("SIGMA_CORS_ORIGINS", ",".join(ORIGINS))
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    previous = sys.modules.pop("main", None)
    module = importlib.import_module("main")
    legacy_identity(module)
    provider = AsyncMock(return_value=httpx.Response(
        200, request=httpx.Request("POST", module.OPENROUTER_URL),
        json={"choices": [{"message": {"content": "Diagnóstico fictício"}}]},
    ))
    fake = Mock(post=provider)
    module.app.dependency_overrides[module.get_provider_client] = lambda: fake
    try:
        with TestClient(module.app) as client:
            yield module, client, provider
    finally:
        sys.modules.pop("main", None)
        if previous is not None:
            sys.modules["main"] = previous


def assert_safe(response, status, message, caplog):
    assert response.status_code == status
    assert response.json() == {"detail": message}
    assert response.headers["content-type"] == "application/json"
    for value in (PRIVATE, KEY, "Traceback", "Authorization", "192.0.2.10"):
        assert value not in response.text + caplog.text
    for record in caplog.records:
        if record.name == "api_errors":
            assert record.exc_info is None
            assert "category=" in record.getMessage()
            assert "exception=" in record.getMessage()
            assert "status=" in record.getMessage()


@pytest.mark.parametrize("origin", ORIGINS)
def test_allowed_origins_can_preflight_and_post(api, origin):
    _, client, provider = api
    preflight = client.options("/api/alertas", headers={
        "Origin": origin, "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    })
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == origin
    assert preflight.headers["access-control-allow-methods"] == "GET, POST, PATCH"
    assert "*" not in preflight.headers["access-control-allow-headers"]
    assert "access-control-allow-credentials" not in preflight.headers
    provider.assert_not_awaited()
    response = client.post("/api/alertas", json=ALERT, headers={"Origin": origin})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert "origin" in response.headers["vary"].lower()
    assert "access-control-allow-credentials" not in response.headers
    assert response.json()["diagnostico_ia"] == "Diagnóstico fictício"
    provider.assert_awaited_once()


@pytest.mark.parametrize("origin", [
    "https://untrusted.example", "null", "", "http://localhost:51730",
    "https://localhost:5173", "http://localhost:5173/", "http://localhost:5173.evil.example",
    "http://user@localhost:5173", "http://localhost:5173 https://untrusted.example",
])
@pytest.mark.parametrize("content_type", ["application/json", "text/plain", "application/x-www-form-urlencoded"])
def test_disallowed_simple_and_json_requests_are_rejected_before_route(api, monkeypatch, caplog, origin, content_type):
    module, client, provider = api
    anonymize = Mock(side_effect=AssertionError("Route must not execute"))
    monkeypatch.setattr(module, "anonimizar_dados", anonymize)
    response = client.post(
        "/api/alertas", content=PRIVATE,
        headers={"Origin": origin, "Content-Type": content_type},
    )
    assert_safe(response, 403, "Requisição não permitida.", caplog)
    assert "access-control-allow-origin" not in response.headers
    assert "access-control-allow-credentials" not in response.headers
    assert response.headers["vary"] == "Origin"
    provider.assert_not_awaited()
    anonymize.assert_not_called()


@pytest.mark.parametrize("origins", [(ORIGINS[0], "https://untrusted.example"), (ORIGINS[0], ORIGINS[0])])
@pytest.mark.parametrize("method", ["POST", "OPTIONS"])
def test_duplicate_origins_fail_closed(api, caplog, origins, method):
    _, client, provider = api
    response = client.request(method, "/api/alertas", headers=[
        ("Origin", value) for value in origins
    ] + [("Access-Control-Request-Method", "POST")], json=ALERT)
    assert_safe(response, 403, "Requisição não permitida.", caplog)
    assert "access-control-allow-origin" not in response.headers
    provider.assert_not_awaited()


@pytest.mark.parametrize("headers", [
    {"Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"},
    {"Origin": "null", "Access-Control-Request-Method": "POST"},
    {"Origin": "", "Access-Control-Request-Method": "POST"},
    {"Origin": ORIGINS[0], "Access-Control-Request-Method": "DELETE"},
    {"Origin": ORIGINS[0], "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "X-Secret-" + PRIVATE},
    {"Origin": ORIGINS[0], "Access-Control-Request-Method": "POST", "Access-Control-Request-Private-Network": "true"},
])
def test_rejected_preflights_are_generic(api, caplog, headers):
    _, client, provider = api
    response = client.options("/api/alertas", headers=headers)
    assert_safe(response, 400, "Requisição inválida.", caplog)
    if headers["Origin"] in ORIGINS:
        assert response.headers["access-control-allow-origin"] == headers["Origin"]
    else:
        assert "access-control-allow-origin" not in response.headers
    assert "x-secret" not in response.headers.get("access-control-allow-headers", "").lower()
    assert "access-control-allow-credentials" not in response.headers
    provider.assert_not_awaited()


def test_service_request_without_origin_still_works(api):
    _, client, provider = api
    response = client.post("/api/alertas", json=ALERT)
    assert response.status_code == 200
    assert response.json()["diagnostico_ia"] == "Diagnóstico fictício"
    assert "access-control-allow-origin" not in response.headers
    assert "access-control-allow-credentials" not in response.headers
    provider.assert_awaited_once()


@pytest.mark.parametrize("payload", [
    {}, {**ALERT, "descricao_erro": {"private": PRIVATE, "key": KEY}},
    [PRIVATE, KEY], {"equipamento": PRIVATE, "ip_origem": KEY},
])
def test_validation_errors_do_not_reflect_input(api, caplog, payload):
    _, client, provider = api
    response = client.post("/api/alertas", json=payload, headers={"Origin": ORIGINS[0]})
    assert_safe(response, 422, "Dados da requisição inválidos.", caplog)
    assert response.headers["access-control-allow-origin"] == ORIGINS[0]
    provider.assert_not_awaited()


def test_invalid_json_does_not_reflect_body(api, caplog):
    _, client, provider = api
    response = client.post("/api/alertas", content=f'{{"{PRIVATE}":"{KEY}"', headers={
        "Origin": ORIGINS[0], "Content-Type": "application/json",
    })
    assert_safe(response, 422, "Dados da requisição inválidos.", caplog)
    assert response.headers["access-control-allow-origin"] == ORIGINS[0]
    provider.assert_not_awaited()


@pytest.mark.parametrize("method,path,status,message", [
    ("GET", "/does-not-exist", 404, "Recurso não encontrado."),
    ("DELETE", "/api/alertas", 405, "Método não permitido."),
    ("OPTIONS", "/api/alertas", 405, "Método não permitido."),
])
def test_router_errors_use_public_contract(api, caplog, method, path, status, message):
    _, client, provider = api
    response = client.request(method, path, headers={"Origin": ORIGINS[0]})
    assert_safe(response, status, message, caplog)
    assert response.headers["access-control-allow-origin"] == ORIGINS[0]
    if status == 405:
        assert response.headers["allow"] == "POST"
    provider.assert_not_awaited()


@pytest.mark.parametrize("status,message", [
    (400, "Requisição inválida."), (401, "Autenticação necessária."),
    (403, "Requisição não permitida."), (429, "Limite de requisições excedido."),
    (418, "Requisição inválida."), (503, "Erro interno do servidor."),
])
def test_http_exception_details_and_arbitrary_headers_are_private(api, caplog, status, message):
    module, client, provider = api

    async def fail():
        raise HTTPException(status_code=status, detail={"secret": PRIVATE, "key": KEY}, headers={"X-Private": PRIVATE})

    module.app.dependency_overrides[module.get_provider_client] = fail
    response = client.post("/api/alertas", json=ALERT, headers={"Origin": ORIGINS[0]})
    assert_safe(response, status, message, caplog)
    assert "x-private" not in response.headers
    assert response.headers["access-control-allow-origin"] == ORIGINS[0]
    provider.assert_not_awaited()


def test_internal_error_is_generic_with_cors_and_safe_log(api, monkeypatch, caplog):
    module, client, provider = api
    monkeypatch.setattr(module, "anonimizar_dados", Mock(side_effect=RuntimeError(f"{PRIVATE} {KEY}")))
    response = client.post("/api/alertas", json=ALERT, headers={"Origin": ORIGINS[0]})
    assert_safe(response, 500, "Erro interno do servidor.", caplog)
    assert response.headers["access-control-allow-origin"] == ORIGINS[0]
    assert "exception=RuntimeError" in caplog.text
    provider.assert_not_awaited()


def test_provider_failure_preserves_k05_contract_and_cors(api, caplog):
    _, client, provider = api
    provider.side_effect = httpx.ReadTimeout(f"{PRIVATE} {KEY}")
    response = client.post("/api/alertas", json=ALERT, headers={"Origin": ORIGINS[0]})
    assert response.status_code == 200
    assert set(response.json()) == {"status", "dados_enviados_nuvem", "diagnostico_ia"}
    assert response.json()["diagnostico_ia"] == "Diagnóstico de IA indisponível no momento. Tente novamente mais tarde."
    assert response.headers["access-control-allow-origin"] == ORIGINS[0]
    for secret in (PRIVATE, KEY):
        assert secret not in response.text + caplog.text
    provider.assert_awaited_once()


def test_openapi_describes_public_error_body(api):
    _, client, provider = api
    schema = client.get("/openapi.json").json()
    for status in ("403", "422", "500"):
        error_schema = schema["paths"]["/api/alertas"]["post"]["responses"][status]["content"]["application/json"]["schema"]
        assert error_schema == {"$ref": "#/components/schemas/PublicError"}
    assert schema["components"]["schemas"]["PublicError"]["required"] == ["detail"]
    provider.assert_not_awaited()


def test_error_boundary_propagates_external_cancellation():
    async def fail(scope, receive, send):
        raise asyncio.CancelledError()

    async def run():
        with pytest.raises(asyncio.CancelledError):
            await PublicErrorBoundary(fail)({"type": "http"}, AsyncMock(), AsyncMock())
    asyncio.run(run())


def test_error_boundary_never_starts_second_response():
    async def fail(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        raise RuntimeError(PRIVATE)

    async def run():
        send = AsyncMock()
        with pytest.raises(RuntimeError):
            await PublicErrorBoundary(fail)({"type": "http"}, AsyncMock(), send)
        send.assert_awaited_once()
    asyncio.run(run())


@pytest.mark.parametrize("origin,expected", [(ORIGINS[0],200),("https://untrusted.example",400)])
@pytest.mark.parametrize("method,path,headers", [
    ("GET","/api/eng/eventos","Authorization,Last-Event-ID"),
    ("PATCH","/api/eng/alvos/synthetic","Authorization,Content-Type"),
])
def test_collection_browser_preflight_reconnect_and_control(api,origin,expected,method,path,headers):
    _,client,provider=api
    response=client.options(path,headers={"Origin":origin,
        "Access-Control-Request-Method":method,"Access-Control-Request-Headers":headers})
    assert response.status_code == expected
    if expected == 200:
        assert response.headers["access-control-allow-origin"] == origin
        assert "last-event-id" in response.headers["access-control-allow-headers"].lower()
    provider.assert_not_awaited()
