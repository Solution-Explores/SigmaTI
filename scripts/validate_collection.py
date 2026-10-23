"""E2 e carga: HTTP/SSE real, PostgreSQL isolado e alvos TCP em loopback."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import csv
import json
import os
from pathlib import Path
import queue
import secrets
import socket
import statistics
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from persistence.database import open_database
from persistence.identity import PostgresIdentityStore
from persistence.operational import PostgresOperationalStore
from auth import password_hasher
from sigma_eng.stats import percentile


class TCPService:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.bind(("127.0.0.1", 0))
        self.port = self.socket.getsockname()[1]
        self.socket.listen(512)
        self.socket.settimeout(0.05)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        while not self.stop_event.is_set():
            try:
                connection, _ = self.socket.accept()
                connection.close()
            except socket.timeout:
                continue
            except OSError:
                return

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=1)
        self.socket.close()


def request(base, method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


class SSEClient:
    def __init__(self, base, token, cursor=None):
        self.messages = queue.Queue()
        self.ready = threading.Event()
        self.stop_event = threading.Event()
        self.error = None
        self.headers = {"Authorization": "Bearer " + token}
        if cursor is not None:
            self.headers["Last-Event-ID"] = str(cursor)
        self.url = base + "/api/eng/eventos"
        self.thread = threading.Thread(target=self.read, daemon=True)
        self.thread.start()
        if not self.ready.wait(10) or self.error:
            raise RuntimeError("SSE não conectou")

    def read(self):
        try:
            req = urllib.request.Request(self.url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=3) as response:
                self.ready.set()
                frame = {}
                while not self.stop_event.is_set():
                    line = response.readline().decode().strip()
                    if not line:
                        if "data" in frame:
                            self.messages.put((time.perf_counter(), frame))
                        frame = {}
                    elif not line.startswith(":"):
                        name, _, value = line.partition(":")
                        frame[name] = value.strip()
                    if response.isclosed():
                        break
        except Exception:
            if not self.stop_event.is_set():
                self.error = "SSE interrompido"
            self.ready.set()

    def wait(self, predicate, timeout=5):
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            try:
                received, frame = self.messages.get(timeout=max(0.01, deadline-time.perf_counter()))
            except queue.Empty:
                break
            payload = json.loads(frame["data"])
            if predicate(frame, payload):
                return received, frame, payload
        raise AssertionError("Evento esperado não recebido no prazo")

    def close(self):
        self.stop_event.set()
        self.thread.join(timeout=4)
        if self.thread.is_alive():
            raise RuntimeError("Cliente SSE não encerrou")


@contextmanager
def api_server(env, log_path):
    with socket.socket() as temporary:
        temporary.bind(("127.0.0.1", 0))
        port = temporary.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with log_path.open("a", encoding="utf-8") as log:
        process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1",
            "--port", str(port), "--timeout-graceful-shutdown", "2"], cwd=ROOT, env=env, stdout=log, stderr=log)
        try:
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError("API de ensaio não iniciou")
                try:
                    if request(base, "GET", "/api/status")[0] == 401:
                        break
                except (urllib.error.URLError, TimeoutError):
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError("API de ensaio não ficou pronta")
            yield base
        finally:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def wait_until(predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.03)
    raise AssertionError("Condição do ensaio não atingida")


def run(database_url, output, *, repeats=30, targets=200):
    if repeats < 30 or targets < 200:
        raise ValueError("E2 exige 30 repetições e carga exige 200 alvos")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Uma rodada reprovada não pode deixar um aceite antigo no caminho oficial.
    for artifact in (output, output.with_suffix('.csv'), output.with_suffix('.load.json')):
        if artifact.exists():
            history = output.parent / 'collection-history'
            history.mkdir(exist_ok=True)
            artifact.replace(history / (uuid.uuid4().hex + '-' + artifact.name))
    schema = "sigma_e2_" + uuid.uuid4().hex
    root_engine = create_engine(database_url, hide_parameters=True)
    engine = None
    service = None
    with root_engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA {schema}"))
    try:
        isolated_url = make_url(database_url).update_query_dict({"options": "-csearch_path=" + schema}).render_as_string(hide_password=False)
        env = dict(os.environ, SIGMA_DATABASE_URL=isolated_url,
            SIGMA_COLLECTION_ENABLED="1", SIGMA_COLLECTION_CONCURRENCY="32", SIGMA_COLLECTION_SEED="0",
            OPENROUTER_API_KEY="fake-only", SIGMA_LLM_MODEL="test/model",
            SIGMA_JWT_SECRET=secrets.token_hex(32), SIGMA_CORS_ORIGINS="http://localhost:5173",
            PYTHON_DOTENV_DISABLED="1", SIGMA_PROBE_NETS="127.0.0.0/8",
            SIGMA_AUDIT_PATH=str(output.parent / schema / 'audit.jsonl'))
        migration = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT,
            env=env, text=True, capture_output=True)
        if migration.returncode:
            raise RuntimeError("Migração do schema isolado falhou")
        engine = open_database(isolated_url)
        store = PostgresOperationalStore(engine)
        username, password = "e2-synthetic", secrets.token_urlsafe(24)
        PostgresIdentityStore(engine).save_user(username, password_hasher.hash(password), "gestor_ti")
        log_path = output.with_suffix(".log")
        rows, identifiers, incident_ids = [], [], []
        with api_server(env, log_path) as base:
            status, login = request(base, "POST", "/api/auth/login", {"username":username,"password":password})
            assert status == 200
            token = login["access_token"]
            assert request(base,"GET","/api/eng/eventos")[0] == 401
            client = SSEClient(base, token)
            try:
                for repetition in range(repeats):
                    service = TCPService()
                    status, target = request(base,"POST","/api/eng/alvos",{
                        "nome":"synthetic-e2", "host":"127.0.0.1", "porta":service.port,
                        "intervalo_s":0.1,"timeout_s":0.5},token)
                    assert status == 200
                    identifier = target["id"]
                    identifiers.append(identifier)
                    wait_until(lambda: any(row["sucesso"] for row in store.measurements(identifier)))
                    started = time.perf_counter()
                    service.stop()
                    service = None
                    received, frame, payload = client.wait(lambda frame, data:
                        data.get("acao")=="incident.created" and data.get("alvo_id")==identifier)
                    latency = received-started
                    assert latency <= 5, latency
                    rows.append({"repetition":repetition,"seconds":latency})
                    incident_ids.append(payload["incidente_id"])
                    status, _ = request(base,"PATCH","/api/eng/alvos/"+identifier,{"ativo":False},token)
                    assert status == 200
                cursor = int(frame["id"])
            finally:
                client.close()
            # Carga em 200 alvos lógicos reais contra serviço TCP local, sem mock da sonda.
            service = TCPService()
            load_ids = [store.create_target("synthetic-load", "127.0.0.1", service.port,
                intervalo_s=2.0, timeout_s=0.5)["id"] for _ in range(targets)]
            identifiers.extend(load_ids)
            try:
                wait_until(lambda: all(store.measurements(identifier,1) for identifier in load_ids), timeout=20)
            except AssertionError:
                metrics = request(base,"GET","/api/eng/coleta/status",token=token)[1]["metricas"]
                output.with_suffix('.load.json').write_text(json.dumps({
                    'phase': 'warmup_failed', 'targets': targets, 'metrics': metrics,
                    'scope': 'loopback; nenhum criterio de aceite relaxado'}, indent=2), encoding='utf-8')
                raise
            before = request(base,"GET","/api/eng/coleta/status",token=token)[1]["metricas"]
            window_start = datetime.now(timezone.utc)
            time.sleep(6)
            after = request(base,"GET","/api/eng/coleta/status",token=token)[1]["metricas"]
            window_end = datetime.now(timezone.utc)
            samples_by_target = [store.measurements(identifier,100) for identifier in load_ids]
            observed = sum(len(samples) for samples in samples_by_target)
            window_counts = [sum(window_start <= row["ts"] <= window_end for row in samples)
                             for samples in samples_by_target]
            output.with_suffix(".load.json").write_text(json.dumps({"before":before,"after":after,
                "measurements":observed},indent=2),encoding="utf-8")
            assert after["queued"] == 0 and after["peak_active"] <= 32
            assert after["max_lag_seconds"] < 0.5
            assert after["errors"] == 0 and after["missed"] == before["missed"]
            assert observed >= targets * 3
            assert min(window_counts) >= 2
            assert after["completed"] - before["completed"] >= targets * 2
            for identifier in load_ids:
                store.configure_target(identifier,False,"e2")
            service.stop()
            service = None
            # Mantém um alvo caído ativo durante o reinício, com incidente já aberto.
            store.configure_target(identifiers[0],True,"e2")
        with api_server(env, log_path) as base:
            assert request(base,"GET","/api/auth/me",token=token)[0] == 200
            count = len(store.measurements(identifiers[0]))
            wait_until(lambda: len(store.measurements(identifiers[0])) > count)
            active = [row for row in store.incidents(True) if row["alvo_id"]==identifiers[0]]
            assert len(active)==1 and active[0]["id"]==incident_ids[0]
            replay = SSEClient(base,token,cursor)
            try:
                status, _ = request(base,"POST","/api/eng/incidentes/"+incident_ids[-1]+"/reconhecer",token=token)
                assert status == 200
                _, replay_frame, _ = replay.wait(lambda f,d: d.get("incidente_id")==incident_ids[-1]
                                                  and d.get("acao")=="incident.ack")
                assert int(replay_frame["id"]) > cursor
                status,_=request(base,"POST","/api/auth/logout",token=token)
                assert status==200
                replay.wait(lambda f,d: f.get("event")=="session.closed",timeout=3)
            finally:
                replay.close()
        logs = log_path.read_text(encoding="utf-8")
        assert token not in logs and password not in logs and env["SIGMA_JWT_SECRET"] not in logs
        samples = sorted(row["seconds"] for row in rows)
        report = {"seed":0,"repetitions":repeats,"median_seconds":statistics.median(samples),
            "p95_seconds":percentile(samples,95),"max_seconds":max(samples),
            "within_5_seconds":sum(t<=5 for t in samples)/len(samples),
            "load":{"targets":targets,"interval_seconds":2,"observation_seconds":6,
                    "measurements":observed,"window_measurements":sum(window_counts),
                    "minimum_per_target_in_window":min(window_counts),"before":before,"after":after},
            "restart_unique_incident":True,"session_survives_restart":True,
            "replay_after_restart":True,"logout_closes_stream":True,
            "scope":"loopback; 200 logical targets, one TCP service; no browser/panel or hospital network"}
        output.write_text(json.dumps(report,indent=2),encoding="utf-8")
        with output.with_suffix(".csv").open("w",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=["repetition","seconds"])
            writer.writeheader()
            writer.writerows(rows)
        print(json.dumps(report),flush=True)
        return report
    finally:
        if service is not None:
            service.stop()
        if engine is not None:
            engine.dispose()
        with root_engine.begin() as connection:
            connection.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        root_engine.dispose()


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",default="test-results/collection-e2.json")
    args=parser.parse_args()
    url=os.getenv("SIGMA_TEST_DATABASE_URL")
    if not url:
        raise SystemExit("Configure SIGMA_TEST_DATABASE_URL para banco descartável.")
    run(url,args.output)
