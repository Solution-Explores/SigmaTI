"""Regras adicionais da #5: detector residual de nomes (IBGE) e identificadores ampliados."""

import pytest

from sanitizer import SanitizationResidualError, anonimizar_dados, sanitizar_texto


def test_nome_sem_contexto_bloqueia_em_vez_de_substituir():
    resultado = sanitizar_texto("Maria Oliveira (leito 12) não consegue acessar")
    assert resultado.sucesso is False
    assert "nome_sem_contexto_residual" in resultado.residuos


def test_nome_sem_contexto_bloqueia_envio_externo(monkeypatch):
    import sanitizer

    monkeypatch.setattr(sanitizer, "registrar_auditoria_privacidade", lambda **_: None)
    with pytest.raises(SanitizationResidualError):
        anonimizar_dados("Maria Oliveira (leito 12) não consegue acessar")


@pytest.mark.parametrize(
    "texto",
    [
        "Falha de conexão com host 192.168.1.55 e gateway 10.0.4.1",
        "Executando zabbix 6.4.21 e n8n 1.80.0",
        "Perda de pacotes entre sw-core-01 e srv-prontuario.fcecon",
    ],
)
def test_texto_tecnico_sem_pii_nao_e_bloqueado(texto):
    assert sanitizar_texto(texto).sucesso is True


def test_login_nao_vaza_parte_apos_ponto():
    resultado = sanitizar_texto("usuario joao.silva bloqueado no AD")
    assert resultado.sucesso is True
    assert "silva" not in resultado.texto_sanitizado.lower()
