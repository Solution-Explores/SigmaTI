import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sigma_eng import api


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from sigma_eng.audit_chain import AuditChain
    monkeypatch.setattr(api, "auditoria", AuditChain(tmp_path / "audit.jsonl"))
    app = FastAPI()
    app.include_router(api.router)
    return TestClient(app)


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
