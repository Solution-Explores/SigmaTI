"""Configuração global de fixtures do pytest para o SIGMA."""

import os
import pytest


@pytest.fixture(autouse=True)
def default_auth_mode(monkeypatch, request):
    """Garante isolamento e compatibilidade nos testes unitários e de integração.

    - Para testes dedicados de sessão/autenticação (test_session_auth), garante
      que a autenticação esteja ativada (SIGMA_AUTH_ENFORCED="1").
    - Para testes legados de erros públicos e provedores IA (K05/K06), mantém o
      comportamento bypass caso não tenham configurado explicitamente a variável,
      preservando suas asserções sem necessidade de cabeçalhos de autorização.
    """
    if "test_session_auth" in request.node.nodeid:
        monkeypatch.setenv("SIGMA_AUTH_ENFORCED", "1")
    elif "SIGMA_AUTH_ENFORCED" not in os.environ:
        monkeypatch.setenv("SIGMA_AUTH_ENFORCED", "0")
