"""B3: mede MTTD, MTTA, MTTR e burn rate com o instante real da falha registrado.

Reusa o arreio do scripts/validate_collection.py (PostgreSQL isolado, API real,
SSE real, alvo TCP em loopback) e acrescenta o que o ensaio E2 nao fazia:
reconhecer e resolver cada incidente, para que MTTA, MTTR e o SLO tenham dados.

O instante real da falha (inicio_real) e tomado no processo de medicao, logo
antes de derrubar o servico TCP. A deteccao e medida pelo relogio monotonico ate
o quadro SSE incident.created chegar ao cliente, portanto e um LIMITE SUPERIOR
do TTD: inclui a entrega pelo SSE. MTTA e MTTR usam os carimbos do banco,
relativos a detectado_em, sem misturar relogios.
"""
import argparse
import datetime as dt
import json
import os
import secrets
import statistics
import subprocess
import sys
import time
import uuid
from datetime import timedelta
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

import validate_collection as vc
from persistence.database import open_database
from persistence.identity import PostgresIdentityStore
from persistence.operational import PostgresOperationalStore
from auth import password_hasher
from sigma_eng import incidents as inc_mod
from sigma_eng import slo as slo_mod
from sigma_eng.stats import percentile


def resumo(valores):
    v = sorted(valores)
    return {"n": len(v), "media_s": round(statistics.mean(v), 3),
            "mediana_s": round(statistics.median(v), 3),
            "p95_s": round(percentile(v, 95), 3), "max_s": round(max(v), 3)}


def como_objeto(amostra):
    """Reconstroi o incidente para a biblioteca do TCC, com inicio_real."""
    det = dt.datetime.fromisoformat(amostra["detectado_em"])
    return inc_mod.Incidente(
        id=str(amostra["repeticao"]),
        inicio_real=det - timedelta(seconds=amostra["ttd_s"]),
        detectado_em=det,
        reconhecido_em=det + timedelta(seconds=amostra["tta_s"]),
        resolvido_em=det + timedelta(seconds=amostra["ttr_s"]))


def run(database_url, output, repeats):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    schema = "sigma_mttd_" + uuid.uuid4().hex
    root_engine = create_engine(database_url, hide_parameters=True)
    engine = service = None
    with root_engine.begin() as c:
        c.execute(text(f"CREATE SCHEMA {schema}"))
    try:
        isolated = make_url(database_url).update_query_dict(
            {"options": "-csearch_path=" + schema}).render_as_string(hide_password=False)
        env = dict(os.environ, SIGMA_DATABASE_URL=isolated,
                   SIGMA_COLLECTION_ENABLED="1", SIGMA_COLLECTION_CONCURRENCY="32",
                   SIGMA_COLLECTION_SEED="0", OPENROUTER_API_KEY="fake-only",
                   SIGMA_LLM_MODEL="test/model", SIGMA_JWT_SECRET=secrets.token_hex(32),
                   SIGMA_CORS_ORIGINS="http://localhost:5173", PYTHON_DOTENV_DISABLED="1",
                   SIGMA_PROBE_NETS="127.0.0.0/8",
                   SIGMA_AUDIT_PATH=str(output.parent / schema / "audit.jsonl"))
        mig = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                             cwd=ROOT, env=env, text=True, capture_output=True)
        if mig.returncode:
            raise RuntimeError("Migracao falhou: " + mig.stderr[-800:])
        engine = open_database(isolated)
        store = PostgresOperationalStore(engine)
        user, pw = "b3-mttd", secrets.token_urlsafe(24)
        PostgresIdentityStore(engine).save_user(user, password_hasher.hash(pw), "gestor_ti")
        log_path = output.with_suffix(".log")

        amostras = []
        with vc.api_server(env, log_path) as base:
            status, login = vc.request(base, "POST", "/api/auth/login",
                                       {"username": user, "password": pw})
            assert status == 200, status
            token = login["access_token"]
            client = vc.SSEClient(base, token)
            try:
                for rep in range(repeats):
                    service = vc.TCPService()
                    status, target = vc.request(base, "POST", "/api/eng/alvos", {
                        "nome": "b3-mttd", "host": "127.0.0.1", "porta": service.port,
                        "intervalo_s": 0.1, "timeout_s": 0.5}, token)
                    assert status == 200, status
                    ident = target["id"]
                    vc.wait_until(lambda: any(r["sucesso"] for r in store.measurements(ident)))
                    t0 = time.perf_counter()
                    service.stop()
                    service = None
                    recebido, _, payload = client.wait(
                        lambda f, d: d.get("acao") == "incident.created"
                        and d.get("alvo_id") == ident)
                    ttd = recebido - t0
                    incidente = payload["incidente_id"]
                    status, _ = vc.request(
                        base, "POST", f"/api/eng/incidentes/{incidente}/reconhecer", {}, token)
                    assert status == 200, status
                    status, _ = vc.request(
                        base, "POST", f"/api/eng/incidentes/{incidente}/resolver", {}, token)
                    assert status == 200, status
                    linha = [r for r in store.incidents(limit=500) if r["id"] == incidente][0]
                    det, ack, res = linha["detectado_em"], linha["reconhecido_em"], linha["resolvido_em"]
                    assert ack is not None and res is not None, linha
                    amostras.append({
                        "repeticao": rep, "ttd_s": ttd,
                        "tta_s": (ack - det).total_seconds(),
                        "ttr_s": (res - det).total_seconds(),
                        "detectado_em": det.isoformat(), "resolvido_em": res.isoformat()})
                    vc.request(base, "PATCH", "/api/eng/alvos/" + ident, {"ativo": False}, token)
            finally:
                client.close()

        # Conferencia: a biblioteca do TCC, alimentada com inicio_real, da o mesmo MTTD.
        objetos = [como_objeto(a) for a in amostras]
        pela_biblioteca = inc_mod.metricas(objetos)

        # SLO e burn rate sobre os incidentes medidos, contra um SLO declarado.
        intervalos = [iv for o in objetos if (iv := o.intervalo_indisponivel())]
        agora = max(e for _, e in intervalos)
        objetivo = slo_mod.SLO("disponibilidade dos alvos", alvo_pct=99.9, janela_dias=30)
        orcamento = slo_mod.error_budget(objetivo, intervalos, agora)
        burn = {f"{h}h": round(slo_mod.burn_rate(objetivo, intervalos, agora, timedelta(hours=h)), 3)
                for h in (1, 6, 24)}
        alertas = slo_mod.burn_alerts(objetivo, intervalos, agora)

        relatorio = {
            "sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                                  capture_output=True).stdout.strip(),
            "repeticoes": repeats,
            "maquina": "fisica (Windows 10, 16 GB, 12 processadores logicos, SSD)",
            "MTTD_s": resumo([a["ttd_s"] for a in amostras]),
            "MTTA_s": resumo([a["tta_s"] for a in amostras]),
            "MTTR_s": resumo([a["ttr_s"] for a in amostras]),
            "MTTD_pela_biblioteca": pela_biblioteca["MTTD"],
            "intervalos_indisponiveis": len(intervalos),
            "slo": {"nome": objetivo.nome, "alvo_pct": objetivo.alvo_pct,
                    "janela_dias": objetivo.janela_dias, **orcamento.as_dict()},
            "burn_rate_por_janela": burn,
            "alertas_burn": alertas,
            "escopo": ("loopback, um alvo TCP por repeticao, PostgreSQL em schema descartavel; "
                       "TTD inclui a entrega pelo SSE, portanto e limite superior; "
                       "MTTA e MTTR sao de reconhecimento e resolucao imediatos por chamada de "
                       "API, nao de operador humano"),
            "amostras": amostras,
        }
        output.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({k: v for k, v in relatorio.items() if k != "amostras"},
                         indent=2, ensure_ascii=False))
        return relatorio
    finally:
        if service is not None:
            service.stop()
        if engine is not None:
            engine.dispose()
        with root_engine.begin() as c:
            c.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        root_engine.dispose()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    p.add_argument("--repeats", type=int, default=30)
    a = p.parse_args()
    run(os.environ["SIGMA_TEST_DATABASE_URL"], a.output, a.repeats)
