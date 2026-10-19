"""Regressões dos achados K11 e revisão independente da métrica E6."""
import importlib
import json
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

import auth
import sanitizer
from scripts import executar_experimento_e6 as e6


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-test-only")
    monkeypatch.setenv("SIGMA_LLM_MODEL", "test/model")
    monkeypatch.setenv("SIGMA_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    previous = sys.modules.pop("main", None)
    module = importlib.import_module("main")
    try:
        with TestClient(module.app) as c:
            yield c
    finally:
        sys.modules.pop("main", None)
        if previous:
            sys.modules["main"] = previous


def login(client, password):
    r = client.post("/api/auth/login", json={"username": "suporte.n1", "password": password})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_logout_revokes_only_its_session(client, temporary_identity):
    first = login(client, temporary_identity)
    second = login(client, temporary_identity)
    assert client.get("/api/auth/me", headers=first).status_code == 200
    assert client.post("/api/auth/logout", headers=first).status_code == 200
    assert client.get("/api/status", headers=first).status_code == 401
    assert client.post("/api/auth/logout", headers=first).status_code == 401
    assert client.get("/api/status", headers=second).status_code == 200


def test_restart_invalidates_sessions(client, temporary_identity):
    headers = login(client, temporary_identity)
    auth.configure_auth(auth.JWT_SECRET)
    assert client.get("/api/status", headers=headers).status_code == 401


def test_deactivated_user_and_changed_role_are_rejected(client, temporary_identity):
    headers = login(client, temporary_identity)
    user = auth.usuario_repo.obter_por_username("suporte.n1")
    user.ativo = False
    assert client.get("/api/status", headers=headers).status_code == 401
    user.ativo = True
    user.papel = "gestor_ti"
    assert client.get("/api/status", headers=headers).status_code == 401


def test_environment_cannot_disable_auth(client, monkeypatch):
    monkeypatch.setenv("SIGMA_AUTH_ENFORCED", "0")
    assert client.get("/api/status").status_code == 401


def test_jwt_secret_from_dotenv_is_loaded_before_auth(monkeypatch, tmp_path):
    import config
    secret = __import__('secrets').token_hex(32)
    path = tmp_path / '.env'
    path.write_text('SIGMA_JWT_SECRET=' + secret + '\nSIGMA_JWT_EXPIRATION_SECONDS=60\n', encoding='utf-8')
    monkeypatch.delenv('SIGMA_JWT_SECRET')
    monkeypatch.delenv('SIGMA_JWT_EXPIRATION_SECONDS', raising=False)
    monkeypatch.delenv('PYTHON_DOTENV_DISABLED', raising=False)
    monkeypatch.setenv('OPENROUTER_API_KEY', 'fake-only')
    monkeypatch.setenv('SIGMA_LLM_MODEL', 'test/model')
    monkeypatch.setenv('SIGMA_CORS_ORIGINS', 'http://localhost:5173')
    settings = config.load_settings(path)
    auth.configure_auth(settings.jwt_secret)
    assert auth.JWT_SECRET == secret
    assert auth.JWT_EXPIRATION_SECONDS == 60


@pytest.mark.parametrize('body', [[], [{"username": "demo", "senha_hash": "plaintext", "papel": "gestor_ti"}]])
def test_invalid_user_file_fails_closed(tmp_path, body):
    from config import ConfigurationError
    path = tmp_path / 'invalid.json'
    path.write_text(json.dumps(body), encoding='utf-8')
    with pytest.raises(ConfigurationError, match='SIGMA_USERS_FILE'):
        auth.UsuarioRepository().carregar(str(path))


@pytest.mark.parametrize("method,path", [("GET", "/api/auth/me"), ("POST", "/api/alertas")])
def test_authenticated_preflight(client, method, path):
    r = client.options(path, headers={"Origin": "http://localhost:5173",
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": "authorization,content-type"})
    assert r.status_code == 200
    assert "*" not in r.headers["access-control-allow-headers"]


def test_e6_detects_partial_leak(monkeypatch):
    corpus = [{"id": "partial", "tipo": "positivo", "entrada": "email e CPF", "identificadores": [
        {"classe": "email", "valor": "email", "substituto": "[EMAIL_REMOVIDO]"},
        {"classe": "cpf", "valor": "52998224725", "substituto": "[CPF_REMOVIDO]"}]}]
    monkeypatch.setattr(e6, "sanitizar_texto", lambda _: sanitizer.ResultadoSanitizacao(
        sucesso=True, texto_sanitizado="[EMAIL_REMOVIDO] 52998224725", identificadores_removidos=["email"]))
    m = e6.executar_experimento(corpus)
    assert m["recall"] == 50
    assert m["vazados"] == 1
    assert not m["aprovado"]


def test_safe_block_is_not_counted_as_transformation(monkeypatch):
    corpus = [{"id": "blocked", "tipo": "positivo", "entrada": "CPF", "identificadores": [
        {"classe": "cpf", "valor": "CPF", "substituto": "[CPF_REMOVIDO]"}]}]
    monkeypatch.setattr(e6, "sanitizar_texto", lambda _: sanitizer.ResultadoSanitizacao(False, ""))
    m = e6.executar_experimento(corpus)
    assert m["bloqueados"] == 1 and m["vazados"] == 0 and m["recall"] == 0
    assert not m["aprovado"]


def test_annotated_corpus_meets_threshold():
    corpus = e6.carregar_corpus(Path(__file__).parent / "data/corpus_sintetico_pii.json")
    assert e6.executar_experimento(corpus)["aprovado"]


@pytest.mark.parametrize("pattern,value", [
    ("RE_EMAIL", "teste@example.invalid"), ("RE_CPF_LIVRE", "52998224725"),
    ("RE_IPV6", "2001:db8::abcd"), ("RE_HOSTNAME_LOG", "srv-teste.local"),
    ("RE_NOMES_CONTEXTUAIS", "Dra. Julia Silva"),
])
def test_residual_detector_blocks_broken_transformer(monkeypatch, pattern, value):
    original = getattr(sanitizer, pattern)
    class BrokenTransform:
        def search(self, text): return original.search(text)
        def sub(self, *args): return args[-1]
        def finditer(self, text): return original.finditer(text)
    monkeypatch.setattr(sanitizer, pattern, BrokenTransform())
    assert not sanitizer.sanitizar_texto(value).sucesso


def test_privacy_audit_never_contains_raw_values(monkeypatch, caplog):
    raw = "teste@example.invalid"
    monkeypatch.setattr(sanitizer, "sanitizar_texto", lambda _: sanitizer.ResultadoSanitizacao(
        False, raw, residuos=[raw], motivo_bloqueio=raw))
    with pytest.raises(sanitizer.SanitizationError):
        sanitizer.anonimizar_dados(raw)
    audit = Path(__import__('os').environ["SIGMA_AUDIT_PATH"]).read_text(encoding="utf-8")
    assert raw not in caplog.text + audit
    assert json.loads(audit.splitlines()[-1])["acao"] == "privacy.sanitization_failed"
