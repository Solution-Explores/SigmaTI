import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from auth import criar_token_sessao, exige_papel
from sigma_eng import api


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from sigma_eng.audit_chain import AuditChain
    monkeypatch.setenv("SIGMA_AUTH_ENFORCED", "1")
    app = FastAPI()
    app.include_router(api.create_router(exige_papel, auditoria=AuditChain(tmp_path / "audit.jsonl")))
    token = criar_token_sessao("k08-engenharia", "gestor_ti")
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as client:
        yield client


def test_probe_bloqueia_alvo_externo(client):
    r = client.post("/api/eng/probe", json={"host": "8.8.8.8", "port": 53})
    assert r.status_code == 403


def test_probe_kind_invalido(client):
    assert client.post("/api/eng/probe", json={"host": "127.0.0.1", "port": 80, "kind": "ftp"}).status_code == 422


def test_slo_e_metricas(client):
    corpo = {"alvo_pct": 99.9, "janela_dias": 30, "agora": "2026-10-31T00:00:00Z",
             "indisponibilidades": [{"inicio": "2026-10-30T23:50:00Z", "fim": "2026-10-31T00:00:00Z"}]}
    r = client.post("/api/eng/slo/avaliar", json=corpo)
    assert r.status_code == 200 and any(a["acao"] == "page" for a in r.json()["alertas"])
    assert client.post("/api/eng/slo/avaliar", json={**corpo, "alvo_pct": 100}).status_code == 422
    m = client.post("/api/eng/incidentes/metricas", json=[
        {"id": "a", "inicio_real": "2026-10-01T00:00:00Z", "detectado_em": "2026-10-01T00:00:04Z"}])
    assert m.json()["MTTD"]["media_s"] == 4


def test_anomalias_e_auditoria(client):
    serie = [20.0 + (i % 3) * 0.1 for i in range(60)] + [90.0]
    assert client.post("/api/eng/anomalias", json={"serie": serie}).json()["indices"] == [60]
    assert client.post("/api/eng/anomalias", json={"serie": serie, "metodo": "x"}).status_code == 422
    assert client.get("/api/eng/auditoria/verificar").json()["integra"] is True


@pytest.mark.parametrize('method,path,payload', [
    ('POST', '/api/eng/probe', {'host': '127.0.0.1', 'port': 80}),
    ('POST', '/api/eng/slo/avaliar', {'indisponibilidades': []}),
    ('POST', '/api/eng/incidentes/metricas', []),
    ('POST', '/api/eng/anomalias', {'serie': [1, 2]}),
    ('GET', '/api/eng/auditoria/verificar', None),
])
def test_packaged_routes_require_auth_and_role(client, method, path, payload):
    assert client.request(method, path, json=payload, headers={'Authorization': ''}).status_code == 401
    token = criar_token_sessao('suporte.n1', 'suporte_n1')
    assert client.request(method, path, json=payload,
                          headers={'Authorization': f'Bearer {token}'}).status_code == 403


def test_router_cannot_be_created_without_host_authorization():
    with pytest.raises(TypeError):
        api.create_router()


def test_probe_dns_misto_nao_conecta(client, monkeypatch):
    import socket
    from sigma_eng import probe
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))
        for ip in ("127.0.0.1", "8.8.8.8")])
    def forbidden(*args, **kwargs):
        pytest.fail("API tentou conexão não autorizada")
    monkeypatch.setattr(probe, "_connect_ip", forbidden)
    response = client.post("/api/eng/probe", json={"host": "hospital.test", "port": 80})
    assert response.status_code == 403


def test_probe_api_fixa_destino_para_toda_serie(client, monkeypatch):
    import socket
    from sigma_eng import probe
    calls, destinations = [], []
    def dns(*args, **kwargs):
        calls.append(args[0])
        ip = "127.0.0.1" if len(calls) == 1 else "8.8.8.8"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))]
    class Connection:
        def close(self):
            pass
    def connect(address, **kwargs):
        destinations.append(address)
        return Connection()
    monkeypatch.setattr(socket, "getaddrinfo", dns)
    monkeypatch.setattr(probe, "_connect_ip", connect)
    response = client.post("/api/eng/probe", json={"host": "hospital.test", "port": 80, "count": 3})
    assert response.status_code == 200
    assert response.json()["failures"] == 0
    assert calls == ["hospital.test"]
    assert destinations == [("127.0.0.1", 80)] * 3
