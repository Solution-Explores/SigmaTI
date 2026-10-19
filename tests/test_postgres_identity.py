"""Integração real; exige banco descartável criado pelo runner ou pelo CI."""
import os
import subprocess
import sys
import uuid

import pytest
from alembic import command
from alembic.config import Config

import auth
from persistence.database import open_database, PersistenceUnavailable
from persistence.identity import PostgresIdentityStore


@pytest.fixture
def pg(monkeypatch):
    url = os.getenv("SIGMA_TEST_DATABASE_URL")
    if not url:
        pytest.skip("PostgreSQL descartável não solicitado; CI executa este grupo obrigatoriamente.")
    monkeypatch.setenv("SIGMA_DATABASE_URL", url)
    command.upgrade(Config("alembic.ini"), "head")
    engine = open_database(url)
    store = PostgresIdentityStore(engine)
    yield store
    engine.dispose()
    monkeypatch.delenv("SIGMA_DATABASE_URL")
    auth.configure_auth(auth.JWT_SECRET)


def identity(store):
    username = "test-" + uuid.uuid4().hex
    store.save_user(username, auth.password_hasher.hash("synthetic-password"), "analista_redes")
    return username


def test_session_survives_new_process_and_revocation(pg):
    username = identity(pg)
    auth.configure_auth(auth.JWT_SECRET)
    token = auth.criar_token_sessao(username, "analista_redes")
    env = dict(os.environ, SIGMA_JWT_SECRET=auth.JWT_SECRET)
    code = "import os,sys,auth; auth.configure_auth(os.environ['SIGMA_JWT_SECRET']); auth.decodificar_token_sessao(sys.stdin.read()); print('valid')"
    result = subprocess.run([sys.executable, "-c", code], input=token, text=True,
                            capture_output=True, env=env, timeout=20)
    assert result.returncode == 0 and result.stdout.strip() == "valid"
    auth.configure_auth(auth.JWT_SECRET)
    assert auth.decodificar_token_sessao(token)["sub"] == username
    auth.revogar_token(token)
    auth.configure_auth(auth.JWT_SECRET)
    with pytest.raises(auth.TokenError):
        auth.decodificar_token_sessao(token)


@pytest.mark.parametrize("change", ["password", "role", "deactivate", "reactivate"])
def test_identity_change_invalidates_sessions_permanently(pg, change):
    username = identity(pg)
    auth.configure_auth(auth.JWT_SECRET)
    token = auth.criar_token_sessao(username, "analista_redes")
    row = pg.get_user(username)
    if change == "password":
        row["senha_hash"] = auth.password_hasher.hash("new-synthetic-password")
    elif change == "role":
        row["papel"] = "gestor_ti"
    else:
        row["ativo"] = False
    pg.save_user(**row)
    if change == "reactivate":
        row["ativo"] = True
        pg.save_user(**row)
    with pytest.raises(auth.TokenError):
        auth.decodificar_token_sessao(token)


def test_password_rehash_and_concurrent_change(pg):
    username = "legacy-" + uuid.uuid4().hex
    old = auth.hash_senha("synthetic-password")
    pg.save_user(username, old, "suporte_n1")
    auth.configure_auth(auth.JWT_SECRET)
    user = auth.usuario_repo.obter_por_username(username)
    assert auth.verificar_senha("synthetic-password", user.senha_hash)
    upgraded = auth.usuario_repo.atualizar_hash(user, "synthetic-password")
    assert pg.get_user(username)["senha_hash"].startswith("$argon2id$")
    token = auth.criar_token_sessao(username, "suporte_n1", expected_hash=upgraded.senha_hash)
    pg.upgrade_hash(username, upgraded.senha_hash, auth.password_hasher.hash("synthetic-password"))
    assert auth.decodificar_token_sessao(token)
    pg.save_user(username, auth.password_hasher.hash("changed-password"), "suporte_n1")
    with pytest.raises(auth.TokenError):
        auth.criar_token_sessao(username, "suporte_n1", expected_hash=upgraded.senha_hash)


def test_unavailable_database_does_not_fallback(pg, monkeypatch):
    monkeypatch.setenv("SIGMA_DATABASE_URL", "postgresql+psycopg://test:test@127.0.0.1:1/test")
    with pytest.raises(PersistenceUnavailable):
        auth.configure_auth(auth.JWT_SECRET)


def test_import_is_atomic_and_rejects_existing_identity(pg):
    username = identity(pg)
    first = auth.Usuario("import-" + uuid.uuid4().hex, auth.hash_senha("synthetic"), "suporte_n1")
    existing = auth.Usuario(username, auth.hash_senha("synthetic"), "suporte_n1")
    with pytest.raises(ValueError):
        pg.import_users([first, existing])
    assert pg.get_user(first.username) is None


def test_migration_downgrade_upgrade_on_disposable_database(pg):
    from sqlalchemy import inspect
    command.downgrade(Config("alembic.ini"), "base")
    assert "usuarios" not in inspect(pg.engine).get_table_names()
    command.upgrade(Config("alembic.ini"), "head")
    assert {"usuarios", "sessoes"} <= set(inspect(pg.engine).get_table_names())


def test_postgres_login_logout_and_failure_response(pg, monkeypatch):
    import importlib
    from fastapi.testclient import TestClient
    username = identity(pg)
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-only")
    monkeypatch.setenv("SIGMA_LLM_MODEL", "test/model")
    monkeypatch.setenv("SIGMA_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    previous = sys.modules.pop("main", None)
    try:
        module = importlib.import_module("main")
        with TestClient(module.app) as client:
            login = client.post("/api/auth/login", json={"username": username, "password": "synthetic-password"})
            assert login.status_code == 200
            headers = {"Authorization": "Bearer " + login.json()["access_token"]}
            auth.configure_auth(auth.JWT_SECRET)
            assert client.get("/api/auth/me", headers=headers).status_code == 200
            assert client.post("/api/auth/logout", headers=headers).status_code == 200
            assert client.get("/api/auth/me", headers=headers).status_code == 401
            def unavailable(*args):
                raise PersistenceUnavailable("private detail")
            monkeypatch.setattr(auth.usuario_repo.backend, "get_user", unavailable)
            response = client.post("/api/auth/login", json={"username": username, "password": "synthetic-password"})
            assert response.status_code == 503
            assert "private detail" not in response.text
    finally:
        sys.modules.pop("main", None)
        if previous is not None:
            sys.modules["main"] = previous


def test_bootstrap_cli_uses_argon2_and_rejects_duplicate(pg, monkeypatch):
    from scripts import manage_identity
    username = "bootstrap-" + uuid.uuid4().hex
    monkeypatch.setattr(sys, "argv", ["manage_identity", "create", username, "gestor_ti"])
    monkeypatch.setattr(manage_identity.getpass, "getpass", lambda prompt: "synthetic-bootstrap-password")
    manage_identity.main()
    row = pg.get_user(username)
    assert row["senha_hash"].startswith("$argon2id$")
    assert auth.verificar_senha("synthetic-bootstrap-password", row["senha_hash"])
    with pytest.raises(SystemExit) as error:
        manage_identity.main()
    assert error.value.code == 2
    assert pg.get_user(username)["senha_hash"] == row["senha_hash"]


def test_expired_session_and_wrong_password(pg):
    username = identity(pg)
    auth.configure_auth(auth.JWT_SECRET)
    row = pg.get_user(username)
    assert not auth.verificar_senha("wrong-synthetic-password", row["senha_hash"])
    assert pg.get_user(username)["senha_hash"] == row["senha_hash"]
    token = auth.criar_token_sessao(username, "analista_redes", expira_em_segundos=-1)
    with pytest.raises(auth.TokenError):
        auth.decodificar_token_sessao(token)
