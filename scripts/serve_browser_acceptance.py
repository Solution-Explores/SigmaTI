"""API de teste local para Playwright: provedor simulado, credenciais efêmeras."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from auth import UsuarioRepository
from scripts.validate_api_acceptance import serve


def main():
    password = os.environ["SIGMA_BROWSER_PASSWORD"]
    directory = ROOT / "test-results" / ("browser-" + secrets.token_hex(6))
    directory.mkdir(parents=True)
    repo = UsuarioRepository()
    repo.adicionar_usuario("browser.demo", password, "suporte_n1")
    users = directory / "users.json"
    users.write_text(json.dumps([asdict(u) for u in repo._usuarios.values()]), encoding="utf-8")
    os.environ.update({"OPENROUTER_API_KEY": "fake-browser-only", "SIGMA_LLM_MODEL": "test/model",
        "SIGMA_CORS_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
        "SIGMA_JWT_SECRET": secrets.token_hex(32), "SIGMA_USERS_FILE": str(users),
        "SIGMA_AUDIT_KEY": secrets.token_hex(32), "SIGMA_AUDIT_PATH": str(directory / "audit.jsonl"),
        "PYTHON_DOTENV_DISABLED": "1"})
    try:
        serve(ROOT, 18000, directory / "events.jsonl")
    finally:
        users.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
