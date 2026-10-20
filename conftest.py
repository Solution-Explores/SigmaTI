"""Credenciais temporárias compartilhadas pelos testes de API e engenharia."""
import json
import secrets

import pytest


@pytest.fixture(autouse=True)
def temporary_identity(monkeypatch, tmp_path):
    import auth
    monkeypatch.delenv("SIGMA_DATABASE_URL", raising=False)
    password = secrets.token_urlsafe(24)
    secret = secrets.token_hex(32)
    users = [
        {"username": nome, "papel": papel, "senha_hash": auth.hash_senha(password)}
        for nome, papel in (("suporte.n1", "suporte_n1"), ("analista.redes", "analista_redes"),
                            ("gestor.ti", "gestor_ti"), ("k08-engenharia", "gestor_ti"))
    ]
    path = tmp_path / "users.json"
    path.write_text(json.dumps(users), encoding="utf-8")
    monkeypatch.setenv("SIGMA_USERS_FILE", str(path))
    monkeypatch.setenv("SIGMA_JWT_SECRET", secret)
    monkeypatch.setenv("SIGMA_AUDIT_PATH", str(tmp_path / "audit.jsonl"))
    auth.configure_auth(secret)
    auth.rate_limiter._tentativas.clear()
    yield password
    with auth._session_lock:
        auth._sessions.clear()


@pytest.fixture
def legacy_identity():
    """Override explícito só para testes isolados anteriores à autenticação."""
    from auth import Usuario, obter_usuario_atual

    def apply(module):
        module.app.dependency_overrides[obter_usuario_atual] = lambda: Usuario(
            username="unit-test", senha_hash="", papel="gestor_ti",
        )
    return apply
