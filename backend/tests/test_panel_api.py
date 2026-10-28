from datetime import datetime,timedelta,timezone
import uuid

import auth
from persistence.operational import PostgresOperationalStore


def test_health_marks_missing_and_stale_data_unknown_without_inventing_budget(pg):
    store=PostgresOperationalStore(pg.engine)
    now=datetime.now(timezone.utc)
    empty=store.create_target("empty","127.0.0.1",8080)
    gap=store.create_target("gap","127.0.0.1",8081)
    store.save_slo(gap["id"],99.9,1,"synthetic")
    store.record_measurement(gap["id"],False,ts=now-timedelta(hours=5))
    data={row["id"]:row for row in store.health_snapshot(now=now)["servicos"]}
    assert data[empty["id"]]["status"] == "unknown"
    assert data[empty["id"]]["orcamento"] is None
    row=data[gap["id"]]
    assert row["status"] == "unknown"
    assert not row["orcamento"]["completo"]
    assert row["orcamento"]["esgota_em"] is None
    assert row["orcamento"]["consumido_min"] == .05
    assert row["orcamento"]["cobertura_pct"] < 1


def test_health_complete_window_uses_measured_downtime_and_projection(pg):
    store=PostgresOperationalStore(pg.engine)
    now=datetime.now(timezone.utc).replace(microsecond=0)
    target=store.create_target("hourly","127.0.0.1",8080,intervalo_s=3600)
    store.save_slo(target["id"],95,1,"synthetic")
    for hour in range(25):
        store.record_measurement(target["id"],hour!=23,10,ts=now-timedelta(hours=24-hour))
    row=next(row for row in store.health_snapshot(now=now)["servicos"] if row["id"]==target["id"])
    assert row["status"]=="up"
    budget=row["orcamento"]
    assert budget["completo"] and budget["cobertura_pct"]==100
    assert budget["consumido_min"]==60 and budget["restante_max_min"]==12
    assert budget["status"]=="at_risk"
    assert datetime.fromisoformat(budget["esgota_em"])==now+timedelta(hours=4.8)


def test_panel_read_routes_follow_role_matrix(pg,pg_client):
    store=PostgresOperationalStore(pg.engine)
    from sigma_eng.approvals import ApprovalService
    item=ApprovalService(repository=store).solicitar("synthetic","other")
    for role,level in [(None,0),("suporte_n1",1),("analista_redes",2),("gestor_ti",3)]:
        headers={}
        if role:
            username=uuid.uuid4().hex
            auth.usuario_repo.adicionar_usuario(username,"synthetic-password",role)
            headers={"Authorization":"Bearer "+auth.criar_token_sessao(username,role)}
        for path,minimum in [("/saude",1),("/incidentes/resumo",2),("/auditoria/recentes",3),("/aprovacoes/"+item.id,2)]:
            response=pg_client.get("/api/eng"+path,headers=headers)
            assert response.status_code == (401 if not role else 403 if level<minimum else 200),(path,role,response.text)
    data=pg_client.get("/api/eng/incidentes/resumo",headers=headers).json()
    assert data["metricas"]["MTTD"]=={"n":0}
    events=pg_client.get("/api/eng/auditoria/recentes",headers=headers).json()["eventos"]
    assert [e["id"] for e in events]==sorted((e["id"] for e in events),reverse=True)


def test_health_exactly_consumed_budget_is_exhausted(pg):
    store=PostgresOperationalStore(pg.engine)
    now=datetime.now(timezone.utc).replace(microsecond=0)
    target=store.create_target("exact-budget","127.0.0.1",8080,intervalo_s=3600)
    store.save_slo(target["id"],50,1,"synthetic")
    for hour in range(25):
        store.record_measurement(target["id"],hour>=12,10,ts=now-timedelta(hours=24-hour))
    budget=next(row["orcamento"] for row in store.health_snapshot(now=now)["servicos"] if row["id"]==target["id"])
    assert budget["completo"]
    assert budget["restante_max_min"]==0
    assert budget["status"]=="breaching"
    assert budget["esgota_em"] is None
