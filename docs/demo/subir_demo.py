"""Sobe a API da demonstração com dados fictícios em schema PostgreSQL isolado.

Uso (na raiz do worktree da develop, com a .venv ativa):
    $env:SIGMA_TEST_DATABASE_URL = 'postgresql+psycopg://usuario:senha@127.0.0.1:5432/sigmadb'
    python <caminho>\\docs\\demo\\subir_demo.py

Reaproveita scripts/serve_browser_acceptance.py, o mesmo servidor do aceite de
navegador: quatro usuários, três alvos, SLO com 25 h de medições, uma aprovação
pendente e um registro de auditoria. API em http://127.0.0.1:18000.
Ctrl+C encerra a API e remove o schema.
"""
import os
import secrets
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(os.environ.get("SIGMA_REPO", Path.cwd())).resolve()


def main():
    if not (ROOT / "scripts" / "serve_browser_acceptance.py").exists():
        sys.exit(f"Rode na raiz do repositório SigmaTI (ou defina SIGMA_REPO). Atual: {ROOT}")
    database_url = os.environ["SIGMA_TEST_DATABASE_URL"]
    schema = "sigma_panel_" + secrets.token_hex(16)
    password = os.environ.get("SIGMA_BROWSER_PASSWORD") or secrets.token_urlsafe(12)
    engine = create_engine(database_url, hide_parameters=True)
    with engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA {schema}"))
    try:
        url = make_url(database_url).update_query_dict(
            {"options": "-csearch_path=" + schema}).render_as_string(hide_password=False)
        env = dict(os.environ, SIGMA_BROWSER_DATABASE_URL=url, SIGMA_DATABASE_URL=url,
                   SIGMA_BROWSER_PASSWORD=password, PYTHON_DOTENV_DISABLED="1")
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                       cwd=ROOT, env=env, check=True)
        print(f"\nSchema: {schema}")
        print("Usuários: browser.demo (suporte_n1), browser.analyst e browser.reviewer"
              " (analista_redes), browser.manager (gestor_ti)")
        print(f"Senha comum: {password}")
        print("API: http://127.0.0.1:18000  |  Ctrl+C encerra\n")
        try:
            subprocess.run([sys.executable, "scripts/serve_browser_acceptance.py"], cwd=ROOT, env=env)
        except KeyboardInterrupt:
            pass
    finally:
        with engine.begin() as connection:
            connection.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        engine.dispose()


if __name__ == "__main__":
    main()
