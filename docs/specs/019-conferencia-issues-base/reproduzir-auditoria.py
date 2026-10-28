"""Diagnóstico da #6, só com dados temporários. Exit0 = lacunas reproduzidas, NÃO correção aprovada."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/"backend"))
from auth import UsuarioRepository,obter_auditor
from sigma_eng.audit_chain import AuditChain
from fastapi.testclient import TestClient


def main():
    with TemporaryDirectory(prefix="sigma-audit-gap-") as temporary:
        folder=Path(temporary)
        secret="synthetic-only-"+"s"*40
        path=folder/"multi.jsonl"
        os.environ.update(SIGMA_AUDIT_PATH=str(path),SIGMA_AUDIT_KEY=secret)
        AuditChain(path,chave=secret.encode()).registrar("synthetic","seed")
        a=obter_auditor();b=obter_auditor()
        a.registrar("synthetic.a","auth.login.success")
        b.registrar("synthetic.b","auth.logout")
        fresh=AuditChain(path,chave=secret.encode())
        first={"disk_entries":len(fresh),"disk_integrity":fresh.verificar()[0],
               "first_invalid_index":fresh.verificar()[1],"cached_entries":len(a),
               "cached_integrity":a.verificar()[0]}
        assert first=={"disk_entries":3,"disk_integrity":False,"first_invalid_index":2,
                       "cached_entries":2,"cached_integrity":True}
        users=folder/"users.json"
        repo=UsuarioRepository()
        repo.adicionar_usuario("synthetic.manager","synthetic-password-25","gestor_ti")
        users.write_text(json.dumps([asdict(u) for u in repo._usuarios.values()]),encoding="utf-8")
        path=folder/"api.jsonl"
        os.environ.update(SIGMA_DATABASE_URL="",SIGMA_USERS_FILE=str(users),SIGMA_AUDIT_PATH=str(path),
            SIGMA_JWT_SECRET="synthetic-jwt-only-"+"j"*40,OPENROUTER_API_KEY="fake-only",
            SIGMA_LLM_MODEL="test/model",SIGMA_CORS_ORIGINS="http://localhost:5173",
            SIGMA_COLLECTION_ENABLED="0",PYTHON_DOTENV_DISABLED="1")
        import main as application
        with TestClient(application.app) as client:
            login=client.post("/api/auth/login",json={"username":"synthetic.manager","password":"synthetic-password-25"})
            assert login.status_code==200
            response=client.get("/api/eng/auditoria/verificar",headers={"Authorization":"Bearer "+login.json()["access_token"]})
            assert response.status_code==200
            disk=AuditChain(path,chave=secret.encode())
            second={"disk_entries":len(disk),"api_entries":response.json()["entradas"],
                    "api_integrity":response.json()["integra"],"disk_integrity":disk.verificar()[0]}
            assert second=={"disk_entries":1,"api_entries":0,"api_integrity":True,"disk_integrity":True}
        print(json.dumps({"status":"gaps_reproduced_not_fixed","multiple_instances":first,
                          "stale_api_verification":second},ensure_ascii=False,indent=2))


if __name__=="__main__":main()
