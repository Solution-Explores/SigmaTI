import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest

from persistence.operational import PostgresOperationalStore
from persistence.scheduler_lease import SchedulerLease


@pytest.fixture
def store(pg):
    return PostgresOperationalStore(pg.engine)


def test_collection_detector_and_incident_commit_together_and_recover(store):
    target = store.create_target("synthetic", "127.0.0.1", 18080, detector="mad")
    for _ in range(20):
        store.record_measurement(target["id"], True, 10, detector_kind="mad")
    fresh = PostgresOperationalStore(store.engine)
    assert len(fresh.get("detectors", target["id"])["state"]["buf"]) == 20
    first = fresh.record_measurement(target["id"], True, 200, detector_kind="mad")["incident"]
    second = fresh.record_measurement(target["id"], True, 200, detector_kind="mad")["incident"]
    assert first["id"] == second["id"] and first["tipo"] == "latency"
    active = [row for row in fresh.incidents(True) if row["alvo_id"] == target["id"]]
    assert len(active) == 1
    assert len(fresh.get("detectors", target["id"])["state"]["buf"]) == 20


def test_collection_failure_rolls_back_detector_and_measurement(store, monkeypatch):
    target = store.create_target("synthetic", "127.0.0.1", 18080)
    store.record_measurement(target["id"], True, 10, detector_kind="ewma")
    previous = store.get("detectors", target["id"])
    def failed(*args, **kwargs):
        raise RuntimeError("synthetic")
    monkeypatch.setattr(store, "_aggregate", failed)
    with pytest.raises(RuntimeError):
        store.record_measurement(target["id"], True, 100, detector_kind="ewma")
    assert store.get("detectors", target["id"]) == previous
    assert len(store.measurements(target["id"])) == 1


def test_concurrent_collection_after_restart_has_one_active_incident(store):
    target = store.create_target("synthetic", "127.0.0.1", 18080)
    def record(_):
        return PostgresOperationalStore(store.engine).record_measurement(target["id"], False,
                                                                         detector_kind="ewma")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(record, range(8)))
    assert len({row["incident"]["id"] for row in results}) == 1
    assert store.get("detectors", target["id"])["versao"] == 8


def test_scheduler_lease_is_exclusive_and_transfers(store):
    first, second = SchedulerLease(store.engine), SchedulerLease(store.engine)
    try:
        assert first.acquire()
        assert first.acquire()
        assert not second.acquire()
        first.release()
        assert second.acquire()
    finally:
        first.release()
        second.release()


def test_stream_filters_audit_and_replays_committed_incidents(store):
    target = store.create_target("synthetic", "127.0.0.1", 18080)
    incident = store.record_measurement(target["id"], False)["incident"]
    events = store.stream_events()
    created = next(row for row in events if row["incidente_id"] == incident["id"])
    store.change_incident(incident["id"], "ack", "synthetic-user")
    store.change_incident(incident["id"], "resolve", "synthetic-user")
    replay = store.stream_events(created["id"])
    own = [row for row in replay if row["incidente_id"] == incident["id"]]
    assert [row["acao"] for row in own] == ["incident.ack", "incident.resolve"]
    assert all(set(row) == {"id", "ts", "acao", "incidente_id", "alvo_id"} for row in replay)


def test_collection_configuration_and_status_rbac(store, pg_client):
    import auth
    for role, expected in [("suporte_n1",403),("analista_redes",200),("gestor_ti",200)]:
        username = uuid.uuid4().hex
        auth.usuario_repo.adicionar_usuario(username,"synthetic-password",role)
        headers = {"Authorization":"Bearer "+auth.criar_token_sessao(username,role)}
        assert pg_client.get("/api/eng/coleta/status",headers=headers).status_code == expected
        target = store.create_target("synthetic", "127.0.0.1", 18080)
        response = pg_client.patch("/api/eng/alvos/"+target["id"], json={"ativo":False},headers=headers)
        assert response.status_code == expected
        if expected == 200:
            assert not response.json()["ativo"]
            assert target["id"] not in {t["id"] for t in store.collection_targets()}
    assert pg_client.get("/api/eng/eventos").status_code == 401
    headers = {"Authorization":"Bearer "+auth.criar_token_sessao(username,role)}
    for cursor in ["-1", "abc", "9223372036854775808"]:
        assert pg_client.get("/api/eng/eventos",headers={**headers,"Last-Event-ID":cursor}).status_code == 422
    assert pg_client.get("/api/eng/eventos?token=synthetic",headers=headers).status_code == 422
