import importlib
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import AsyncMock, Mock

import pytest
import httpx2 as httpx
from fastapi.testclient import TestClient

import config


ROOT = Path(__file__).resolve().parents[2]
VALUES = {
    "OPENROUTER_API_KEY": "fake-key-only-for-tests",
    "SIGMA_LLM_MODEL": "test-provider/test-model",
    "SIGMA_CORS_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
}


@pytest.fixture
def environment(monkeypatch, tmp_path):
    for name, value in VALUES.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("PYTHON_DOTENV_DISABLED", raising=False)
    return tmp_path / ".env"


def test_load_valid_settings_and_hide_key(environment):
    settings = config.load_settings(environment)
    assert settings.openrouter_api_key == VALUES["OPENROUTER_API_KEY"]
    assert settings.llm_model == VALUES["SIGMA_LLM_MODEL"]
    assert settings.cors_origins == ("http://localhost:5173", "http://127.0.0.1:5173")
    assert VALUES["OPENROUTER_API_KEY"] not in repr(settings)


@pytest.mark.parametrize(
    "key", ["fake-key\nHeader: value", "fake-key\rHeader: value", "fake\tkey", "fake-☃"]
)
def test_invalid_api_key_fails_before_http_can_disclose_it(environment, monkeypatch, key):
    monkeypatch.setenv("OPENROUTER_API_KEY", key)
    with pytest.raises(config.ConfigurationError) as error:
        config.load_settings(environment)
    assert "OPENROUTER_API_KEY" in str(error.value)
    assert "fake" not in str(error.value)


@pytest.mark.parametrize("name", VALUES)
@pytest.mark.parametrize("value", [None, "", " \t "])
def test_required_values_fail_without_disclosing_values(environment, monkeypatch, name, value):
    if value is None:
        monkeypatch.delenv(name)
    else:
        monkeypatch.setenv(name, value)
    with pytest.raises(config.ConfigurationError) as error:
        config.load_settings(environment)
    assert name in str(error.value)
    assert VALUES["OPENROUTER_API_KEY"] not in str(error.value)


def test_dotenv_is_used_when_process_values_are_absent(environment, monkeypatch):
    for name in VALUES:
        monkeypatch.delenv(name)
    # Windows PowerShell 5.1 costuma gravar arquivos UTF-8 com BOM.
    environment.write_text(
        "\n".join(f"{name}={value}" for name, value in VALUES.items()), encoding="utf-8-sig"
    )
    settings = config.load_settings(environment)
    assert settings.openrouter_api_key == VALUES["OPENROUTER_API_KEY"]
    assert settings.llm_model == VALUES["SIGMA_LLM_MODEL"]


def test_process_values_override_dotenv(environment):
    environment.write_text(
        "OPENROUTER_API_KEY=file-only-fake-key\n"
        "SIGMA_LLM_MODEL=file/model\n"
        "SIGMA_CORS_ORIGINS=https://file.example\n",
        encoding="utf-8",
    )
    settings = config.load_settings(environment)
    assert settings.openrouter_api_key == VALUES["OPENROUTER_API_KEY"]
    assert settings.llm_model == VALUES["SIGMA_LLM_MODEL"]
    assert settings.cors_origins[0] == "http://localhost:5173"


@pytest.mark.parametrize("name", VALUES)
def test_empty_process_value_is_not_replaced_by_dotenv(environment, monkeypatch, name):
    environment.write_text(f"{name}={VALUES[name]}\n", encoding="utf-8")
    monkeypatch.setenv(name, "")
    with pytest.raises(config.ConfigurationError, match=name):
        config.load_settings(environment)


def test_default_dotenv_path_is_project_root_not_cwd(environment, monkeypatch, tmp_path):
    project = tmp_path / "project"
    other = tmp_path / "other"
    project.mkdir()
    other.mkdir()
    (project / ".env").write_text(
        "\n".join(f"{name}={value}" for name, value in VALUES.items()), encoding="utf-8"
    )
    (other / ".env").write_text("SIGMA_LLM_MODEL=wrong/model\n", encoding="utf-8")
    for name in VALUES:
        monkeypatch.delenv(name)
    monkeypatch.setattr(config, "__file__", str(project / "backend" / "config.py"))
    monkeypatch.chdir(other)
    assert config.load_settings().llm_model == VALUES["SIGMA_LLM_MODEL"]


def test_dotenv_values_are_literal(environment, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    environment.write_text("OPENROUTER_API_KEY=fake-${SIGMA_LLM_MODEL}\n", encoding="utf-8")
    assert config.load_settings(environment).openrouter_api_key == "fake-${SIGMA_LLM_MODEL}"


@pytest.mark.parametrize(
    "origins",
    [
        "*", "null", "https://*.example.org", "localhost:5173", "ftp://panel.example",
        "https://panel.example/", "https://panel.example/path", "https://user:secret@panel.example",
        "https://panel.example?key=do-not-print", "https://panel.example#fragment", "https://",
        "http://localhost:", "http://localhost:65536", "http://localhost:0",
        "http://bad..example", "http://-bad.example", "https://panel.example\\path",
        "https://panel.example,", ",https://panel.example", "https://panel.example,,http://localhost",
        "https://panel. example", "https://panel.example\n.evil.example", "http://[invalid]",
    ],
)
def test_invalid_origins_are_rejected(environment, monkeypatch, origins):
    monkeypatch.setenv("SIGMA_CORS_ORIGINS", origins)
    with pytest.raises(config.ConfigurationError) as error:
        config.load_settings(environment)
    assert "SIGMA_CORS_ORIGINS" in str(error.value)
    assert origins not in str(error.value)
    assert "secret" not in str(error.value)
    assert "do-not-print" not in str(error.value)


def test_explicit_origins_allow_whitespace_ports_https_and_ipv6(environment, monkeypatch):
    monkeypatch.setenv(
        "SIGMA_CORS_ORIGINS",
        " https://panel.example , http://127.0.0.1:5173 , http://[::1]:5173 ",
    )
    assert config.load_settings(environment).cors_origins == (
        "https://panel.example", "http://127.0.0.1:5173", "http://[::1]:5173"
    )


@pytest.mark.parametrize(
    ("name", "bad_value"),
    [(None, None)] + [(name, value) for name in VALUES for value in (None, "", " ")]
    + [("SIGMA_CORS_ORIGINS", "*")],
)
def test_actual_app_import_requires_configuration(name, bad_value):
    env = os.environ.copy()
    env.update(VALUES)
    env["PYTHON_DOTENV_DISABLED"] = "1"
    if name:
        if bad_value is None:
            env.pop(name)
        else:
            env[name] = bad_value
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'backend'); import main\nprint('app-ready')"],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=15,
    )
    output = result.stdout + result.stderr
    assert VALUES["OPENROUTER_API_KEY"] not in output
    if name:
        assert result.returncode != 0
        assert name in output
        assert "app-ready" not in output
    else:
        assert result.returncode == 0, output
        assert "app-ready" in output


@pytest.fixture
def api(environment, monkeypatch, legacy_identity):
    settings = config.load_settings(environment)
    monkeypatch.setattr(config, "load_settings", lambda: settings)
    previous = sys.modules.pop("main", None)
    module = importlib.import_module("main")
    legacy_identity(module)
    provider = AsyncMock(side_effect=AssertionError("Unexpected external request"))
    fake_client = Mock(post=provider)
    module.app.dependency_overrides[module.get_provider_client] = lambda: fake_client
    try:
        with TestClient(module.app) as client:
            yield client, provider
    finally:
        sys.modules.pop("main", None)
        if previous is not None:
            sys.modules["main"] = previous


@pytest.mark.parametrize("origin", VALUES["SIGMA_CORS_ORIGINS"].split(","))
def test_allowed_browser_preflight(api, origin):
    client, provider = api
    response = client.options(
        "/api/alertas",
        headers={"Origin": origin, "Access-Control-Request-Method": "POST",
                 "Access-Control-Request-Headers": "content-type"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    provider.assert_not_called()


def test_disallowed_browser_preflight(api):
    client, provider = api
    response = client.options(
        "/api/alertas",
        headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
    provider.assert_not_called()


def test_alert_uses_configured_provider_and_preserves_response_contract(api):
    client, provider = api
    provider.side_effect = None
    provider.return_value = httpx.Response(
        200, request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
        json={"choices": [{"message": {"content": "Diagnóstico simulado"}}]},
    )
    response = client.post(
        "/api/alertas", headers={"Origin": "http://localhost:5173"},
        json={"equipamento": "Switch de teste", "ip_origem": "192.0.2.10",
              "descricao_erro": "Falha de rede no IP 192.0.2.10"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.json() == {
        "status": "Incidente Registrado",
        "dados_enviados_nuvem": "Equipamento: [SWITCH_REDE] | Erro: Falha de rede no IP 192.0.2.0/24. Forneça um diagnóstico de rede curto e direto.",
        "diagnostico_ia": "Diagnóstico simulado",
    }
    provider.assert_awaited_once()
    args, kwargs = provider.call_args
    assert args == ("https://openrouter.ai/api/v1/chat/completions",)
    assert kwargs["headers"]["Authorization"] == f"Bearer {VALUES['OPENROUTER_API_KEY']}"
    assert kwargs["json"]["model"] == VALUES["SIGMA_LLM_MODEL"]
    assert VALUES["OPENROUTER_API_KEY"] not in response.text


def test_example_has_no_api_key_or_model_default():
    from dotenv import dotenv_values

    values = dotenv_values(ROOT / ".env.example")
    assert values["OPENROUTER_API_KEY"] == ""
    assert values["SIGMA_LLM_MODEL"] == ""
    assert values["SIGMA_CORS_ORIGINS"] == VALUES["SIGMA_CORS_ORIGINS"]
