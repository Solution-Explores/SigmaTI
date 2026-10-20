"""Smoke RNF06: falha→SSE→backup→banco novo→recriação, somente dados fictícios."""
from __future__ import annotations
import argparse
import json
import hashlib
import hmac
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.recovery import backup, restore, verify, fingerprint, sql, canonical, digest
from scripts.validate_postgres import IMAGE
from scripts.validate_collection import TCPService, SSEClient, api_server, request, wait_until
from persistence.database import open_database
from persistence.identity import PostgresIdentityStore
from auth import password_hasher
from sigma_eng.audit_chain import AuditChain


def run(output, image=IMAGE, install=False):
    output = Path(output).absolute()
    output.mkdir(parents=True, exist_ok=False)
    os.chmod(output, 0o700)
    suffix = secrets.token_hex(6)
    names = ["sigma-recovery-source-"+suffix, "sigma-recovery-target-"+suffix]
    volume = "sigma-recovery-data-"+suffix
    password = secrets.token_urlsafe(32)
    audit_key = secrets.token_hex(32)
    credentials = output/"postgres.env"
    credentials.write_text("POSTGRES_USER=sigma_test\nPOSTGRES_DB=sigma_test\nPOSTGRES_PASSWORD="+password+"\n")
    os.chmod(credentials, 0o600)
    # Fora do bundle; não publicar em artifact nem enviar no mesmo canal do backup.
    secret_file = output/"audit-key.txt"
    secret_file.write_text(audit_key); os.chmod(secret_file, 0o600)
    previous = os.environ.get("SIGMA_AUDIT_KEY")
    os.environ["SIGMA_AUDIT_KEY"] = audit_key
    report = {"status": "running", "scope": "dois contêineres no mesmo host; não segunda máquina",
              "image": image, "checks": []}
    service = None
    engine = None

    def check(name, condition):
        report["checks"].append({"name": name, "passed": bool(condition)})
        print(("PASS " if condition else "FAIL ")+name, flush=True)
        if not condition: raise RuntimeError(name)

    def command(args):
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=180)

    def start(name, persistent=False):
        args=["docker", "run", "--detach", "--name", name, "--label", "sigmati.test=recovery",
              "--env-file", str(credentials), "--publish", "127.0.0.1::5432"]
        if persistent: args += ["--volume", volume+":/var/lib/postgresql/data"]
        command(args+[image])
        for _ in range(100):
            ready=subprocess.run(["docker","exec",name,"pg_isready","-h","127.0.0.1","-U","sigma_test","-d","sigma_test"],capture_output=True)
            if ready.returncode==0:
                try:
                    sql(name,"SELECT 1;")
                    return
                except RuntimeError: pass
            time.sleep(.2)
        raise RuntimeError("PostgreSQL não iniciou")

    def url(name):
        port=subprocess.check_output(["docker","port",name,"5432/tcp"],text=True).strip().rsplit(":",1)[1]
        return f"postgresql+psycopg://sigma_test:{password}@127.0.0.1:{port}/sigma_test"

    def rejects(name, operation):
        try: operation()
        except (ValueError, RuntimeError): check(name, True)
        else: check(name, False)

    try:
        start(names[0]); start(names[1], True)
        source=url(names[0])
        audit_path=output/"source-audit.jsonl"
        AuditChain(audit_path, chave=audit_key.encode()).registrar("smoke.synthetic","fixture.seeded","synthetic")
        env=dict(os.environ, SIGMA_DATABASE_URL=source, SIGMA_COLLECTION_ENABLED="1", SIGMA_COLLECTION_SEED="0",
                 SIGMA_PROBE_NETS="127.0.0.0/8", SIGMA_JWT_SECRET=secrets.token_hex(32),
                 OPENROUTER_API_KEY="fake-smoke-only",SIGMA_LLM_MODEL="test/model",
                 SIGMA_CORS_ORIGINS="http://localhost:5173", PYTHON_DOTENV_DISABLED="1",
                 SIGMA_AUDIT_PATH=str(audit_path))
        migration=subprocess.run(["bash","scripts/install.sh"] if install else [sys.executable,"-m","alembic","upgrade","head"],cwd=ROOT,env=env,capture_output=True)
        check("migrações na origem", migration.returncode==0)
        engine=open_database(source)
        PostgresIdentityStore(engine).save_user("smoke.manager", password_hasher.hash(password), "gestor_ti")
        service=TCPService()
        with api_server(env,output/"api-source.log") as base:
            status,login=request(base,"POST","/api/auth/login",{"username":"smoke.manager","password":password})
            check("login real",status==200)
            token=login["access_token"]
            with_client=SSEClient(base,token)
            try:
                status,target=request(base,"POST","/api/eng/alvos",{"nome":"smoke.synthetic","host":"127.0.0.1",
                    "porta":service.port,"intervalo_s":.1,"timeout_s":.3},token)
                check("alvo real cadastrado",status==200)
                from persistence.operational import PostgresOperationalStore
                store=PostgresOperationalStore(engine)
                wait_until(lambda: any(row["sucesso"] for row in store.measurements(target["id"])))
                started=time.perf_counter(); service.stop(); service=None
                received,_,event=with_client.wait(lambda _,data:data.get("acao")=="incident.created" and data.get("alvo_id")==target["id"])
                report["alert_seconds"]=round(received-started,4)
                check("falha real chega ao cliente SSE até5s",received-started<=5)
                incident=event["incidente_id"]
                check("cadeia íntegra via API",request(base,"GET","/api/eng/auditoria/verificar",token=token)[1]["integra"])
                check("aprovação persistida",request(base,"POST","/api/eng/aprovacoes",{"acao":"smoke.synthetic"},token)[0]==200)
                check("SLO persistido",request(base,"POST",f"/api/eng/alvos/{target['id']}/slo",{"alvo_pct":99.9,"janela_dias":30},token)[0]==200)
            finally: with_client.close()
        engine.dispose(); engine=None
        # API já encerrada: nenhuma coleta entre dump, auditoria e inventário.
        bundle=output/"bundle"
        manifest=backup(names[0],audit_path,bundle,quiesced=True)
        check("dump e manifesto autenticados",verify(bundle)==manifest)
        check("backup inclui incidentes e identidades",manifest["tables"]["incidentes"]["rows"]>0 and manifest["tables"]["usuarios"]["rows"]>0)
        empty=fingerprint(names[1])
        wrong=os.environ["SIGMA_AUDIT_KEY"]; os.environ["SIGMA_AUDIT_KEY"]="x"*64
        rejects("chave errada recusada",lambda:restore(names[1],bundle,output/"wrong.jsonl",quiesced=True))
        os.environ["SIGMA_AUDIT_KEY"]=wrong
        dump=bundle/"database.dump"
        with dump.open("ab") as stream:stream.write(b"tampered")
        rejects("dump alterado recusado antes do banco",lambda:restore(names[1],bundle,output/"tampered.jsonl",quiesced=True))
        with dump.open("r+b") as stream:stream.truncate(dump.stat().st_size-len(b"tampered"))
        check("destino intacto após recusas",fingerprint(names[1])==empty)
        # Arquivo inválido porém autenticado: pg_restore deve falhar sem relações parciais.
        original_dump=dump.read_bytes()
        manifest_file=bundle/"manifest.json"
        original_manifest=manifest_file.read_bytes()
        dump.write_bytes(b"not-a-postgres-archive")
        signed=json.loads(original_manifest)
        signed["manifest"]["files"]["database.dump"]=digest(dump)
        signed["hmac_sha256"]=hmac.new(audit_key.encode(),canonical(signed["manifest"]),hashlib.sha256).hexdigest()
        manifest_file.write_bytes(canonical(signed))
        rejects("archive inválido falha sem publicar trilha",lambda:restore(names[1],bundle,output/"invalid.jsonl",quiesced=True))
        check("falha de pg_restore preserva banco vazio",fingerprint(names[1])==empty and not (output/"invalid.jsonl").exists())
        dump.write_bytes(original_dump);manifest_file.write_bytes(original_manifest)
        restored_audit=output/"restored-audit.jsonl"
        restore(names[1],bundle,restored_audit,quiesced=True)
        check("todas as tabelas e linhas reproduzidas",fingerprint(names[1])==manifest["tables"])
        check("auditoria restaurada íntegra",AuditChain(restored_audit,chave=audit_key.encode()).verificar()[0])
        rejects("banco ocupado recusado",lambda:restore(names[1],bundle,output/"occupied.jsonl",quiesced=True))
        baseline=fingerprint(names[1])
        command(["docker","rm","--force",names[1]])
        start(names[1],True)
        check("recriar contêiner preserva todos os registros",fingerprint(names[1])==baseline)
        env.update(SIGMA_DATABASE_URL=url(names[1]),SIGMA_COLLECTION_ENABLED="0",SIGMA_AUDIT_PATH=str(restored_audit))
        with api_server(env,output/"api-restored.log") as base:
            status,login=request(base,"POST","/api/auth/login",{"username":"smoke.manager","password":password})
            check("identidade restaurada permite login",status==200)
            token=login["access_token"]
            rows=request(base,"GET","/api/eng/incidentes",token=token)[1]["incidentes"]
            check("incidente original disponível na API restaurada",any(row["id"]==incident for row in rows))
            check("API restaurada atesta trilha íntegra",request(base,"GET","/api/eng/auditoria/verificar",token=token)[1]["integra"])
            previous_id=int(sql(names[1],"SELECT coalesce(max(id),0) FROM eventos_operacionais;"))
            check("escrita nova funciona após restore",request(base,"POST","/api/eng/aprovacoes",{"acao":"smoke.after-restore"},token)[0]==200)
            check("sequência de eventos avança sem colisão",int(sql(names[1],"SELECT max(id) FROM eventos_operacionais;"))>previous_id)
        report.update(status="passed",tables=len(manifest["tables"]),audit_entries=manifest["audit_entries"],
                      second_machine="pendente; pacote e chave separada preparados")
        return report
    except BaseException:
        report["status"]="failed"
        raise
    finally:
        if service:service.stop()
        if engine is not None:engine.dispose()
        for name in names:
            subprocess.run(["docker","rm","--force","--volumes",name],capture_output=True)
        subprocess.run(["docker","volume","rm",volume],capture_output=True)
        credentials.unlink(missing_ok=True)
        if previous is None:os.environ.pop("SIGMA_AUDIT_KEY",None)
        else:os.environ["SIGMA_AUDIT_KEY"]=previous
        (output/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--image",default=IMAGE)
    parser.add_argument("--install",action="store_true",help="Validar install.sh no Linux antes do smoke")
    args=parser.parse_args()
    try:run(args.output,args.image,args.install)
    except Exception:
        print("Smoke falhou; confira os checks de report.json. Nenhum segredo publicado.",file=sys.stderr)
        return 1
    return 0


if __name__=="__main__":raise SystemExit(main())
