"""API de teste local para Playwright: provedor simulado, credenciais efêmeras."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import secrets
import re
from datetime import datetime,timedelta,timezone
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
from auth import UsuarioRepository
from scripts.validate_api_acceptance import serve


def main():
    password = os.environ["SIGMA_BROWSER_PASSWORD"]
    directory = ROOT / "test-results" / ("browser-" + secrets.token_hex(6))
    directory.mkdir(parents=True)
    repo = UsuarioRepository()
    roles={"browser.demo":"suporte_n1", "browser.analyst":"analista_redes",
           "browser.reviewer":"analista_redes", "browser.manager":"gestor_ti"}
    for username,role in roles.items():
        repo.adicionar_usuario(username,password,role)
    users = directory / "users.json"
    users.write_text(json.dumps([asdict(u) for u in repo._usuarios.values()]), encoding="utf-8")
    os.environ.update({"OPENROUTER_API_KEY": "fake-browser-only", "SIGMA_LLM_MODEL": "test/model",
        "SIGMA_CORS_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
        "SIGMA_JWT_SECRET": secrets.token_hex(32), "SIGMA_USERS_FILE": str(users),
        "SIGMA_AUDIT_KEY": secrets.token_hex(32), "SIGMA_AUDIT_PATH": str(directory / "audit.jsonl"),
        "PYTHON_DOTENV_DISABLED": "1", "SIGMA_DATABASE_URL":"",
        "SIGMA_COLLECTION_ENABLED":"0"})
    engine=None
    tcp=None
    database_url=os.environ.get("SIGMA_BROWSER_DATABASE_URL")
    if database_url:
        from sqlalchemy.engine import make_url
        options=make_url(database_url).query.get("options","")
        if not re.fullmatch(r"-csearch_path=sigma_panel_[0-9a-f]{32}",options):
            raise RuntimeError("Ensaio exige schema sigma_panel isolado.")
        from persistence.database import open_database
        from persistence.identity import PostgresIdentityStore
        from persistence.operational import PostgresOperationalStore
        from sigma_eng.approvals import ApprovalService
        from sigma_eng.audit_chain import AuditChain
        from auth import password_hasher
        from scripts.validate_collection import TCPService
        engine=open_database(database_url)
        identity=PostgresIdentityStore(engine)
        for username,role in roles.items():
            identity.save_user(username,password_hasher.hash(password),role)
        store=PostgresOperationalStore(engine)
        tcp=TCPService()
        now=datetime.now(timezone.utc)
        historical=store.create_target("Portal de testes","127.0.0.1",tcp.port,intervalo_s=3600,timeout_s=.5)
        store.save_slo(historical["id"],95,1,"browser.fixture")
        for hour in range(25):
            store.record_measurement(historical["id"],hour!=23,10,ts=now-timedelta(hours=24-hour))
        store.create_target("Coletor SSE de teste","127.0.0.1",tcp.port,intervalo_s=.2,timeout_s=.3)
        store.create_target("Serviço aguardando coleta","127.0.0.1",tcp.port,intervalo_s=3600)
        ApprovalService(repository=store).solicitar("Revisar mudança sintética","browser.analyst")
        AuditChain(os.environ["SIGMA_AUDIT_PATH"],chave=os.environ["SIGMA_AUDIT_KEY"].encode()).registrar(
            "browser.fixture","fixture.seeded","synthetic")
        os.environ.update(SIGMA_DATABASE_URL=database_url,SIGMA_COLLECTION_ENABLED="1",
                          SIGMA_COLLECTION_SEED="0",SIGMA_PROBE_NETS="127.0.0.0/8")
    try:
        serve(ROOT, 18000, directory / "events.jsonl")
    finally:
        if tcp is not None: tcp.stop()
        if engine is not None: engine.dispose()
        users.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
