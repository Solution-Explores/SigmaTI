"""Valida navegador→API→PostgreSQL→SSE em schema fictício descartável."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import uuid

from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url

ROOT=Path(__file__).resolve().parents[1]


def run(database_url):
    schema="sigma_panel_"+uuid.uuid4().hex
    engine=create_engine(database_url,hide_parameters=True)
    with engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA {schema}"))
    try:
        url=make_url(database_url).update_query_dict({"options":"-csearch_path="+schema}).render_as_string(hide_password=False)
        env=dict(os.environ,SIGMA_BROWSER_DATABASE_URL=url,SIGMA_DATABASE_URL=url,
                 SIGMA_BROWSER_PASSWORD=secrets.token_urlsafe(24),PYTHON_DOTENV_DISABLED="1")
        migration=subprocess.run([sys.executable,"-m","alembic","upgrade","head"],cwd=ROOT,env=env,capture_output=True)
        if migration.returncode: raise RuntimeError("Migração do schema de navegador falhou.")
        npm="npm.cmd" if os.name=="nt" else "npm"
        result=subprocess.run([npm,"run","test:e2e:operational"],cwd=ROOT/"sigma-frontend",env=env,timeout=240)
        report={"exit_code":result.returncode,"database":"schema isolado PostgreSQL",
                "provider":"simulado","browser":os.getenv("SIGMA_BROWSER_CHANNEL","chromium"),"scope":"navegador, API real, SSE e decisões persistentes"}
        output=ROOT/"test-results/panel-run.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(report,indent=2),encoding="utf-8")
        if result.returncode: raise RuntimeError("Ensaio do painel falhou; conferir evidências locais.")
        return report
    finally:
        with engine.begin() as connection:
            connection.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        engine.dispose()


if __name__=="__main__":
    url=os.getenv("SIGMA_TEST_DATABASE_URL")
    if not url: raise SystemExit("Configure SIGMA_TEST_DATABASE_URL para banco descartável.")
    run(url)
