"""Fixtures de API: identidades temporárias, PostgreSQL descartável e clientes isolados."""

import os
import sys
import pytest
import auth
from alembic import command
from alembic.config import Config
from persistence.database import open_database
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
    monkeypatch.setenv("SIGMA_DATABASE_URL", "")
    auth.configure_auth(auth.JWT_SECRET)


@pytest.fixture
def pg_client(pg, monkeypatch):
    import importlib
    from fastapi.testclient import TestClient
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-only")
    monkeypatch.setenv("SIGMA_LLM_MODEL", "test/model")
    monkeypatch.setenv("SIGMA_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    previous = sys.modules.pop("main", None)
    try:
        module = importlib.import_module("main")
        with TestClient(module.app) as client:
            yield client
    finally:
        sys.modules.pop("main", None)
        if previous is not None:
            sys.modules["main"] = previous
