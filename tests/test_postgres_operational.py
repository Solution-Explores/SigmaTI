"""Aceite operacional contra PostgreSQL real, sem comandos/rede externos."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
import subprocess
import sys
import uuid

import pytest
from sqlalchemy import inspect, select

import auth
from persistence.operational import PostgresOperationalStore
from persistence.operational_models import IncidentRow, MeasurementRow
from sigma_eng.approvals import ApprovalService, AprovacaoError
from sigma_eng.anomaly import EwmaDetector, MadDetector
from sigma_eng.runbooks import RunbookRunner, RunbookError, ResultadoPasso, parsear
from sigma_eng.state import StateConflict, detector_snapshot, restore_detector


@pytest.fixture
def store(pg):
    return PostgresOperationalStore(pg.engine)


def target(store):
    return store.create_target("Alvo sintético", "127.0.0.1", 18080)


def test_schema_and_monthly_partition(store):
    tables = set(inspect(store.engine).get_table_names())
    assert {"alvos", "medicoes", "incidentes", "aprovacoes", "execucoes_runbook", "slo", "detectores"} <= tables
    t = target(store)
    store.record_measurement(t["id"], True, 10, datetime(2026, 8, 1, tzinfo=timezone.utc))
    assert "medicoes_202608" in inspect(store.engine).get_table_names()
    assert any(i["name"] == "ix_medicoes_alvo_ts" for i in inspect(store.engine).get_indexes("medicoes"))


def test_downsampling_and_repeated_measurement(store):
    t = target(store)
    ts = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
    identifier = str(uuid.uuid4())
    store.record_measurement(t["id"], True, 10, ts, identifier)
    assert not store.record_measurement(t["id"], True, 10, ts, identifier)["inserted"]
    store.record_measurement(t["id"], True, 20, ts + timedelta(seconds=2))
    store.record_measurement(t["id"], False, None, ts + timedelta(minutes=1))
    minute = store.aggregates(t["id"], "minute")
    hour = store.aggregates(t["id"], "hour")[0]
    assert len(minute) == 2 and sum(row["total"] for row in minute) == 3
    assert hour["total"] == 3 and hour["sucessos"] == 2
    assert hour["latencia_n"] == 2 and hour["latencia_media"] == 15
    assert hour["latencia_min"] == 10 and hour["latencia_max"] == 20


def test_concurrent_failures_create_one_active_incident(store):
    t = target(store)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: store.record_measurement(t["id"], False), range(8)))
    assert len({result["incident"]["id"] for result in results}) == 1
    events = [event for event in store.events() if event["acao"] == "incident.created"
              and event["detalhes"].get("alvo_id") == t["id"]]
    assert len(events) == 1


def test_incident_ack_resolution_and_new_failure(store):
    t = target(store)
    first = store.record_measurement(t["id"], False)["incident"]
    assert store.change_incident(first["id"], "ack", "analyst")["reconhecido_em"] is not None
    resolved = store.change_incident(first["id"], "resolve", "analyst")
    assert resolved["resolvido_em"] is not None
    assert store.change_incident(first["id"], "resolve", "analyst")["resolvido_em"] == resolved["resolvido_em"]
    second = store.record_measurement(t["id"], False)["incident"]
    assert second["id"] != first["id"]
    assert len([i for i in store.incidents(True) if i["alvo_id"] == t["id"]]) == 1


def test_measurement_and_audit_rollback_together(store, monkeypatch):
    t = target(store)
    def fail(*args, **kwargs):
        raise RuntimeError("injected audit failure")
    monkeypatch.setattr(store, "_event", fail)
    with pytest.raises(RuntimeError):
        store.record_measurement(t["id"], False, ts=datetime(2026, 7, 1, tzinfo=timezone.utc))
    assert store.measurements(t["id"]) == []
    assert store.aggregates(t["id"], "hour") == []
    assert not any(i["alvo_id"] == t["id"] for i in store.incidents())


def test_retention_preserves_aggregates_and_drops_old_partition(store):
    t = target(store)
    old = datetime(2026, 1, 10, tzinfo=timezone.utc)
    recent = datetime(2026, 10, 19, tzinfo=timezone.utc)
    store.record_measurement(t["id"], True, 5, old)
    store.record_measurement(t["id"], True, 15, recent)
    result = store.retain(30, now=recent + timedelta(days=1))
    assert "medicoes_202601" in result["particoes"]
    assert len(store.measurements(t["id"])) == 1
    assert sum(row["total"] for row in store.aggregates(t["id"], "hour")) == 2


def test_slo_survives_repository_recreation(store):
    t = target(store)
    store.save_slo(t["id"], 99.9, 30, "analyst")
    other = PostgresOperationalStore(store.engine)
    assert other.get_slo(t["id"])["alvo_pct"] == 99.9


def test_approval_recovery_expiration_and_separation(store):
    first = ApprovalService(repository=store)
    ap = first.solicitar("runbook:synthetic:step", "requester")
    second = ApprovalService(repository=PostgresOperationalStore(store.engine))
    assert any(row.id == ap.id for row in second.pendentes())
    with pytest.raises(AprovacaoError):
        second.aprovar(ap.id, "requester", "gestor_ti")
    assert second.aprovar(ap.id, "decider", "gestor_ti").estado == "approved"
    clock = lambda: datetime.now(timezone.utc) + timedelta(days=1)
    expired = first.solicitar("expired", "requester")
    third = ApprovalService(repository=store, relogio=clock)
    with pytest.raises(AprovacaoError):
        third.aprovar(expired.id, "decider", "gestor_ti")
    assert store.get("approvals", expired.id)["estado"] == "expired"


def test_two_deciders_cannot_override_final_decision(store):
    ap = ApprovalService(repository=store).solicitar("x", "requester")
    def decide(actor):
        try:
            ApprovalService(repository=PostgresOperationalStore(store.engine)).aprovar(ap.id, actor, "gestor_ti")
            return True
        except AprovacaoError:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(decide, ["decider-a", "decider-b"])) == 1


def test_execution_waiting_approval_recovers_without_repeating_steps(store):
    calls = []
    def fake(argv, timeout):
        calls.append(argv)
        return ResultadoPasso("", True, "synthetic")
    md = "```sigma:step{id=before}\necho before\n```\n```sigma:step{id=after, requires_approval=true}\necho after\n```"
    runner = RunbookRunner(["echo"], fake, repository=store)
    ex = runner.executar(str(uuid.uuid4()), parsear(md), {}, dry_run=False)
    assert ex.status == "waiting_approval" and len(calls) == 1
    fresh = RunbookRunner(["echo"], fake, repository=PostgresOperationalStore(store.engine))
    restored = fresh.obter(ex.id)
    approvals = ApprovalService(repository=store)
    ap = approvals.solicitar(f"runbook:{ex.id}:after", "requester")
    ap = approvals.aprovar(ap.id, "decider", "gestor_ti")
    assert fresh.retomar(restored, ap).status == "completed" and len(calls) == 2
    with pytest.raises(RunbookError):
        fresh.retomar(restored, ap)
    assert len(calls) == 2


def test_interrupted_side_effect_is_never_repeated_automatically(store):
    calls = []
    def interrupted(argv, timeout):
        calls.append(argv)
        raise RuntimeError("process interruption")
    runner = RunbookRunner(["echo"], interrupted, repository=store)
    identifier = str(uuid.uuid4())
    with pytest.raises(RuntimeError):
        runner.executar(identifier, parsear("```sigma:step{id=a}\necho a\n```"), {}, dry_run=False)
    restored = RunbookRunner(["echo"], interrupted, repository=store).obter(identifier)
    assert restored.status == "running" and restored.passo_em_execucao == "a"
    ap = ApprovalService().solicitar("x", "requester")
    with pytest.raises(RunbookError):
        runner.retomar(restored, ap)
    assert len(calls) == 1


@pytest.mark.parametrize("kind", ["ewma", "mad"])
def test_detector_warmup_survives_new_process(store, kind):
    detector = EwmaDetector() if kind == "ewma" else MadDetector()
    for value in [10.0, 11.0, 10.5] * 10:
        detector.update(value)
    identifier = str(uuid.uuid4())
    store.create("detectors", identifier, detector_snapshot(detector))
    expected = detector.update(1000)
    code = ("import os,sys,json; from persistence.database import open_database; "
            "from persistence.operational import PostgresOperationalStore; "
            "from sigma_eng.state import restore_detector; "
            "engine=open_database(os.environ['SIGMA_TEST_DATABASE_URL']); "
            "det=restore_detector(PostgresOperationalStore(engine).get('detectors',sys.stdin.read())); "
            "print(json.dumps(det.update(1000))); engine.dispose()")
    result = subprocess.run([sys.executable, "-c", code], input=identifier, text=True,
                            capture_output=True, timeout=30, env=os.environ.copy())
    assert result.returncode == 0 and json.loads(result.stdout) == expected


def test_api_reads_survive_fresh_app_and_respect_roles(store, pg_client):
    import importlib
    from fastapi.testclient import TestClient
    def headers(role):
        username = "operational-" + uuid.uuid4().hex
        auth.usuario_repo.adicionar_usuario(username, "synthetic-password", role)
        return {"Authorization": "Bearer " + auth.criar_token_sessao(username, role)}
    analyst, n1 = headers("analista_redes"), headers("suporte_n1")
    body = {"nome": "synthetic", "host": "127.0.0.1", "porta": 18080}
    assert pg_client.post("/api/eng/alvos", json=body).status_code == 401
    assert pg_client.post("/api/eng/alvos", json=body, headers=n1).status_code == 403
    created = pg_client.post("/api/eng/alvos", json=body, headers=analyst)
    assert created.status_code == 200
    target_id = created.json()["id"]
    incident = store.record_measurement(target_id, False)["incident"]
    ap = pg_client.post("/api/eng/aprovacoes", json={"acao": "synthetic"}, headers=analyst).json()
    ex = RunbookRunner(["echo"], repository=store).executar(str(uuid.uuid4()),
        parsear("```sigma:step{id=a, requires_approval=true}\necho synthetic\n```"), {}, dry_run=False)
    previous = sys.modules.pop("main", None)
    try:
        module = importlib.import_module("main")
        with TestClient(module.app) as fresh:
            assert fresh.get("/api/eng/alvos", headers=n1).status_code == 200
            pending = fresh.get("/api/eng/aprovacoes", headers=analyst).json()["aprovacoes"]
            assert any(row["id"] == ap["id"] for row in pending)
            execution_data = fresh.get(f"/api/eng/execucoes/{ex.id}", headers=analyst).json()
            assert execution_data["status"] == "waiting_approval"
            assert "variaveis" not in execution_data and "passos" not in execution_data
            assert fresh.post(f"/api/eng/incidentes/{incident['id']}/reconhecer", headers=analyst).status_code == 200
            assert fresh.post(f"/api/eng/incidentes/{incident['id']}/resolver", headers=analyst).status_code == 200
    finally:
        sys.modules.pop("main", None)
        if previous is not None:
            sys.modules["main"] = previous


def test_real_http_api_restart_preserves_session_and_pending_work(store, monkeypatch, tmp_path):
    from contextlib import contextmanager
    import socket
    import time
    import urllib.request
    import urllib.error
    username = "restart-" + uuid.uuid4().hex
    # Usuário administrativo criado explicitamente em banco descartável.
    from persistence.identity import PostgresIdentityStore
    PostgresIdentityStore(store.engine).save_user(username, auth.password_hasher.hash("synthetic-password"), "analista_redes")
    env = dict(os.environ, OPENROUTER_API_KEY="fake-only", SIGMA_LLM_MODEL="test/model",
               SIGMA_CORS_ORIGINS="http://localhost:5173", PYTHON_DOTENV_DISABLED="1")
    log_path = tmp_path / "restart-api.log"
    def request(base, method, path, body=None, token=None):
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)
    @contextmanager
    def server():
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        with log_path.open("a", encoding="utf-8") as log:
            process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1",
                "--port", str(port)], env=env, stdout=log, stderr=log)
            try:
                for _ in range(100):
                    if process.poll() is not None:
                        pytest.fail("API não iniciou; verificar log de teste local.")
                    try:
                        if request(base, "GET", "/api/status")[0] == 401:
                            break
                    except (urllib.error.URLError, TimeoutError):
                        pass
                    time.sleep(0.1)
                else:
                    pytest.fail("API não ficou pronta.")
                yield base
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
    with server() as base:
        status, login = request(base, "POST", "/api/auth/login", {"username": username, "password": "synthetic-password"})
        assert status == 200
        token = login["access_token"]
        status, created = request(base, "POST", "/api/eng/alvos", {"nome": "restart", "host": "127.0.0.1", "porta": 18080}, token)
        assert status == 200
        status, approval = request(base, "POST", "/api/eng/aprovacoes", {"acao": "restart-synthetic"}, token)
        assert status == 200
        ex = RunbookRunner(["echo"], repository=store).executar(str(uuid.uuid4()),
            parsear("```sigma:step{id=a, requires_approval=true}\necho synthetic\n```"), {}, dry_run=False)
        incident = store.record_measurement(created["id"], False)["incident"]
    with server() as base:
        assert request(base, "GET", "/api/auth/me", token=token)[0] == 200
        status, pending = request(base, "GET", "/api/eng/aprovacoes", token=token)
        assert status == 200 and any(row["id"] == approval["id"] for row in pending["aprovacoes"])
        status, execution = request(base, "GET", f"/api/eng/execucoes/{ex.id}", token=token)
        assert status == 200 and execution["status"] == "waiting_approval"
        assert request(base, "POST", f"/api/eng/incidentes/{incident['id']}/resolver", token=token)[0] == 200
    logs = log_path.read_text(encoding="utf-8")
    assert token not in logs and "synthetic-password" not in logs and auth.JWT_SECRET not in logs


def test_retry_cannot_change_measurement_or_duplicate_incident(store):
    t = target(store)
    ts, identifier = datetime.now(timezone.utc), str(uuid.uuid4())
    first = store.record_measurement(t["id"], False, ts=ts, identifier=identifier)
    repeated = store.record_measurement(t["id"], False, ts=ts, identifier=identifier)
    assert not repeated["inserted"] and repeated["incident"]["id"] == first["incident"]["id"]
    with pytest.raises(StateConflict):
        store.record_measurement(t["id"], True, 10, ts=ts, identifier=identifier)
    assert len(store.measurements(t["id"])) == 1


def test_resolving_while_recording_failure_does_not_lose_measurement(store):
    t = target(store)
    incident = store.record_measurement(t["id"], False)["incident"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        resolving = pool.submit(store.change_incident, incident["id"], "resolve", "analyst")
        recording = pool.submit(store.record_measurement, t["id"], False)
        assert resolving.result()["resolvido_em"] is not None
        assert recording.result()["inserted"]
    assert len(store.measurements(t["id"])) == 2
    assert len([i for i in store.incidents(True) if i["alvo_id"] == t["id"]]) <= 1


def test_entire_operational_rbac_matrix_against_postgres(store, pg_client):
    t = target(store)
    incident = store.record_measurement(t["id"], False)["incident"]
    store.save_slo(t["id"], 99.9, 30, "system")
    execution = RunbookRunner(["echo"], repository=store).executar(str(uuid.uuid4()),
        parsear("```sigma:step{id=a}\necho synthetic\n```"), {})
    cases = [
        ("GET", "/alvos", None, 1),
        ("POST", "/alvos", {"nome": "rbac", "host": "127.0.0.1", "porta": 18080}, 2),
        ("GET", f"/alvos/{t['id']}/medicoes", None, 1),
        ("GET", f"/alvos/{t['id']}/agregados", None, 1),
        ("GET", "/incidentes", None, 1),
        ("POST", f"/incidentes/{incident['id']}/reconhecer", {}, 2),
        ("POST", f"/incidentes/{incident['id']}/resolver", {}, 2),
        ("GET", "/aprovacoes", None, 2),
        ("POST", "/aprovacoes", {"acao": "synthetic"}, 2),
        ("GET", f"/execucoes/{execution.id}", None, 2),
        ("POST", f"/alvos/{t['id']}/slo", {"alvo_pct": 99.9, "janela_dias": 30}, 2),
        ("GET", f"/alvos/{t['id']}/slo", None, 1),
        ("GET", "/auditoria/eventos", None, 3),
    ]
    for level, role in enumerate([None, "suporte_n1", "analista_redes", "gestor_ti"]):
        headers = {}
        if role:
            username = "matrix-" + uuid.uuid4().hex
            auth.usuario_repo.adicionar_usuario(username, "synthetic-password", role)
            headers = {"Authorization": "Bearer " + auth.criar_token_sessao(username, role)}
        ap = ApprovalService(repository=store).solicitar("synthetic", "other-requester")
        decision = ("POST", f"/aprovacoes/{ap.id}/decidir", {"aprovar": True}, 2)
        for method, path, body, minimum in cases + [decision]:
            expected = 401 if role is None else 403 if level < minimum else 200
            response = pg_client.request(method, "/api/eng" + path, json=body, headers=headers)
            assert response.status_code == expected, (method, path, role, response.status_code)
